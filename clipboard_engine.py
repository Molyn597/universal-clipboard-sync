import sys
import io
import os
import time
import struct
import hashlib
import base64
import logging
import threading
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from PIL import Image, ImageGrab

logger = logging.getLogger("ClipboardEngine")

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

MAX_FILE_SYNC_BYTES = 25 * 1024 * 1024  # base64 + Fernet roughly double this on the wire
RECEIVE_DIR = Path.home() / "Downloads" / "Universal Clipboard"

win32clipboard = win32con = None
if IS_WINDOWS:
    try:
        import win32clipboard
        import win32con
    except ImportError:
        pass

AppKit = Foundation = None
if IS_MACOS:
    # Native NSPasteboard access (PyObjC ships with pywebview on macOS); far more reliable than osascript
    import AppKit
    import Foundation


def _mac_pasteboard():
    return AppKit.NSPasteboard.generalPasteboard()


def _walk_files(path: str) -> List[str]:
    if not os.path.isdir(path):
        return [path]
    found = []
    for root, dirs, files in os.walk(path):
        dirs.sort()
        found.extend(os.path.join(root, f) for f in sorted(files))
    return found


def paths_total_size(paths: List[str]) -> int:
    return sum(os.path.getsize(f) for p in paths for f in _walk_files(p))


