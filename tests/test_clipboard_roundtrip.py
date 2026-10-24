"""Round-trips text, images and files through the real OS clipboard.
Runs in the release workflow on macOS so clipboard code is exercised on a real Mac before shipping."""
import base64
import io
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import clipboard_engine as ce  # noqa: E402
from clipboard_engine import ClipboardEngine, ClipboardItem, file_item_from_paths, hash_paths, pack_files, unpack_files  # noqa: E402


def test_text_round_trip():
    engine = ClipboardEngine()
    item = ClipboardItem("text", "Příliš žluťoučký kůň\nřádek 2")
    assert engine.write_local_clipboard(item)
    assert engine.poll_clipboard() is None, "own write must not be re-detected"
    assert engine.read_local_clipboard().hash == item.hash


def test_image_round_trip():
    engine = ClipboardEngine()
    buf = io.BytesIO()
    Image.new("RGB", (40, 30), (200, 10, 50)).save(buf, "PNG")
    item = ClipboardItem("image", base64.b64encode(buf.getvalue()).decode())
    assert engine.write_local_clipboard(item)
    back = engine.read_local_clipboard()
    assert back is not None and back.item_type == "image"
    assert back.hash == item.hash


def test_files_round_trip(tmp_path):
    engine = ClipboardEngine()
    (tmp_path / "doc.txt").write_text("hello")
    (tmp_path / "folder").mkdir()
    (tmp_path / "folder" / "a.txt").write_text("nested")
    paths = [str(tmp_path / "doc.txt"), str(tmp_path / "folder")]

    assert engine.write_local_clipboard(file_item_from_paths(paths))
    back = engine.read_local_clipboard()
    assert back is not None and back.item_type == "file", f"expected files, got {back and back.item_type}"
    assert [Path(p).resolve() for p in back.data.splitlines()] == [Path(p).resolve() for p in paths]


def test_detects_user_copy_after_own_write():
    engine = ClipboardEngine()
    engine.write_local_clipboard(ClipboardItem("text", "ours"))
    engine._write_text_native("copied by the user")
    detected = engine.poll_clipboard()
    assert detected is not None and detected.data == "copied by the user"


def test_received_files_keep_hash(tmp_path):
    src = tmp_path / "src"
    (src / "folder").mkdir(parents=True)
    (src / "doc.txt").write_text("hello")
    (src / "folder" / "b.txt").write_text("nested")
    paths = [str(src / "doc.txt"), str(src / "folder")]
    saved = unpack_files(pack_files(paths), tmp_path / "received")
    assert hash_paths(saved) == hash_paths(paths)
    assert ce.MAX_FILE_SYNC_BYTES > 0
