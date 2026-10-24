import asyncio
import logging
import os
import sys
import threading
import urllib.request
from logging.handlers import RotatingFileHandler

from app_paths import LOG_FILE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=2, encoding="utf-8")]
    + ([logging.StreamHandler()] if sys.stderr else []),  # windowed builds have no console
)

import webview  # noqa: E402

from server import DEFAULT_PORT, start_server  # noqa: E402
from tray_icon import setup_tray  # noqa: E402
from version import APP_NAME  # noqa: E402

logger = logging.getLogger("App")
APP_URL = f"http://127.0.0.1:{DEFAULT_PORT}"


def _ping_running_instance() -> bool:
    """Asks an already running instance to show its window; True if one answered."""
    try:
        req = urllib.request.Request(f"{APP_URL}/api/show", method="POST", data=b"")
        with urllib.request.urlopen(req, timeout=1.0):
            return True
    except Exception:
        return False


def _is_app_quitting() -> bool:
    # pywebview fires the same `closing` event for the window close button and for app quit
    # (Cmd+Q, Dock > Quit, logout); on macOS the latter arrives via applicationShouldTerminate_.
    frame = sys._getframe()
    while frame:
        if frame.f_code.co_name == "applicationShouldTerminate_":
            return True
        frame = frame.f_back
    return False


def main():
    if _ping_running_instance():
        return

    window = webview.create_window(
        APP_NAME, APP_URL, width=1320, height=880, min_size=(900, 640),
        hidden="--hidden" in sys.argv,  # autostart at login goes straight to the tray
        background_color="#080A0F",
    )

    def show_window():
        window.show()
        window.restore()

    def quit_app():
        logger.info("Quitting from tray")
        os._exit(0)

    def on_closing():
        if sys.platform == "darwin":
            if _is_app_quitting():
                return True
            # A minimized window comes back when the Dock icon is clicked; a hidden one would not
            threading.Thread(target=window.minimize, daemon=True).start()
        else:
            threading.Thread(target=window.hide, daemon=True).start()
        return False  # keep syncing in the background

    window.events.closing += on_closing

    ready = threading.Event()
    threading.Thread(
        target=lambda: asyncio.run(start_server(DEFAULT_PORT, on_show=show_window, on_ready=ready.set)),
        daemon=True,
    ).start()
    if not ready.wait(15):
        logger.error(f"Server did not start on port {DEFAULT_PORT}")

    setup_tray(on_open=show_window, on_quit=quit_app)
    webview.start()
    os._exit(0)


if __name__ == "__main__":
    main()
