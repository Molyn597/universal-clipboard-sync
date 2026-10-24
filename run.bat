@echo off
title Universal Clipboard Sync (Windows Node)
cd /d "%~dp0"

echo ========================================================
echo   Universal Clipboard Sync (Windows Node)
echo ========================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [1/2] Vytvarim venv a instaluji zavislosti...
    python -m venv venv
)
echo [1/2] Kontroluji zavislosti...
venv\Scripts\python.exe -m pip install --quiet -r requirements.txt
set "PY_EXE=venv\Scripts\python.exe"

echo [2/2] Spoustim aplikaci ze zdrojaku (vyvojovy rezim)...
echo.

"%PY_EXE%" main.py

if %errorlevel% neq 0 (
    echo.
    echo Doslo k chybe.
    pause
)
