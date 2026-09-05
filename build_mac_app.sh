#!/usr/bin/env bash
# ==============================================================================
# Universal Clipboard - Native Apple Silicon (ARM64) Application Builder
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

APP_NAME="Universal Clipboard.app"
DEST_APP="/Applications/$APP_NAME"

echo "========================================================"
echo "  Vytvářím 100% nativní aplikaci pro Apple Silicon (ARM64)"
echo "========================================================"
echo ""

# 1. Odstranění staré verze
rm -rf "$APP_NAME"
if [ -d "$DEST_APP" ]; then
    rm -rf "$DEST_APP"
fi

# 2. Vytvoření nativní AppleScript aplikace přes osacompile (Nativní ARM64, bez nutnosti Rosetta!)
TMP_SCRIPT="$DIR/launcher.applescript"

cat << EOF > "$TMP_SCRIPT"
set projectPath to "$DIR"

-- 1. Kontrola a spusteni Python serveru na pozadi
try
    do shell script "cd " & quoted form of projectPath & " && (curl -s -m 1 http://127.0.0.1:7890/api/status >/dev/null 2>&1 || (nohup python3 server.py 7890 >/dev/null 2>&1 &))"
end try

delay 0.8

-- 2. Otevreni v samostatnem okne aplikace
try
    do shell script "
    URL='http://localhost:7890'
    if [ -d '/Applications/Google Chrome.app' ]; then
        open -na 'Google Chrome' --args --app=\$URL --window-size=1280,850
    elif [ -d '/Applications/Brave Browser.app' ]; then
        open -na 'Brave Browser' --args --app=\$URL --window-size=1280,850
    elif [ -d '/Applications/Microsoft Edge.app' ]; then
        open -na 'Microsoft Edge' --args --app=\$URL --window-size=1280,850
    else
        open \$URL
    fi
    "
end try
EOF

echo "[1/3] Kompiluji nativní Apple Silicon aplikaci..."
osacompile -o "$APP_NAME" "$TMP_SCRIPT"
rm -f "$TMP_SCRIPT"

# 3. Nastavení ikony pro Mac aplikaci
if [ -f "$DIR/assets/icon.png" ]; then
    echo "[2/3] Generuji Apple Retina ikonu..."
    ICONSET_DIR="$DIR/temp.iconset"
    mkdir -p "$ICONSET_DIR"
    sips -z 16 16     "$DIR/assets/icon.png" --out "$ICONSET_DIR/icon_16x16.png" >/dev/null 2>&1 || true
    sips -z 32 32     "$DIR/assets/icon.png" --out "$ICONSET_DIR/icon_16x16@2x.png" >/dev/null 2>&1 || true
    sips -z 32 32     "$DIR/assets/icon.png" --out "$ICONSET_DIR/icon_32x32.png" >/dev/null 2>&1 || true
    sips -z 64 64     "$DIR/assets/icon.png" --out "$ICONSET_DIR/icon_32x32@2x.png" >/dev/null 2>&1 || true
    sips -z 128 128   "$DIR/assets/icon.png" --out "$ICONSET_DIR/icon_128x128.png" >/dev/null 2>&1 || true
    sips -z 256 256   "$DIR/assets/icon.png" --out "$ICONSET_DIR/icon_128x128@2x.png" >/dev/null 2>&1 || true
    sips -z 512 512   "$DIR/assets/icon.png" --out "$ICONSET_DIR/icon_512x512.png" >/dev/null 2>&1 || true
    sips -z 1024 1024 "$DIR/assets/icon.png" --out "$ICONSET_DIR/icon_512x512@2x.png" >/dev/null 2>&1 || true

    iconutil -c icns "$ICONSET_DIR" -o "$APP_NAME/Contents/Resources/applet.icns" >/dev/null 2>&1 || true
    rm -rf "$ICONSET_DIR"
fi

# 4. Instalace do /Applications
echo "[3/3] Instaluji do složky /Applications..."
cp -R "$APP_NAME" "/Applications/$APP_NAME" 2>/dev/null || cp -R "$APP_NAME" "$HOME/Applications/$APP_NAME" 2>/dev/null || true

echo ""
echo "========================================================"
echo "  [✓] HOTOVO! Aplikace je plně nativní pro Apple Silicon"
echo "  Najdeš ji v /Applications/Universal Clipboard.app"
echo "========================================================"
