import sys
import os
import io
import json
import time
import base64
import asyncio
import logging
import subprocess
import webbrowser
from pathlib import Path
from typing import Callable, Optional

from aiohttp import web
from cryptography.fernet import InvalidToken
from PIL import Image

from app_paths import DATA_DIR, resource
from clipboard_engine import (
    MAX_FILE_SYNC_BYTES, RECEIVE_DIR, ClipboardEngine, ClipboardItem, file_item_from_paths, pack_files, unpack_files,
)
from p2p_sync import P2PManager
from previews import MAX_PDF_PAGES, file_kind, file_preview, image_thumbnail, pdf_page_count, pdf_page_png, thumbnail_png
from store import Store
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
OUTBOX_DIR = DATA_DIR / "Odeslane"  # files dropped into the app are kept here so they can be re-copied later
LOOPBACK = {"127.0.0.1", "::1"}
PEER_ROUTES = {"/api/ping", "/api/sync"}  # the only endpoints reachable from other devices
UPDATE_CHECK_INTERVAL = 6 * 3600
MAX_LISTED_FILES = 300
MAX_TEXT_PREVIEW_BYTES = 1024 * 1024

Notifier = Callable[[str, str], None]


def _entry(path: Path) -> dict:
    stat = path.stat()
    is_dir = path.is_dir()
    return {
        "path": str(path), "name": path.name, "is_dir": is_dir, "kind": file_kind(str(path)),
        "size": 0 if is_dir else stat.st_size, "mtime": stat.st_mtime,
    }


def _item_size(item: ClipboardItem) -> int:
    if item.item_type == "text":
        return len(item.data.encode("utf-8"))
    return int(item.metadata.get("size_bytes", 0))


def _open(path: str):
    """Opens a file in its default application."""
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])


def _reveal(path: str):
    """Shows a file in Explorer/Finder, or opens a folder."""
    if sys.platform == "win32":
        if os.path.isdir(path):
            os.startfile(path)
        else:
            subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path] if os.path.isdir(path) else ["open", "-R", path])


