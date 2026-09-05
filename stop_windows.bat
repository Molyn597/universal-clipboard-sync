@echo off
title Zastaveni Universal Clipboard
cd /d "%~dp0"

echo ========================================================
echo   Zastavuji Universal Clipboard Server...
echo ========================================================
echo.

:: 1. Pokus o korektni ukonceni pres HTTP API
echo [1/2] Odesilam pozadavek na ukonceni serveru...
curl -s -X POST http://localhost:7890/api/shutdown >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Prikaz k ukonceni byl uspesne dorucen.
    timeout /t 1 /nobreak >nul
)

:: 2. Jistota ukonceni procesu na portu 7890 (pokud by stale bezel)
echo [2/2] Kontroluji stav portu 7890...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":7890" ^| findstr "LISTENING"') do (
    echo [INFO] Ukoncuji zbyvajici proces (PID: %%a)...
    taskkill /f /pid %%a >nul 2>nul
)

echo.
echo ========================================================
echo   [HOTOVO] Synchronizacni server byl uspesne zastaven.
echo ========================================================
echo.
timeout /t 2 >nul
