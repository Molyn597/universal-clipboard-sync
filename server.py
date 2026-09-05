import sys
import os
import io
import json
import base64
import time
import asyncio
import logging
from aiohttp import web
from PIL import Image

from clipboard_engine import ClipboardEngine, ClipboardItem
from p2p_sync import P2PManager
try:
    from tray_icon import setup_tray
except ImportError:
    setup_tray = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ClipboardServer")

DEFAULT_PORT = 7890
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


class ClipboardServer:
    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self.app = web.Application(client_max_size=50 * 1024 * 1024)  # 50MB max for big screenshots/images
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
        self.app.router.add_static("/static/", STATIC_DIR, name="static")

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
            self.engine.write_local_clipboard(item)
        else:
            # Broadcast to peers across Wi-Fi
            logger.info(f"Broadcasting local {item.item_type} to LAN peers...")
            asyncio.create_task(self.p2p.broadcast_to_peers(item_dict))

        # Notify local UI Dashboard
        await self.broadcast_ws({"event": "clipboard_item", "item": item_dict, "from_remote": from_remote})

    async def handle_api_ping(self, request: web.Request):
        """Direct unicast handshake from a remote peer."""
        try:
            data = await request.json()
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
        except Exception as e:
            return web.json_response({"status": "error", "message": str(e)}, status=400)

    async def handle_api_sync(self, request: web.Request):
        """Endpoint called by remote peer or UI."""
        try:
            data = await request.json()
            item = ClipboardItem.from_dict(data)
            if not self.engine.is_hash_seen(item.hash):
                self.engine.mark_hash_seen(item.hash)
                await self.process_and_broadcast_item(item, from_remote=True)
                return web.json_response({"status": "ok", "hash": item.hash})
            else:
                return web.json_response({"status": "already_seen", "hash": item.hash})
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
            "peers": self.p2p.get_active_peers_list(),
            "history_count": len(self.history),
        })

    async def handle_api_history(self, request: web.Request):
        return web.json_response({"history": self.history})

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
                item = self.engine.poll_clipboard()
                if item:
                    logger.info(f"Detected new local clipboard item: {item.item_type} (hash: {item.hash[:8]})")
                    await self.process_and_broadcast_item(item, from_remote=False)
            except Exception as e:
                logger.debug(f"Poll loop error: {e}")
            await asyncio.sleep(0.35)


async def start_server(port: int = DEFAULT_PORT):
    server = ClipboardServer(port=port)
    await server.p2p.start()

    runner = web.AppRunner(server.app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logger.info(f"✨ Universal Clipboard Sync running!")
    logger.info(f"📊 Dashboard UI: http://localhost:{port}")
    logger.info(f"💻 Device: {server.p2p.hostname} ({server.p2p.system})")

    # Start Tray icon in background if supported
    if setup_tray:
        try:
            setup_tray()
            logger.info("🟢 System Tray icon initialized (dole vpravo vedle hodin).")
        except Exception as e:
            logger.debug(f"Tray init error: {e}")

    # Start clipboard background poller
    asyncio.create_task(server._clipboard_poll_loop())

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