class ClipboardServer:
    def __init__(self, port: int = DEFAULT_PORT, on_show: Optional[Callable[[], None]] = None,
                 notifier: Optional[Notifier] = None):
        self.port = port
        self.on_show = on_show
        self.notifier = notifier
        self.updater = Updater()
        self.store = Store()
        self.app = web.Application(
            client_max_size=64 * 1024 * 1024,  # fits a 25MB file after base64 + Fernet overhead
            middlewares=[self._access_guard],
        )
        self.engine = ClipboardEngine()
        for h in self.store.history:
            self.engine.mark_hash_seen(h["hash"])
        self.p2p = P2PManager(local_http_port=self.port, on_peer_change=self._on_peers_updated)
        self.ws_clients = set()
        self._setup_routes()

    def _setup_routes(self):
        r = self.app.router
        r.add_get("/", self.handle_index)
        r.add_get("/ws", self.handle_ws)
        r.add_post("/api/ping", self.handle_api_ping)
        r.add_post("/api/sync", self.handle_api_sync)
        r.add_post("/api/upload", self.handle_api_upload)
        r.add_post("/api/upload-files", self.handle_api_upload_files)
        r.add_post("/api/shutdown", self.handle_api_shutdown)
        r.add_get("/api/status", self.handle_api_status)
        r.add_get("/api/history", self.handle_api_history)
        r.add_post("/api/history/pin", self.handle_api_history_pin)
        r.add_post("/api/history/delete", self.handle_api_history_delete)
        r.add_post("/api/history/clear", self.handle_api_history_clear)
        r.add_post("/api/history/copy", self.handle_api_history_copy)
        r.add_post("/api/history/reveal", self.handle_api_history_reveal)
        r.add_post("/api/history/open", self.handle_api_history_open)
        r.add_get("/api/history/file", self.handle_api_history_file)
        r.add_post("/api/open-received", self.handle_api_open_received)
        r.add_get("/api/files", self.handle_api_files)
        r.add_get("/api/files/info", self.handle_api_files_info)
        r.add_get("/api/files/raw", self.handle_api_files_raw)
        r.add_get("/api/files/text", self.handle_api_files_text)
        r.add_get("/api/files/thumb", self.handle_api_files_thumb)
        r.add_get("/api/files/pdf-page", self.handle_api_files_pdf_page)
        r.add_post("/api/files/open", self.handle_api_files_open)
        r.add_post("/api/files/reveal", self.handle_api_files_reveal)
        r.add_post("/api/files/copy", self.handle_api_files_copy)
        r.add_post("/api/files/send", self.handle_api_files_send)
        r.add_get("/api/settings", self.handle_api_settings_get)
        r.add_post("/api/settings", self.handle_api_settings_set)
        r.add_get("/api/pairing", self.handle_api_pairing_get)
        r.add_post("/api/pairing", self.handle_api_pairing_set)
        r.add_post("/api/pairing/copy", self.handle_api_pairing_copy)
        r.add_get("/api/update", self.handle_api_update_status)
        r.add_post("/api/update/install", self.handle_api_update_install)
        r.add_post("/api/update/open", self.handle_api_update_open)
        r.add_post("/api/show", self.handle_api_show)
        r.add_static("/static/", STATIC_DIR, name="static")

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

    @property
    def receive_dir(self) -> Path:
        return Path(self.store.settings["receive_dir"]) if self.store.settings["receive_dir"] else RECEIVE_DIR

    def _history_paths(self, direction: Optional[str] = None) -> list:
        return [Path(p) for h in self.store.history
                if h["type"] == "file" and (direction is None or h.get("direction") == direction)
                for p in h.get("data", "").splitlines()]

    def _allowed_path(self, raw: str) -> Optional[Path]:
        """The file API may only touch the received/sent folders and files that appear in history,
        never arbitrary paths on disk."""
        if not raw:
            return None
        path = Path(raw).resolve()
        if not path.exists():
            return None
        roots = [self.receive_dir.resolve(), OUTBOX_DIR.resolve(), *(p.resolve() for p in self._history_paths())]
        if any(path == root or root in path.parents for root in roots):
            return path
        return None

    def _query_path(self, request: web.Request) -> Path:
        path = self._allowed_path(request.query.get("path", ""))
        if not path:
            raise web.HTTPNotFound()
        return path

    async def _body_path(self, request: web.Request) -> Path:
        path = self._allowed_path((await request.json()).get("path", ""))
        if not path:
            raise web.HTTPNotFound()
        return path

    @property
    def node_info(self) -> dict:
        return {"id": self.p2p.node_id, "name": self.p2p.hostname, "system": self.p2p.system, "port": self.port}

    async def handle_index(self, request: web.Request):
        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_path):
            return web.FileResponse(index_path)
        return web.Response(text="Dashboard UI files not found.", status=404)

    async def handle_ws(self, request: web.Request):
        ws = web.WebSocketResponse(max_msg_size=64 * 1024 * 1024)
        await ws.prepare(request)
        self.ws_clients.add(ws)
        try:
            await ws.send_json({
                "event": "init",
                "node": self.node_info,
                "version": __version__,
                "peers": self.p2p.get_active_peers_list(),
                "history": self.store.history,
                "stats": self.store.stats,
                "settings": self.store.settings,
                "update": self.updater.status(),
                "receive_dir": str(self.receive_dir),
                "default_receive_dir": str(RECEIVE_DIR),
            })
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        if data.get("action") == "push_text" and data.get("text"):
                            item = ClipboardItem("text", data["text"], {"source": "dashboard"})
                            await asyncio.to_thread(self.engine.write_local_clipboard, item)
                            await self.process_and_broadcast_item(item, from_remote=False)
                    except Exception as e:
                        logger.error(f"WS message error: {e}")
        finally:
            self.ws_clients.discard(ws)
        return ws

    async def broadcast_ws(self, event_data: dict):
        dead = []
        for ws in list(self.ws_clients):
            try:
                await ws.send_json(event_data)
            except Exception:
                dead.append(ws)
        for d in dead:
            self.ws_clients.discard(d)

    def _on_peers_updated(self, peers: list):
        asyncio.create_task(self.broadcast_ws({"event": "peers_updated", "peers": peers}))

    async def _persist(self):
        await asyncio.to_thread(self.store.save)

    async def _history_changed(self):
        await self.broadcast_ws({"event": "history", "history": self.store.history, "stats": self.store.stats})
        await self._persist()

    def _notify(self, title: str, message: str):
        if self.notifier and self.store.settings["notifications"]:
            try:
                self.notifier(title, message)
            except Exception as e:
                logger.debug(f"Notification failed: {e}")

    async def process_and_broadcast_item(self, item: ClipboardItem, from_remote: bool = False,
                                         origin: Optional[dict] = None):
        """Records the item in history, writes it to the local clipboard (if remote) or sends it to peers."""
        item_dict = item.to_dict()
        if item.item_type == "image":
            item_dict["metadata"] = {**item.metadata, "thumb": await asyncio.to_thread(image_thumbnail, item.data)}
        elif item.item_type == "file":
            preview = await asyncio.to_thread(file_preview, item.data.splitlines())
            item_dict["metadata"] = {**item.metadata, "preview": preview}
        size = _item_size(item)
        peers = self.p2p.get_active_peers_list()

        if from_remote:
            origin = origin or {}
            item_dict.update(direction="received", device=origin.get("name", "Neznámé zařízení"),
                             device_system=origin.get("system", ""))
            self.store.record_transfer("received", size)
            logger.info(f"Writing incoming {item.item_type} to local clipboard...")
            await asyncio.to_thread(self.engine.write_local_clipboard, item)
            label = {"text": "Text", "image": "Obrázek", "file": "Soubory"}.get(item.item_type, "Položka")
            self._notify(f"{label} z {item_dict['device']}", "Je ve schránce, stačí vložit.")
        else:
            item_dict.update(direction="sent", device=self.p2p.hostname, device_system=self.p2p.system,
                             targets=[p["name"] for p in peers])
            if item.metadata.get("too_large"):
                logger.warning(f"Copied files exceed the sync limit ({size} bytes), not sending.")
            elif peers:
                self.store.record_transfer("sent", size)
                payload = {**item_dict, "origin": {"name": self.p2p.hostname, "system": self.p2p.system}}
                payload["metadata"] = item.metadata  # thumbnails are rebuilt by the receiver
                if item.item_type == "file":
                    # Contents ride outside metadata so they never land in history or WebSocket events
                    payload["packed"] = await asyncio.to_thread(pack_files, item.data.splitlines())
                asyncio.create_task(self.p2p.broadcast_to_peers(payload))

        self.store.add(item_dict)
        await self.broadcast_ws({"event": "clipboard_item", "item": item_dict, "from_remote": from_remote,
                                 "stats": self.store.stats})
        await self._persist()

    async def handle_api_ping(self, request: web.Request):
        """Direct unicast handshake from a remote peer."""
        try:
            data = self.p2p.unseal(await request.read())
            node_id = data.get("id")
            if node_id and node_id != self.p2p.node_id:
                self.p2p.handle_peer_beacon(node_id, data.get("name", "Unknown"), request.remote,
                                            data.get("port", DEFAULT_PORT), data.get("system", "unknown"))
                return web.json_response({"status": "ok", **self.node_info})
            return web.json_response({"status": "ignored"})
        except InvalidToken:
            return web.json_response({"status": "error", "message": "Invalid pairing key"}, status=403)
        except Exception as e:
            return web.json_response({"status": "error", "message": str(e)}, status=400)

    async def handle_api_sync(self, request: web.Request):
        """Endpoint called by remote peers (sealed) or the local dashboard (plain JSON)."""
        if self.store.settings["paused"]:
            return web.json_response({"status": "paused"}, status=423)
        try:
            data = await self._read_payload(request)
            item = ClipboardItem.from_dict(data)
            if self.engine.is_hash_seen(item.hash):
                return web.json_response({"status": "already_seen", "hash": item.hash})
            self.engine.mark_hash_seen(item.hash)
            if item.item_type == "file":
                if not data.get("packed"):
                    return web.json_response({"status": "error", "message": "File contents missing"}, status=400)
                saved = await asyncio.to_thread(unpack_files, data["packed"], self.receive_dir)
                logger.info(f"Saved {len(saved)} incoming file(s) to {os.path.dirname(saved[0])}")
                item = file_item_from_paths(saved, item_hash=item.hash)
            from_peer = request.remote not in LOOPBACK or request.content_type != "application/json"
            await self.process_and_broadcast_item(item, from_remote=from_peer, origin=data.get("origin"))
            return web.json_response({"status": "ok", "hash": item.hash})
        except InvalidToken:
            logger.warning(f"Rejected sync from {request.remote}: invalid pairing key")
            return web.json_response({"status": "error", "message": "Invalid pairing key"}, status=403)
        except Exception as e:
            logger.error(f"Sync endpoint error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=400)

    async def handle_api_upload(self, request: web.Request):
        """An image pasted into the dashboard (Ctrl+V of a screenshot)."""
        try:
            reader = await request.multipart()
            field = await reader.next()
            if not field or field.name != "file":
                return web.json_response({"status": "error", "message": "No file field found"}, status=400)
            img = Image.open(io.BytesIO(await field.read()))
            out_buf = io.BytesIO()
            img.save(out_buf, format="PNG")
            png_bytes = out_buf.getvalue()
            item = ClipboardItem("image", base64.b64encode(png_bytes).decode("ascii"), {
                "filename": field.filename or "pasted_image.png",
                "width": img.width, "height": img.height, "size_bytes": len(png_bytes), "source": "dashboard",
            })
            if self.engine.is_hash_seen(item.hash):
                return web.json_response({"status": "already_sent"})
            await asyncio.to_thread(self.engine.write_local_clipboard, item)
            await self.process_and_broadcast_item(item, from_remote=False)
            return web.json_response({"status": "ok"})
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return web.json_response({"status": "error", "message": "Obrázek se nepodařilo načíst"}, status=400)

    async def handle_api_upload_files(self, request: web.Request):
        """Files dragged into the dashboard: stored in the outbox, put on the clipboard and sent to peers."""
        target = OUTBOX_DIR / time.strftime("%Y-%m-%d_%H-%M-%S")
        saved, total = [], 0
        try:
            reader = await request.multipart()
            while (field := await reader.next()) is not None:
                if field.name != "files" or not field.filename:
                    continue
                target.mkdir(parents=True, exist_ok=True)
                path = target / Path(field.filename.replace("\\", "/")).name
                with open(path, "wb") as fh:
                    while chunk := await field.read_chunk():
                        total += len(chunk)
                        if total > MAX_FILE_SYNC_BYTES:
                            raise ValueError("too_large")
                        fh.write(chunk)
                saved.append(str(path))
        except ValueError:
            return web.json_response({"status": "error", "message": "Soubory jsou větší než 25 MB"}, status=413)
        if not saved:
            return web.json_response({"status": "error", "message": "Žádné soubory"}, status=400)
        item = await asyncio.to_thread(file_item_from_paths, saved)
        if self.engine.is_hash_seen(item.hash):
            return web.json_response({"status": "already_sent", "count": len(saved)})
        item.metadata["source"] = "dashboard"
        await asyncio.to_thread(self.engine.write_local_clipboard, item)
        await self.process_and_broadcast_item(item, from_remote=False)
        return web.json_response({"status": "ok", "count": len(saved)})

    async def handle_api_status(self, request: web.Request):
        return web.json_response({
            "node": self.node_info,
            "version": __version__,
            "peers": self.p2p.get_active_peers_list(),
            "history_count": len(self.store.history),
        })

    async def handle_api_history(self, request: web.Request):
        return web.json_response({"history": self.store.history})

    async def _json_hash(self, request: web.Request):
        data = await request.json()
        return data, self.store.find(data.get("hash", ""))

    async def handle_api_history_pin(self, request: web.Request):
        data, item = await self._json_hash(request)
        if not item:
            raise web.HTTPNotFound()
        self.store.set_pinned(item["hash"], bool(data.get("pinned")))
        await self._history_changed()
        return web.json_response({"status": "ok"})

    async def handle_api_history_delete(self, request: web.Request):
        _, item = await self._json_hash(request)
        if item:
            self.store.delete(item["hash"])
            await self._history_changed()
        return web.json_response({"status": "ok"})

    async def handle_api_history_clear(self, request: web.Request):
        self.store.clear_unpinned()
        await self._history_changed()
        return web.json_response({"status": "ok"})

    async def handle_api_history_copy(self, request: web.Request):
        """Puts a history item back on the local clipboard without re-sending it."""
        _, item = await self._json_hash(request)
        if not item or not item.get("data"):
            return web.json_response({"status": "error", "message": "Položka už není dostupná"}, status=404)
        if item["type"] == "file" and not all(os.path.exists(p) for p in item["data"].splitlines()):
            return web.json_response({"status": "error", "message": "Soubory už neexistují"}, status=404)
        clip = ClipboardItem(item["type"], item["data"], item.get("metadata"), item_hash=item["hash"])
        ok = await asyncio.to_thread(self.engine.write_local_clipboard, clip)
        return web.json_response({"status": "ok" if ok else "error"}, status=200 if ok else 500)

    def _existing_paths(self, item: Optional[dict]) -> list:
        if not item or item["type"] != "file":
            return []
        return [p for p in item.get("data", "").splitlines() if os.path.exists(p)]

    async def handle_api_history_reveal(self, request: web.Request):
        _, item = await self._json_hash(request)
        paths = self._existing_paths(item)
        if not paths:
            return web.json_response({"status": "error", "message": "Soubory už neexistují"}, status=404)
        _reveal(paths[0])
        return web.json_response({"status": "ok"})

    async def handle_api_history_open(self, request: web.Request):
        _, item = await self._json_hash(request)
        paths = self._existing_paths(item)
        if not paths:
            return web.json_response({"status": "error", "message": "Soubory už neexistují"}, status=404)
        _open(paths[0])
        return web.json_response({"status": "ok"})

    async def handle_api_history_file(self, request: web.Request):
        """Serves the first file of a history item for the full-size preview (localhost only)."""
        paths = self._existing_paths(self.store.find(request.query.get("hash", "")))
        if not paths or os.path.isdir(paths[0]):
            raise web.HTTPNotFound()
        return web.FileResponse(paths[0])

    async def handle_api_open_received(self, request: web.Request):
        self.receive_dir.mkdir(parents=True, exist_ok=True)
        _reveal(str(self.receive_dir))
        return web.json_response({"status": "ok"})

    async def handle_api_settings_get(self, request: web.Request):
        return web.json_response(self.store.settings)

    async def handle_api_settings_set(self, request: web.Request):
        changes = await request.json()
        if changes.get("receive_dir"):
            target = Path(changes["receive_dir"]).expanduser()
            try:
                if not target.is_absolute():
                    raise ValueError
                target.mkdir(parents=True, exist_ok=True)
            except (OSError, ValueError):
                return web.json_response({"status": "error", "message": "Do této složky nejde ukládat"}, status=400)
            changes["receive_dir"] = str(target)
        self.store.update_settings(changes)
        await self.broadcast_ws({"event": "settings", "settings": self.store.settings, "receive_dir": str(self.receive_dir)})
        await self._persist()
        return web.json_response({**self.store.settings, "effective_receive_dir": str(self.receive_dir)})

    # ----------------- FILE BROWSER & VIEWER -----------------
    def _list_files(self, scope: str) -> list:
        if scope == "received":
            candidates = list(self.receive_dir.iterdir()) if self.receive_dir.exists() else []
        else:
            outbox = [p for d in OUTBOX_DIR.iterdir() if d.is_dir() for p in d.iterdir()] if OUTBOX_DIR.exists() else []
            candidates = outbox + self._history_paths("sent")
        seen, entries = set(), []
        for path in candidates:
            key = str(path.resolve()) if path.exists() else None
            if key and key not in seen and not path.name.startswith("."):
                seen.add(key)
                entries.append(_entry(path))
        entries.sort(key=lambda e: e["mtime"], reverse=True)
        return entries[:MAX_LISTED_FILES]

    async def handle_api_files(self, request: web.Request):
        scope = request.query.get("scope", "received")
        files = await asyncio.to_thread(self._list_files, scope)
        return web.json_response({"files": files, "dir": str(self.receive_dir if scope == "received" else OUTBOX_DIR)})

    async def handle_api_files_info(self, request: web.Request):
        path = self._query_path(request)
        info = _entry(path)
        if info["kind"] == "pdf":
            info["pages"] = min(await asyncio.to_thread(pdf_page_count, str(path)), MAX_PDF_PAGES)
        if path.is_dir():
            info["children"] = [_entry(p) for p in sorted(path.iterdir())[:200]]
        return web.json_response(info)

    async def handle_api_files_raw(self, request: web.Request):
        path = self._query_path(request)
        if path.is_dir():
            raise web.HTTPNotFound()
        return web.FileResponse(path)

    async def handle_api_files_text(self, request: web.Request):
        path = self._query_path(request)
        with open(path, "rb") as fh:
            raw = fh.read(MAX_TEXT_PREVIEW_BYTES + 1)
        text = raw[:MAX_TEXT_PREVIEW_BYTES].decode("utf-8", errors="replace")
        return web.json_response({"text": text, "truncated": len(raw) > MAX_TEXT_PREVIEW_BYTES})

    async def handle_api_files_thumb(self, request: web.Request):
        png = await asyncio.to_thread(thumbnail_png, str(self._query_path(request)))
        if not png:
            raise web.HTTPNotFound()
        return web.Response(body=png, content_type="image/png", headers={"Cache-Control": "max-age=3600"})

    async def handle_api_files_pdf_page(self, request: web.Request):
        path = self._query_path(request)
        page = int(request.query.get("page", 0))
        png = await asyncio.to_thread(pdf_page_png, str(path), page)
        return web.Response(body=png, content_type="image/png", headers={"Cache-Control": "max-age=3600"})

    async def handle_api_files_open(self, request: web.Request):
        _open(str(await self._body_path(request)))
        return web.json_response({"status": "ok"})

    async def handle_api_files_reveal(self, request: web.Request):
        _reveal(str(await self._body_path(request)))
        return web.json_response({"status": "ok"})

    async def handle_api_files_copy(self, request: web.Request):
        """Puts the file on the local clipboard only (marked as seen, so it is not re-sent)."""
        path = await self._body_path(request)
        item = await asyncio.to_thread(file_item_from_paths, [str(path)])
        await asyncio.to_thread(self.engine.write_local_clipboard, item)
        return web.json_response({"status": "ok"})

    async def handle_api_files_send(self, request: web.Request):
        path = await self._body_path(request)
        item = await asyncio.to_thread(file_item_from_paths, [str(path)])
        await self.process_and_broadcast_item(item, from_remote=False)
        return web.json_response({"status": "ok"})

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
            status = await asyncio.to_thread(self.updater.check)
            await self.broadcast_ws({"event": "update_status", "update": status})
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
                await self._persist()
                await asyncio.sleep(0.5)
                os._exit(0)

        asyncio.create_task(_run())
        return web.json_response({"status": "ok"})

    async def handle_api_show(self, request: web.Request):
        """A second launch of the app asks the running instance to bring its window up."""
        if self.on_show:
            self.on_show()
        return web.json_response({"status": "ok"})

    async def handle_api_shutdown(self, request: web.Request):
        logger.info("Shutdown request received from UI / API. Shutting down...")

        async def _do_shutdown():
            await asyncio.sleep(0.35)
            try:
                await self._persist()
                await self.p2p.stop()
            except Exception:
                pass
            os._exit(0)
        asyncio.create_task(_do_shutdown())
        return web.json_response({"status": "ok", "message": "Server se ukončuje..."})

    async def _update_check_loop(self):
        await asyncio.sleep(5)
        while True:
            status = await asyncio.to_thread(self.updater.check)
            if status["available"]:
                logger.info(f"Update available: {status['latest']}")
            await self.broadcast_ws({"event": "update_status", "update": status})
            await asyncio.sleep(UPDATE_CHECK_INTERVAL)

    async def _clipboard_poll_loop(self):
        """Periodically polls OS clipboard for new items."""
        while True:
            try:
                item = await asyncio.to_thread(self.engine.poll_clipboard)
                # While paused the poller keeps consuming changes so resuming does not resend old copies
                if item and not self.store.settings["paused"]:
                    logger.info(f"Detected new local clipboard item: {item.item_type} (hash: {item.hash[:8]})")
                    await self.process_and_broadcast_item(item, from_remote=False)
            except Exception as e:
                logger.debug(f"Poll loop error: {e}")
            await asyncio.sleep(0.35)


async def start_server(port: int = DEFAULT_PORT, on_show: Optional[Callable[[], None]] = None,
                       on_ready: Optional[Callable[["ClipboardServer"], None]] = None,
                       notifier: Optional[Notifier] = None):
    server = ClipboardServer(port=port, on_show=on_show, notifier=notifier)
    await server.p2p.start()

    runner = web.AppRunner(server.app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logger.info(f"Universal Clipboard {__version__} running on http://localhost:{port}")
    logger.info(f"Device: {server.p2p.hostname} ({server.p2p.system})")

    asyncio.create_task(server._clipboard_poll_loop())
    asyncio.create_task(server._update_check_loop())
    if on_ready:
        on_ready(server)

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
