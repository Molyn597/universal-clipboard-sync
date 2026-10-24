import asyncio
import json
import logging
import os
import subprocess
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


def _set_paused(paused: bool):
    """Goes through the local API so the dashboard and saved settings stay in sync."""
    req = urllib.request.Request(
        f"{APP_URL}/api/settings", method="POST", data=json.dumps({"paused": paused}).encode(),
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=2.0).close()


def _mac_notify(title: str, message: str):
    # Passed as argv so titles/messages can never break out of the AppleScript string
    subprocess.Popen([
        "osascript", "-e", "on run argv", "-e", "display notification (item 2 of argv) with title (item 1 of argv)",
        "-e", "end run", title, message,
    ])


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
    state = {}

    def on_ready(server):
        state["server"] = server
        ready.set()

    def notify(title: str, message: str):
        if sys.platform == "darwin":
            _mac_notify(title, message)
        elif state.get("tray"):
            state["tray"].notify(message, title)

    def is_paused() -> bool:
        return bool(state.get("server") and state["server"].store.settings["paused"])

    threading.Thread(
        target=lambda: asyncio.run(start_server(DEFAULT_PORT, on_show=show_window, on_ready=on_ready, notifier=notify)),
        daemon=True,
    ).start()
    if not ready.wait(15):
        logger.error(f"Server did not start on port {DEFAULT_PORT}")

    state["tray"] = setup_tray(on_open=show_window, on_quit=quit_app,
                               is_paused=is_paused, on_toggle_pause=lambda: _set_paused(not is_paused()))
    webview.start()
    os._exit(0)


if __name__ == "__main__":
    main()
