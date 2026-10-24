import hashlib
import json
import logging
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Callable, Optional

from app_paths import IS_FROZEN
from version import APP_NAME, GITHUB_REPO, __version__

logger = logging.getLogger("Updater")

LATEST_RELEASE_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
CHECKSUMS_ASSET = "checksums.txt"
HTTP_HEADERS = {"User-Agent": f"{APP_NAME}/{__version__}", "Accept": "application/vnd.github+json"}

# Swaps the .app bundle once this process has exited, rolling back if the copy fails
MAC_INSTALL_SCRIPT = """
pid="$1"; dmg="$2"; app="$3"
mnt="$(mktemp -d)"
hdiutil attach -nobrowse -readonly -mountpoint "$mnt" "$dmg" || exit 1
while kill -0 "$pid" 2>/dev/null; do sleep 0.2; done
rm -rf "$app.old"
mv "$app" "$app.old"
if ditto "$mnt/{app_name}.app" "$app"; then rm -rf "$app.old"; else rm -rf "$app"; mv "$app.old" "$app"; fi
hdiutil detach "$mnt" -quiet
rm -f "$dmg"
open "$app"
""".replace("{app_name}", APP_NAME)


def parse_version(version: str) -> tuple:
    try:
        return tuple(int(part) for part in version.strip().lstrip("v").split(".")[:3])
    except ValueError:
        return (0,)


def installer_asset_name(version: str) -> Optional[str]:
    if sys.platform == "win32":
        return f"Universal-Clipboard-Setup-{version}.exe"
    if sys.platform == "darwin":
        return f"Universal-Clipboard-{version}-macOS.dmg"
    return None


def _http_get(url: str, timeout: float = 15.0):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HTTP_HEADERS), timeout=timeout)


class Updater:
    def __init__(self):
        self.latest: Optional[dict] = None
        self.state = "idle"  # idle | checking | downloading | installing | error
        self.progress = 0.0
        self.error: Optional[str] = None

    def status(self) -> dict:
        latest_version = self.latest["version"] if self.latest else None
        available = bool(latest_version) and parse_version(latest_version) > parse_version(__version__)
        asset = installer_asset_name(latest_version) if latest_version else None
        return {
            "current": __version__,
            "latest": latest_version,
            "available": available,
            # Running from source there is no installed bundle to replace; the UI links to the release instead
            "can_install": available and IS_FROZEN and bool(asset) and asset in self.latest["assets"],
            "release_url": self.latest["url"] if self.latest else f"https://github.com/{GITHUB_REPO}/releases",
            "state": self.state,
            "progress": round(self.progress, 3),
            "error": self.error,
        }

    def check(self) -> dict:
        try:
            with _http_get(LATEST_RELEASE_API) as resp:
                release = json.load(resp)
            self.latest = {
                "version": release["tag_name"].lstrip("v"),
                "url": release["html_url"],
                "assets": {a["name"]: a["browser_download_url"] for a in release.get("assets", [])},
            }
            if self.state == "error":
                self.state, self.error = "idle", None
        except Exception as e:
            logger.info(f"Update check failed: {e}")
        return self.status()

    def _expected_sha256(self, asset: str) -> str:
        with _http_get(self.latest["assets"][CHECKSUMS_ASSET]) as resp:
            for line in resp.read().decode("utf-8").splitlines():
                parts = line.split()
                if len(parts) == 2 and parts[1].lstrip("*") == asset:
                    return parts[0].lower()
        raise RuntimeError(f"{asset} missing from {CHECKSUMS_ASSET}")

    def _download(self, url: str, target: Path, on_progress: Callable[[dict], None]):
        with _http_get(url, timeout=60.0) as resp, open(target, "wb") as out:
            total = int(resp.headers.get("Content-Length") or 0)
            done = 0
            for chunk in iter(lambda: resp.read(1 << 16), b""):
                out.write(chunk)
                done += len(chunk)
                if total:
                    new_progress = done / total
                    if new_progress - self.progress >= 0.02 or done == total:
                        self.progress = new_progress
                        on_progress(self.status())

    def download_and_launch_installer(self, on_progress: Callable[[dict], None]) -> bool:
        """Downloads and verifies the installer, then hands over to it. The caller must exit
        the app right after a True return so the installer can replace the running files."""
        if not self.status()["can_install"]:
            return False
        asset = installer_asset_name(self.latest["version"])
        try:
            self.state, self.progress, self.error = "downloading", 0.0, None
            on_progress(self.status())
            expected = self._expected_sha256(asset)
            target = Path(tempfile.mkdtemp(prefix="uclip-update-")) / asset
            self._download(self.latest["assets"][asset], target, on_progress)

            digest = hashlib.sha256()
            with open(target, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    digest.update(chunk)
            if digest.hexdigest() != expected:
                target.unlink(missing_ok=True)
                raise RuntimeError("Downloaded update failed the SHA-256 check")

            self.state = "installing"
            on_progress(self.status())
            if sys.platform == "win32":
                subprocess.Popen(
                    [str(target), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"],
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                    close_fds=True,
                )
            else:
                app_bundle = Path(sys.executable).resolve().parents[2]  # .../X.app/Contents/MacOS/<exe>
                subprocess.Popen(
                    ["/bin/bash", "-c", MAC_INSTALL_SCRIPT, "install", str(os.getpid()), str(target), str(app_bundle)],
                    start_new_session=True,
                    close_fds=True,
                )
            return True
        except Exception as e:
            logger.error(f"Update failed: {e}")
            self.state, self.error = "error", str(e)
            on_progress(self.status())
            return False
