import base64
import io
import logging
import os
from typing import Any, Dict, List, Optional

from PIL import Image

try:
    import pypdfium2 as pdfium
except ImportError:
    pdfium = None

logger = logging.getLogger("Previews")

THUMB_MAX = (480, 360)
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tif", ".tiff", ".heic"}
TEXT_EXTS = {".txt", ".md", ".csv", ".json", ".log", ".py", ".js", ".ts", ".html", ".css", ".xml", ".yml", ".yaml",
             ".ini", ".toml", ".sql", ".sh", ".bat", ".ps1"}
KIND_BY_EXT = {
    **{e: "doc" for e in (".doc", ".docx", ".odt", ".rtf", ".pages")},
    **{e: "sheet" for e in (".xls", ".xlsx", ".ods", ".numbers")},
    **{e: "slides" for e in (".ppt", ".pptx", ".odp", ".key")},
    **{e: "archive" for e in (".zip", ".rar", ".7z", ".tar", ".gz", ".dmg")},
    **{e: "audio" for e in (".mp3", ".wav", ".flac", ".m4a", ".ogg")},
    **{e: "video" for e in (".mp4", ".mov", ".mkv", ".avi", ".webm")},
}
SNIPPET_CHARS = 600
MAX_PDF_PAGES = 60  # the in-app viewer renders at most this many pages


def file_kind(path: str) -> str:
    if os.path.isdir(path):
        return "folder"
    ext = os.path.splitext(path)[1].lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext == ".pdf":
        return "pdf"
    if ext in TEXT_EXTS:
        return "text"
    return KIND_BY_EXT.get(ext, "file")


def pdf_page_count(path: str) -> int:
    if not pdfium:
        return 0
    pdf = pdfium.PdfDocument(path)
    try:
        return len(pdf)
    finally:
        pdf.close()


def pdf_page_png(path: str, index: int, width: int = 1100) -> bytes:
    pdf = pdfium.PdfDocument(path)
    try:
        page = pdf[index]
        image = page.render(scale=width / max(page.get_width(), 1)).to_pil()
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()
    finally:
        pdf.close()


def thumbnail_png(path: str) -> Optional[bytes]:
    """Small PNG for the file browser grid; None when the file type has no visual preview."""
    preview = file_preview([path])
    if not preview or not preview.get("thumb"):
        return None
    return base64.b64decode(preview["thumb"])


def _encode(img: Image.Image) -> str:
    img = img.copy()
    img.thumbnail(THUMB_MAX)
    buf = io.BytesIO()
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def image_thumbnail(b64_png: str) -> str:
    try:
        return _encode(Image.open(io.BytesIO(base64.b64decode(b64_png))))
    except Exception:
        return ""


def _pdf_preview(path: str) -> Dict[str, Any]:
    if not pdfium:
        return {"kind": "pdf"}
    pdf = pdfium.PdfDocument(path)
    try:
        page = pdf[0]
        bitmap = page.render(scale=480 / max(page.get_width(), 1))
        return {"kind": "pdf", "thumb": _encode(bitmap.to_pil()), "pages": len(pdf)}
    finally:
        pdf.close()


def file_preview(paths: List[str]) -> Optional[Dict[str, Any]]:
    """Describes how the first copied file looks: an image/PDF thumbnail, a text snippet or just its kind."""
    if not paths:
        return None
    path = paths[0]
    if os.path.isdir(path):
        return {"kind": "folder"}
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in IMAGE_EXTS:
            with Image.open(path) as img:
                return {"kind": "image", "thumb": _encode(img), "width": img.width, "height": img.height}
        if ext == ".pdf":
            return _pdf_preview(path)
        if ext in TEXT_EXTS:
            with open(path, encoding="utf-8", errors="replace") as fh:
                return {"kind": "text", "snippet": fh.read(SNIPPET_CHARS)}
    except Exception as e:
        logger.debug(f"Preview of {path} failed: {e}")
    return {"kind": KIND_BY_EXT.get(ext, "file")}
