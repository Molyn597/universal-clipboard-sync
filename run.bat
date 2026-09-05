@echo off
title Universal Clipboard Sync (Windows Node)
cd /d "%~dp0"

echo ========================================================
echo   Universal Clipboard Sync (Windows Node)
echo ========================================================
echo.

if exist "venv\Scripts\python.exe" (
    echo [1/2] Pouzivam dedikovany venv...
    set "PY_EXE=venv\Scripts\python.exe"
) else (
    echo [1/2] Hledam Python...
    set "PY_EXE=python"
)

echo [2/2] Spoustim synchronizacni server...
echo.
echo ========================================================
echo  Dashboard UI: http://localhost:7890
echo ========================================================
echo.

start http://localhost:7890
"%PY_EXE%" server.py 7890

if %errorlevel% neq 0 (
    echo.
    echo Doslo k chybe.
    pause
)
