import logging
import sys
from typing import Callable

from PIL import Image

from app_paths import resource
from version import APP_NAME

try:
    import pystray
except ImportError:
    pystray = None

logger = logging.getLogger("Tray")


def setup_tray(on_open: Callable[[], None], on_quit: Callable[[], None]):
    """System tray icon (Windows only); on macOS the Dock icon plays this role and
    pystray would fight pywebview for the Cocoa main thread."""
    if sys.platform != "win32" or not pystray:
        return None
    try:
        menu = pystray.Menu(
            pystray.MenuItem("Otevřít Universal Clipboard", lambda icon, item: on_open(), default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Ukončit", lambda icon, item: (icon.stop(), on_quit())),
        )
        tray = pystray.Icon("universal_clipboard", Image.open(resource("assets", "icon.png")), APP_NAME, menu)
        tray.run_detached()
        return tray
    except Exception as e:
        logger.warning(f"Failed to start tray icon: {e}")
        return None
