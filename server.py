import sys
import os
import io
import json
import base64
import asyncio
import logging
import webbrowser
from aiohttp import web
from cryptography.fernet import InvalidToken
from PIL import Image

from typing import Callable, Optional

from app_paths import resource
from clipboard_engine import ClipboardEngine, ClipboardItem, file_item_from_paths, pack_files, unpack_files
from p2p_sync import P2PManager
from updater import Updater
from version import __version__

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ClipboardServer")

DEFAULT_PORT = 7890
STATIC_DIR = resource("static")
LOOPBACK = {"127.0.0.1", "::1"}
PEER_ROUTES = {"/api/ping", "/api/sync"}  # the only endpoints reachable from other devices
UPDATE_CHECK_INTERVAL = 6 * 3600


class ClipboardServer:
    def __init__(self, port: int = DEFAULT_PORT, on_show: Optional[Callable[[], None]] = None):
        self.port = port
        self.on_show = on_show
        self.updater = Updater()
        self.app = web.Application(
            client_max_size=64 * 1024 * 1024,  # fits a 25MB file after base64 + Fernet overhead
            middlewares=[self._access_guard],
        )
        self.engine = ClipboardEngine()
        self.p2p = P2PManager(local_http_port=self.port, on_peer_change=self._on_peers_updated)
        self.ws_clients = set()
        self.history = []  # List of ClipboardItem dicts (max 50)
        self._setup_routes()

    def _setup_routes(self):
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/ws", self.handle_ws)
        self.app.router.add_post("/api/ping", self.handle_api_ping)
        self.app.router.add_post("/api/sync", self.handle_api_sync)
        self.app.router.add_post("/api/upload", self.handle_api_upload)
        self.app.router.add_post("/api/shutdown", self.handle_api_shutdown)
        self.app.router.add_get("/api/status", self.handle_api_status)
        self.app.router.add_get("/api/history", self.handle_api_history)
        self.app.router.add_get("/api/pairing", self.handle_api_pairing_get)
        self.app.router.add_post("/api/pairing", self.handle_api_pairing_set)
        self.app.router.add_post("/api/pairing/copy", self.handle_api_pairing_copy)
        self.app.router.add_get("/api/update", self.handle_api_update_status)
        self.app.router.add_post("/api/update/install", self.handle_api_update_install)
        self.app.router.add_post("/api/update/open", self.handle_api_update_open)
        self.app.router.add_post("/api/show", self.handle_api_show)
        self.app.router.add_static("/static/", STATIC_DIR, name="static")

    @web.middleware
    async def _access_guard(self, request: web.Request, handler):
        """Dashboard/API is localhost-only; LAN peers may only reach the sealed peer endpoints.
        The Origin check stops other websites open in the local browser from using the API,
        the Host check stops DNS-rebinding pages from reading it (e.g. the pairing key)."""
        if request.remote not in LOOPBACK:
            if request.path not in PEER_ROUTES:
                raise web.HTTPForbidden()
        else:
            local_hosts = (f"localhost:{self.port}", f"127.0.0.1:{self.port}")
            origin = request.headers.get("Origin")
            if origin and origin not in tuple(f"http://{h}" for h in local_hosts):
                raise web.HTTPForbidden()
            if request.host not in local_hosts:
                raise web.HTTPForbidden()
        return await handler(request)

    async def _read_payload(self, request: web.Request) -> dict:
        """Plain JSON is accepted only from the local dashboard; everything else must be sealed."""
        if request.remote in LOOPBACK and request.content_type == "application/json":
            return await request.json()
        return self.p2p.unseal(await request.read())

    async def handle_index(self, request: web.Request):
        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_path):
            return web.FileResponse(index_path)
        return web.Response(text="Dashboard UI files not found.", status=404)

    async def handle_ws(self, request: web.Request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.ws_clients.add(ws)
        logger.info(f"WebSocket client connected. Total clients: {len(self.ws_clients)}")

        try:
            init_payload = {
                "event": "init",
                "node": {
                    "id": self.p2p.node_id,
                    "name": self.p2p.hostname,
                    "system": self.p2p.system,
                    "port": self.port,
                },
                "peers": self.p2p.get_active_peers_list(),
                "history": self.history[:30],
                "update": self.updater.status(),
            }
            await ws.send_json(init_payload)

            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        if data.get("action") == "push_text":
                            text = data.get("text", "")
                            if text:
                                item = ClipboardItem("text", text, {"source": "dashboard"})
                                await self.process_and_broadcast_item(item, from_remote=False)
                    except Exception as e:
                        logger.error(f"WS message error: {e}")
        finally:
            self.ws_clients.remove(ws)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.ws_clients)}")

        return ws

    async def broadcast_ws(self, event_data: dict):
        if not self.ws_clients:
            return
        dead = []
        for ws in self.ws_clients:
            try:
                await ws.send_json(event_data)
            except Exception:
                dead.append(ws)
        for d in dead:
            self.ws_clients.discard(d)

    def _on_peers_updated(self, peers: list):
        asyncio.create_task(self.broadcast_ws({"event": "peers_updated", "peers": peers}))

    async def process_and_broadcast_item(self, item: ClipboardItem, from_remote: bool = False):
        """Adds to history, writes to local clipboard (if remote), broadcasts to P2P and WebSockets."""
        item_dict = item.to_dict()

        # Deduplicate history: ensure item appears only once at the top
        self.history = [h for h in self.history if h.get("hash") != item.hash]
        self.history.insert(0, item_dict)
        if len(self.history) > 50:
            self.history.pop()

        if from_remote:
            logger.info(f"Writing incoming {item.item_type} to local clipboard...")
            await asyncio.to_thread(self.engine.write_local_clipboard, item)
        elif item.metadata.get("too_large"):
            logger.warning(f"Copied files exceed the sync limit ({item.metadata.get('size_bytes', 0)} bytes), not sending.")
        else:
            logger.info(f"Broadcasting local {item.item_type} to LAN peers...")
            payload = item_dict
            if item.item_type == "file":
                # Contents ride outside metadata so they never land in history or WebSocket events
                payload = {**item_dict, "packed": await asyncio.to_thread(pack_files, item.data.splitlines())}
            asyncio.create_task(self.p2p.broadcast_to_peers(payload))

        # Notify local UI Dashboard
        await self.broadcast_ws({"event": "clipboard_item", "item": item_dict, "from_remote": from_remote})

    async def handle_api_ping(self, request: web.Request):
        """Direct unicast handshake from a remote peer."""
        try:
            data = self.p2p.unseal(await request.read())
            node_id = data.get("id")
            name = data.get("name", "Unknown")
            port = data.get("port", 7890)
            system = data.get("system", "unknown")
            peer_ip = request.remote

            if node_id and node_id != self.p2p.node_id:
                self.p2p.handle_peer_beacon(node_id, name, peer_ip, port, system)
                return web.json_response({
                    "status": "ok",
                    "id": self.p2p.node_id,
                    "name": self.p2p.hostname,
                    "system": self.p2p.system,
                    "port": self.port,
                })
            return web.json_response({"status": "ignored"})
        except InvalidToken:
            return web.json_response({"status": "error", "message": "Invalid pairing key"}, status=403)
        except Exception as e:
            return web.json_response({"status": "error", "message": str(e)}, status=400)

    async def handle_api_sync(self, request: web.Request):
        """Endpoint called by remote peer or UI."""
        try:
            data = await self._read_payload(request)
            item = ClipboardItem.from_dict(data)
            if not self.engine.is_hash_seen(item.hash):
                self.engine.mark_hash_seen(item.hash)
                if item.item_type == "file":
                    if not data.get("packed"):
                        return web.json_response({"status": "error", "message": "File contents missing"}, status=400)
                    saved = await asyncio.to_thread(unpack_files, data["packed"])
                    logger.info(f"Saved {len(saved)} incoming file(s) to {os.path.dirname(saved[0])}")
                    item = file_item_from_paths(saved, item_hash=item.hash)
                await self.process_and_broadcast_item(item, from_remote=True)
                return web.json_response({"status": "ok", "hash": item.hash})
            else:
                return web.json_response({"status": "already_seen", "hash": item.hash})
        except InvalidToken:
            logger.warning(f"Rejected sync from {request.remote}: invalid pairing key")
            return web.json_response({"status": "error", "message": "Invalid pairing key"}, status=403)
        except Exception as e:
            logger.error(f"Sync endpoint error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=400)

    async def handle_api_upload(self, request: web.Request):
        """Handles Drag & Drop image/file uploads from Web UI."""
        try:
            reader = await request.multipart()
            field = await reader.next()
            if field and field.name == "file":
                filename = field.filename or "pasted_image.png"
                size = 0
                buf = io.BytesIO()
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                    size += len(chunk)
                    buf.write(chunk)

                buf.seek(0)
                try:
                    img = Image.open(buf)
                    out_buf = io.BytesIO()
                    img.save(out_buf, format="PNG")
                    png_bytes = out_buf.getvalue()
                    b64_data = base64.b64encode(png_bytes).decode("ascii")

                    item = ClipboardItem(
                        item_type="image",
                        data=b64_data,
                        metadata={
                            "filename": filename,
                            "width": img.width,
                            "height": img.height,
                            "size_bytes": len(png_bytes),
                            "source": "drag_and_drop",
                        },
                    )
                    await self.process_and_broadcast_item(item, from_remote=False)
                    return web.json_response({"status": "ok", "item": item.to_dict()})
                except Exception as img_err:
                    logger.error(f"Image parse error: {img_err}")
                    return web.json_response({"status": "error", "message": "Invalid image file"}, status=400)

            return web.json_response({"status": "error", "message": "No file field found"}, status=400)
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def handle_api_status(self, request: web.Request):
        return web.json_response({
            "node": {
                "id": self.p2p.node_id,
                "name": self.p2p.hostname,
                "system": self.p2p.system,
                "port": self.port,
            },
            "version": __version__,
            "peers": self.p2p.get_active_peers_list(),
            "history_count": len(self.history),
        })

    async def handle_api_history(self, request: web.Request):
        return web.json_response({"history": self.history})

    async def handle_api_pairing_get(self, request: web.Request):
        return web.json_response({"key": self.p2p.sync_key})

    async def handle_api_pairing_set(self, request: web.Request):
        try:
            data = await request.json()
            self.p2p.set_sync_key(data.get("key", ""))
            logger.info("Pairing key changed from the dashboard")
            return web.json_response({"status": "ok"})
        except ValueError as e:
            return web.json_response({"status": "error", "message": str(e)}, status=400)

    async def handle_api_pairing_copy(self, request: web.Request):
        """Copies the key without syncing it: write_local_clipboard marks it as seen, so the
        poller neither broadcasts it nor adds it to history."""
        await asyncio.to_thread(self.engine.write_local_clipboard, ClipboardItem("text", self.p2p.sync_key))
        return web.json_response({"status": "ok"})

    async def handle_api_update_open(self, request: web.Request):
        webbrowser.open(self.updater.status()["release_url"])
        return web.json_response({"status": "ok"})

    async def handle_api_update_status(self, request: web.Request):
        if request.query.get("refresh"):
            await asyncio.to_thread(self.updater.check)
        return web.json_response(self.updater.status())

    async def handle_api_update_install(self, request: web.Request):
        if not self.updater.status()["can_install"] or self.updater.state in ("downloading", "installing"):
            return web.json_response({"status": "error", "message": "No installable update"}, status=400)
        loop = asyncio.get_running_loop()

        def on_progress(status: dict):
            loop.call_soon_threadsafe(asyncio.create_task, self.broadcast_ws({"event": "update_status", "update": status}))

        async def _run():
            if await asyncio.to_thread(self.updater.download_and_launch_installer, on_progress):
                logger.info("Installer launched, exiting so it can replace the app.")
                await asyncio.sleep(0.5)
                os._exit(0)

        asyncio.create_task(_run())
        return web.json_response({"status": "ok"})

    async def handle_api_show(self, request: web.Request):
        """A second launch of the app asks the running instance to bring its window up."""
        if self.on_show:
            self.on_show()
        return web.json_response({"status": "ok"})

    async def _update_check_loop(self):
        await asyncio.sleep(5)
        while True:
            status = await asyncio.to_thread(self.updater.check)
            if status["available"]:
                logger.info(f"Update available: {status['latest']}")
            await self.broadcast_ws({"event": "update_status", "update": status})
            await asyncio.sleep(UPDATE_CHECK_INTERVAL)

    async def handle_api_shutdown(self, request: web.Request):
        logger.info("Shutdown request received from UI / API. Shutting down...")
        async def _do_shutdown():
            await asyncio.sleep(0.35)
            try:
                await self.p2p.stop()
            except Exception:
                pass
            logger.info("Server exiting cleanly.")
            os._exit(0)
        asyncio.create_task(_do_shutdown())
        return web.json_response({"status": "ok", "message": "Server se ukončuje..."})

    async def _clipboard_poll_loop(self):
        """Periodically polls OS clipboard for new items."""
        while True:
            try:
                item = await asyncio.to_thread(self.engine.poll_clipboard)
                if item:
                    logger.info(f"Detected new local clipboard item: {item.item_type} (hash: {item.hash[:8]})")
                    await self.process_and_broadcast_item(item, from_remote=False)
            except Exception as e:
                logger.debug(f"Poll loop error: {e}")
            await asyncio.sleep(0.35)


async def start_server(port: int = DEFAULT_PORT, on_show: Optional[Callable[[], None]] = None,
                       on_ready: Optional[Callable[[], None]] = None):
    server = ClipboardServer(port=port, on_show=on_show)
    await server.p2p.start()

    runner = web.AppRunner(server.app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logger.info(f"✨ Universal Clipboard {__version__} running!")
    logger.info(f"📊 Dashboard UI: http://localhost:{port}")
    logger.info(f"💻 Device: {server.p2p.hostname} ({server.p2p.system})")

    asyncio.create_task(server._clipboard_poll_loop())
    asyncio.create_task(server._update_check_loop())
    if on_ready:
        on_ready()

    # Keep alive
    while True:
        await asyncio.sleep(3600)


def main():
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    try:
        asyncio.run(start_server(port))
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")


if __name__ == "__main__":
    main()
