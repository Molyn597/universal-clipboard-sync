import sys
import io
import os
import time
import hashlib
import base64
import logging
import platform
import subprocess
from typing import Optional, Dict, Any, List, Callable
from PIL import Image, ImageGrab

logger = logging.getLogger("ClipboardEngine")

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

if IS_WINDOWS:
    try:
        import win32clipboard
        import win32con
    except ImportError:
        win32clipboard = None
        win32con = None


class ClipboardItem:
    def __init__(self, item_type: str, data: str, metadata: Optional[Dict[str, Any]] = None):
        """
        item_type: 'text' | 'image'
        data: UTF-8 string for text, or base64 encoded PNG for image
        """
        self.item_type = item_type
        self.data = data
        self.metadata = metadata or {}
        self.timestamp = time.time()
        self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        h = hashlib.sha256()
        h.update(self.item_type.encode("utf-8"))
        h.update(self.data.encode("utf-8"))
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

    # ----------------- READING CLIPBOARD -----------------
    def read_local_clipboard(self) -> Optional[ClipboardItem]:
        """Reads current clipboard (text or image/GIF) and returns ClipboardItem if changed."""
        try:
            # 1. Read Image/Screenshot/GIF from clipboard (In-Memory)
            img_item = self._read_image_native()
            if img_item:
                return img_item

            # 2. Read Text/Code from clipboard
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
                # Fast in-memory Cocoa NSPasteboard image read
                script = '''
                use framework "AppKit"
                use framework "Foundation"
                set pb to current application's NSPasteboard's generalPasteboard()
                set imgData to pb's dataForType:(current application's NSPasteboardTypePNG)
                if imgData is missing value then
                    set imgData to pb's dataForType:(current application's NSPasteboardTypeTIFF)
                end if
                if imgData is not missing value then
                    set b64 to imgData's base64EncodedStringWithOptions:0
                    return b64 as text
                end if
                return ""
                '''
                p = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
                b64_res = p.stdout.strip()
                if b64_res:
                    raw_bytes = base64.b64decode(b64_res)
                    img = Image.open(io.BytesIO(raw_bytes))
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
            try:
                win32clipboard.OpenClipboard()
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    win32clipboard.CloseClipboard()
                    return data
                win32clipboard.CloseClipboard()
            except Exception:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
        elif IS_MACOS:
            try:
                p = subprocess.run(["pbpaste"], capture_output=True, text=True)
                if p.returncode == 0:
                    return p.stdout
            except Exception:
                pass
        return None

    # ----------------- WRITING CLIPBOARD -----------------
    def write_local_clipboard(self, item: ClipboardItem) -> bool:
        """Writes item to the local OS clipboard and marks its hash as seen."""
        self.mark_hash_seen(item.hash)
        self.last_item = item

        if item.item_type == "text":
            return self._write_text_native(item.data)
        elif item.item_type == "image":
            return self._write_image_native(item.data)
        return False

    def _write_text_native(self, text: str) -> bool:
        if IS_WINDOWS and win32clipboard:
            try:
                win32clipboard.OpenClipboard()
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
                p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
                p.communicate(text.encode("utf-8"))
                return p.returncode == 0
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

                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_DIB, data)
                win32clipboard.CloseClipboard()
                return True

            elif IS_MACOS:
                # Fast in-memory Cocoa NSPasteboard image write
                script = f'''
                use framework "AppKit"
                use framework "Foundation"
                set b64Data to current application's NSString's stringWithString:"{b64_png}"
                set rawData to current application's NSData's alloc()'s initWithBase64EncodedString:b64Data options:0
                set theImage to current application's NSImage's alloc()'s initWithData:rawData
                set pb to current application's NSPasteboard's generalPasteboard()
                pb's clearContents()
                pb's writeObjects:{{theImage}}
                '''
                p = subprocess.run(["osascript", "-e", script], capture_output=True)
                return p.returncode == 0

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
        item = self.read_local_clipboard()
        if item and not self.is_hash_seen(item.hash):
            self.mark_hash_seen(item.hash)
            self.last_item = item
            for cb in self._callbacks:
                try:
                    cb(item)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
            return item
        return None
