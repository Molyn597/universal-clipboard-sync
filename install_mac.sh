#!/usr/bin/env bash
# Installs the latest Universal Clipboard release into /Applications.
# Usage: curl -fsSL https://raw.githubusercontent.com/Molyn597/universal-clipboard-sync/main/install_mac.sh | bash
#
# Downloading with curl (unlike a browser) does not set the quarantine flag, so Gatekeeper
# does not block the unsigned app on first launch.
set -euo pipefail

REPO="Molyn597/universal-clipboard-sync"
APP="Universal Clipboard.app"
DEST="/Applications/$APP"

echo "==> Hledam nejnovejsi verzi..."
DMG_URL=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" \
    | grep -o '"browser_download_url": *"[^"]*-macOS\.dmg"' \
    | sed 's/.*"\(https[^"]*\)"/\1/')
if [ -z "$DMG_URL" ]; then
    echo "Chyba: v poslednim releasu jsem nenasel .dmg pro macOS." >&2
    exit 1
fi

TMP=$(mktemp -d)
MNT="$TMP/mnt"
cleanup() {
    hdiutil detach "$MNT" -quiet 2>/dev/null || true
    rm -rf "$TMP"
}
trap cleanup EXIT

echo "==> Stahuji $(basename "$DMG_URL")..."
curl -fL --progress-bar "$DMG_URL" -o "$TMP/app.dmg"

echo "==> Instaluji do /Applications..."
osascript -e 'quit app "Universal Clipboard"' 2>/dev/null || true
sleep 1
mkdir -p "$MNT"
hdiutil attach -nobrowse -readonly -mountpoint "$MNT" "$TMP/app.dmg" -quiet
rm -rf "$DEST"
ditto "$MNT/$APP" "$DEST"
xattr -dr com.apple.quarantine "$DEST" 2>/dev/null || true

echo "==> Hotovo, spoustim Universal Clipboard."
open "$DEST"
