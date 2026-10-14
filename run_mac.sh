#!/usr/bin/env bash
# Universal Clipboard Sync (macOS Node)

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "========================================================"
echo "  Universal Clipboard Sync (macOS Node)"
echo "========================================================"
echo ""

echo "[1/2] Kontroluji závislosti..."
pip3 install --quiet aiohttp Pillow cryptography 2>/dev/null || pip install --quiet aiohttp Pillow cryptography

echo "[2/2] Spouštím synchronizační službu..."
echo ""
echo "========================================================"
echo "  Dashboard UI: http://localhost:7890"
echo "========================================================"
echo ""

URL="http://localhost:7890"

# Spuštění okna v režimu aplikace
if [ -d "/Applications/Google Chrome.app" ]; then
    open -na "Google Chrome" --args --app="$URL" --window-size=1280,850 &
elif [ -d "/Applications/Brave Browser.app" ]; then
    open -na "Brave Browser" --args --app="$URL" --window-size=1280,850 &
elif [ -d "/Applications/Microsoft Edge.app" ]; then
    open -na "Microsoft Edge" --args --app="$URL" --window-size=1280,850 &
else
    open "$URL" &
fi

python3 server.py 7890 || python server.py 7890
