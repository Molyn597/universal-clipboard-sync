import os
import sys
import subprocess
from PIL import Image

try:
    import pystray
except ImportError:
    pystray = None

TRAY_ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")


def open_dashboard():
    """Opens the standalone app window."""
    url = "http://localhost:7890"
    if sys.platform == "win32":
        edge_paths = [
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        ]
        for p in edge_paths:
            if os.path.exists(p):
                subprocess.Popen([p, f"--app={url}", "--window-size=1300,860"])
                return
        os.system(f"start {url}")
    elif sys.platform == "darwin":
        os.system(f"open {url}")


def setup_tray(on_quit_callback=None):
    """Initializes and runs the System Tray icon (Windows only)."""
    # macOS Cocoa crashes if pystray runs on non-main thread; keep tray Windows-only
    if sys.platform != "win32":
        return None

    if not pystray or not os.path.exists(TRAY_ICON_PATH):
        return None

    try:
        icon_img = Image.open(TRAY_ICON_PATH)

        def on_open(icon, item):
            open_dashboard()

        def on_exit(icon, item):
            icon.stop()
            if on_quit_callback:
                on_quit_callback()
            else:
                os._exit(0)

        menu = pystray.Menu(
            pystray.MenuItem("📋 Otevřít Schránku", on_open, default=True),
            pystray.MenuItem("🟢 Stav: Aktivní P2P Sync", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Ukončit aplikaci", on_exit),
        )

        tray = pystray.Icon(
            "universal_clipboard",
            icon_img,
            "Universal Clipboard (Aktivní)",
            menu
        )

        tray.run_detached()
        return tray
    except Exception as e:
        print(f"Failed to start tray icon: {e}")
        return None
