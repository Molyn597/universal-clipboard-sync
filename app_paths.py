import os
import shutil
import sys
from pathlib import Path

from version import APP_NAME

IS_FROZEN = getattr(sys, "frozen", False)
SOURCE_DIR = Path(__file__).resolve().parent
# PyInstaller unpacks bundled data (static/, assets/) into sys._MEIPASS
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", SOURCE_DIR))


def _data_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / APP_NAME


# Lives outside the install folder so updates and reinstalls never touch the pairing key
DATA_DIR = _data_dir()
DATA_DIR.mkdir(parents=True, exist_ok=True)
KEY_FILE = DATA_DIR / "sync.key"
LOG_FILE = DATA_DIR / "universal-clipboard.log"

_legacy_key = SOURCE_DIR / "sync.key"
if not KEY_FILE.exists() and _legacy_key.exists():
    shutil.copy2(_legacy_key, KEY_FILE)


def resource(*parts: str) -> str:
    return str(RESOURCE_DIR.joinpath(*parts))
