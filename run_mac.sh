#!/usr/bin/env bash
# Universal Clipboard - run from source (development); end users install the .dmg from GitHub Releases

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

if [ ! -d "venv" ]; then
    echo "[1/2] Vytvarim venv..."
    python3 -m venv venv
fi
echo "[1/2] Kontroluji zavislosti..."
./venv/bin/pip install --quiet -r requirements.txt

echo "[2/2] Spoustim aplikaci ze zdrojaku (vyvojovy rezim)..."
./venv/bin/python main.py