def hash_paths(paths: List[str]) -> str:
    """Content fingerprint independent of where the files live, so a received copy
    saved under another folder or name hashes the same as the sender's original."""
    h = hashlib.sha256(b"file")
    for path in paths:
        for f in _walk_files(path):
            h.update(os.path.relpath(f, path).replace("\\", "/").encode("utf-8"))
            with open(f, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(chunk)
    return h.hexdigest()


def pack_files(paths: List[str]) -> List[Dict[str, Any]]:
    """Embeds file contents for transfer; folders travel as zip archives."""
    packed = []
    for path in paths:
        name = os.path.basename(path.rstrip("\\/")) or path
        if os.path.isdir(path):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in _walk_files(path):
                    zf.write(f, os.path.relpath(f, path))
            raw, is_dir = buf.getvalue(), True
        else:
            with open(path, "rb") as fh:
                raw, is_dir = fh.read(), False
        packed.append({"name": name, "is_dir": is_dir, "content": base64.b64encode(raw).decode("ascii")})
    return packed


def _unique_path(directory: Path, name: str) -> Path:
    target = directory / name
    stem, suffix = os.path.splitext(name)
    n = 1
    while target.exists():
        target = directory / f"{stem} ({n}){suffix}"
        n += 1
    return target


def unpack_files(packed: List[Dict[str, Any]], directory: Path = RECEIVE_DIR) -> List[str]:
    directory.mkdir(parents=True, exist_ok=True)
    saved = []
    for entry in packed:
        name = os.path.basename(entry["name"].replace("\\", "/")) or "file"
        raw = base64.b64decode(entry["content"])
        target = _unique_path(directory, name)
        if entry.get("is_dir"):
            target.mkdir()
            with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                zf.extractall(target)  # extractall strips absolute paths and ".." components
        else:
            target.write_bytes(raw)
        saved.append(str(target))
    return saved


def describe_paths(paths: List[str]) -> List[Dict[str, Any]]:
    entries = []
    for path in paths:
        try:
            is_dir = os.path.isdir(path)
            size = paths_total_size([path])
        except OSError:
            is_dir, size = False, 0
        entries.append({
            "path": path,
            "name": os.path.basename(path.rstrip("\\/")) or path,
            "is_dir": is_dir,
            "size_bytes": size,
        })
    return entries


def file_item_from_paths(paths: List[str], item_hash: Optional[str] = None) -> "ClipboardItem":
    entries = describe_paths(paths)
    total = sum(e["size_bytes"] for e in entries)
    metadata: Dict[str, Any] = {"files": entries, "count": len(entries), "size_bytes": total}
    if total > MAX_FILE_SYNC_BYTES:
        # Too large to hash/transfer every time it is copied; fingerprint by paths instead
        metadata["too_large"] = True
        item_hash = item_hash or hashlib.sha256(("file-paths\n" + "\n".join(paths)).encode("utf-8")).hexdigest()
    return ClipboardItem("file", "\n".join(paths), metadata, item_hash=item_hash or hash_paths(paths))


class ClipboardItem:
    def __init__(self, item_type: str, data: str, metadata: Optional[Dict[str, Any]] = None,
                 item_hash: Optional[str] = None):
        """
        item_type: 'text' | 'image' | 'file'
        data: UTF-8 string for text, base64 encoded PNG for image,
              newline-separated absolute paths for file
        """
        self.item_type = item_type
        self.data = data
        self.metadata = metadata or {}
        self.timestamp = time.time()
        self.hash = item_hash or self._compute_hash()

    def _compute_hash(self) -> str:
        """Hashes content the way it survives an OS clipboard round-trip: line endings
        get normalized, and images are compared by pixels since PNG/BMP/TIFF
        re-encoding changes the bytes."""
        h = hashlib.sha256()
        h.update(self.item_type.encode("utf-8"))
        if self.item_type == "image":
            try:
                img = Image.open(io.BytesIO(base64.b64decode(self.data))).convert("RGB")
                h.update(f"{img.width}x{img.height}".encode("ascii"))
                h.update(img.tobytes())
                return h.hexdigest()
            except Exception:
                pass
        h.update(self.data.replace("\r\n", "\n").encode("utf-8"))
        return h.hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.item_type,
            "data": self.data,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ClipboardItem":
        item = cls(d.get("type", "text"), d.get("data", ""), d.get("metadata", {}))
        item.timestamp = d.get("timestamp", time.time())
        item.hash = d.get("hash", item._compute_hash())
        return item


class ClipboardEngine:
    def __init__(self, max_history_hashes: int = 50):
        self.recent_hashes: List[str] = []
        self.max_history = max_history_hashes
        self.last_item: Optional[ClipboardItem] = None
        self._callbacks: List[Callable[[ClipboardItem], None]] = []
        self._last_change_count: Optional[int] = None
        self._empty_reads = 0
        self._lock = threading.Lock()  # poll runs in a worker thread, writes in the event loop

    def register_callback(self, cb: Callable[[ClipboardItem], None]):
        self._callbacks.append(cb)

    def mark_hash_seen(self, item_hash: str):
        if item_hash in self.recent_hashes:
            self.recent_hashes.remove(item_hash)
        self.recent_hashes.append(item_hash)
        if len(self.recent_hashes) > self.max_history:
            self.recent_hashes.pop(0)

    def is_hash_seen(self, item_hash: str) -> bool:
        return item_hash in self.recent_hashes

    @staticmethod
    def _change_count() -> Optional[int]:
        """OS counter that increments on every clipboard change; lets us skip reads when
        nothing changed and recognise changes made by our own writes."""
        try:
            if IS_WINDOWS and win32clipboard:
                return win32clipboard.GetClipboardSequenceNumber()
            if IS_MACOS:
                return int(_mac_pasteboard().changeCount())
        except Exception:
            pass
        return None

    # ----------------- WINDOWS CLIPBOARD ACCESS -----------------
    @staticmethod
    def _open_clipboard_retry(attempts: int = 5, delay: float = 0.02) -> bool:
        """Windows allows one owner at a time; Explorer/Office briefly lock it after Ctrl+C."""
        for i in range(attempts):
            try:
                win32clipboard.OpenClipboard()
                return True
            except Exception:
                time.sleep(delay * (i + 1))
        return False

    # ----------------- READING CLIPBOARD -----------------
    def read_local_clipboard(self) -> Optional[ClipboardItem]:
        """Reads current clipboard (text or image/GIF) and returns ClipboardItem if changed."""
        try:
            # 1. Read copied files/folders (CF_HDROP on Windows, file URLs on macOS)
            file_item = self._read_files_native()
            if file_item:
                return file_item

            # 2. Read Image/Screenshot/GIF from clipboard (In-Memory)
            img_item = self._read_image_native()
            if img_item:
                return img_item

            # 3. Read Text/Code from clipboard
            text_data = self._read_text_native()
            if text_data and len(text_data.strip()) > 0:
                item = ClipboardItem(
                    item_type="text",
                    data=text_data,
                    metadata={"length": len(text_data)},
                )
                return item

        except Exception as e:
            logger.debug(f"Error reading clipboard: {e}")
        return None

    def _read_files_native(self) -> Optional[ClipboardItem]:
        paths: List[str] = []
        if IS_WINDOWS and win32clipboard:
            if not self._open_clipboard_retry():
                return None
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
                    paths = [str(p) for p in win32clipboard.GetClipboardData(win32con.CF_HDROP)]
            except Exception as e:
                logger.debug(f"CF_HDROP read failed: {e}")
            finally:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
        elif IS_MACOS:
            try:
                urls = _mac_pasteboard().readObjectsForClasses_options_(
                    [AppKit.NSURL], {AppKit.NSPasteboardURLReadingFileURLsOnlyKey: True}
                )
                paths = [str(u.path()) for u in (urls or [])]
            except Exception as e:
                logger.debug(f"NSPasteboard file read failed: {e}")

        paths = [p for p in paths if os.path.exists(p)]
        if not paths:
            return None
        return file_item_from_paths(paths)

    def _read_image_native(self) -> Optional[ClipboardItem]:
        if IS_WINDOWS:
            try:
                img = ImageGrab.grabclipboard()
                if isinstance(img, Image.Image):
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    png_bytes = buf.getvalue()
                    b64_data = base64.b64encode(png_bytes).decode("ascii")
                    return ClipboardItem(
                        item_type="image",
                        data=b64_data,
                        metadata={"width": img.width, "height": img.height, "size_bytes": len(png_bytes)},
                    )
            except Exception:
                pass
        elif IS_MACOS:
            try:
                pb = _mac_pasteboard()
                data = pb.dataForType_(AppKit.NSPasteboardTypePNG) or pb.dataForType_(AppKit.NSPasteboardTypeTIFF)
                if data:
                    img = Image.open(io.BytesIO(bytes(data)))
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    png_bytes = buf.getvalue()
                    b64_clean = base64.b64encode(png_bytes).decode("ascii")
                    return ClipboardItem(
                        item_type="image",
                        data=b64_clean,
                        metadata={"width": img.width, "height": img.height, "size_bytes": len(png_bytes)},
                    )
            except Exception:
                pass
        return None

    def _read_text_native(self) -> Optional[str]:
        if IS_WINDOWS and win32clipboard:
            if not self._open_clipboard_retry():
                return None
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    return win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            except Exception as e:
                logger.debug(f"CF_UNICODETEXT read failed: {e}")
            finally:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
        elif IS_MACOS:
            text = _mac_pasteboard().stringForType_(AppKit.NSPasteboardTypeString)
            return str(text) if text is not None else None
        return None

    # ----------------- WRITING CLIPBOARD -----------------
    def write_local_clipboard(self, item: ClipboardItem) -> bool:
        """Writes item to the local OS clipboard and marks its hash as seen.
        For 'file' items, data must hold paths that exist on this machine."""
        with self._lock:
            self.mark_hash_seen(item.hash)
            self.last_item = item

            if item.item_type == "text":
                ok = self._write_text_native(item.data)
            elif item.item_type == "image":
                ok = self._write_image_native(item.data)
            elif item.item_type == "file":
                ok = self._write_files_native(item.data.splitlines())
            else:
                ok = False
            # Our own write bumps the OS change counter; record it so the poller ignores it
            self._last_change_count = self._change_count()
            return ok

    def _write_files_native(self, paths: List[str]) -> bool:
        if IS_WINDOWS and win32clipboard:
            # DROPFILES header (pFiles offset, pt.x, pt.y, fNC, fWide) + double-NUL terminated UTF-16 list
            data = struct.pack("IiiII", 20, 0, 0, 0, 1) + ("\0".join(paths) + "\0\0").encode("utf-16-le")
            if not self._open_clipboard_retry():
                return False
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_HDROP, data)
                return True
            except Exception as e:
                logger.error(f"Failed to write files to Windows clipboard: {e}")
                return False
            finally:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
        elif IS_MACOS:
            try:
                pb = _mac_pasteboard()
                pb.clearContents()
                return bool(pb.writeObjects_([AppKit.NSURL.fileURLWithPath_(p) for p in paths]))
            except Exception as e:
                logger.error(f"Failed to write files to Mac clipboard: {e}")
        return False

    def _write_text_native(self, text: str) -> bool:
        if IS_WINDOWS and win32clipboard:
            if not self._open_clipboard_retry():
                return False
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
                win32clipboard.CloseClipboard()
                return True
            except Exception as e:
                logger.error(f"Failed to write text to Windows clipboard: {e}")
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
                return False
        elif IS_MACOS:
            try:
                pb = _mac_pasteboard()
                pb.clearContents()
                return bool(pb.setString_forType_(text, AppKit.NSPasteboardTypeString))
            except Exception as e:
                logger.error(f"Failed to write text to Mac clipboard: {e}")
                return False
        return False

    def _write_image_native(self, b64_png: str) -> bool:
        try:
            png_bytes = base64.b64decode(b64_png)
            img = Image.open(io.BytesIO(png_bytes))

            if IS_WINDOWS and win32clipboard:
                # Convert image to BMP DIB format for Windows clipboard
                output = io.BytesIO()
                img.convert("RGB").save(output, "BMP")
                data = output.getvalue()[14:]  # Strip standard 14-byte BMP header for CF_DIB
                output.close()

                if not self._open_clipboard_retry():
                    return False
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_DIB, data)
                win32clipboard.CloseClipboard()
                return True

            elif IS_MACOS:
                ns_data = Foundation.NSData.dataWithBytes_length_(png_bytes, len(png_bytes))
                pb = _mac_pasteboard()
                pb.clearContents()
                # PNG for modern apps plus TIFF (via NSImage) for older ones that only read TIFF
                image = AppKit.NSImage.alloc().initWithData_(ns_data)
                ok = bool(pb.writeObjects_([image])) if image else False
                return bool(pb.setData_forType_(ns_data, AppKit.NSPasteboardTypePNG)) or ok

        except Exception as e:
            logger.error(f"Failed to write image to clipboard: {e}")
            if IS_WINDOWS and win32clipboard:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
            return False
        return False

    def poll_clipboard(self) -> Optional[ClipboardItem]:
        """Polls clipboard, triggers callbacks if new item detected."""
        with self._lock:
            change_count = self._change_count()
            if change_count is not None and change_count == self._last_change_count:
                return None
            item = self.read_local_clipboard()
            # An empty read may just mean another app still holds the clipboard lock; retry a few polls
            self._empty_reads = 0 if item else self._empty_reads + 1
            if item or self._empty_reads >= 3:
                self._last_change_count = change_count
            if not item or self.is_hash_seen(item.hash):
                return None
            self.mark_hash_seen(item.hash)
            self.last_item = item
        for cb in self._callbacks:
            try:
                cb(item)
            except Exception as e:
                logger.error(f"Callback error: {e}")
        return item
