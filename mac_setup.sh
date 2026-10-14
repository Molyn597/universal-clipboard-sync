#!/bin/bash
set -e

cd "$HOME/AI_Workspace/clipboard_sync"

# 1. Oprava tray_icon pro Mac
cat << 'EOF' > tray_icon.py
import os

def setup_tray(on_quit_callback=None):
    return None

def open_dashboard():
    os.system("open http://localhost:7890")
EOF

# 2. Vytvoreni venv a instalace balicku
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
./venv/bin/pip install --quiet aiohttp Pillow cryptography

# 3. Kompilace nativni Apple Silicon aplikace
osacompile -o "/Applications/Universal Clipboard.app" -e 'set p to POSIX path of (path to home folder) & "AI_Workspace/clipboard_sync"
do shell script "cd " & quoted form of p & " && (curl -s -m 1 http://127.0.0.1:7890/api/status >/dev/null 2>&1 || nohup ./venv/bin/python server.py 7890 >/dev/null 2>&1 &)"
delay 0.8
do shell script "open http://localhost:7890"'

# 4. Ikona
if [ -f "assets/icon.png" ]; then
    rm -rf temp_icon.iconset
    mkdir -p temp_icon.iconset
    sips -z 128 128 assets/icon.png --out temp_icon.iconset/icon_128x128.png >/dev/null 2>&1 || true
    sips -z 256 256 assets/icon.png --out temp_icon.iconset/icon_256x256.png >/dev/null 2>&1 || true
    iconutil -c icns temp_icon.iconset -o "/Applications/Universal Clipboard.app/Contents/Resources/applet.icns" >/dev/null 2>&1 || true
    rm -rf temp_icon.iconset
    touch "/Applications/Universal Clipboard.app"
fi

echo "========================================================"
echo "  [OK] Hotovo! Aplikace je pripravena v /Applications"
echo "========================================================"
