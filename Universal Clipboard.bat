@echo off
cd /d "%~dp0"

:: 1. Start hidden Python background daemon
start "" "%~dp0venv\Scripts\pythonw.exe" "%~dp0server.py" 7890

:: 2. Wait 1 second for port to be ready
timeout /t 1 /nobreak >nul

:: 3. Launch dedicated standalone App window (Edge or Chrome)
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" --app=http://localhost:7890 --window-size=1300,860
) else if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" --app=http://localhost:7890 --window-size=1300,860
) else if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" --app=http://localhost:7890 --window-size=1300,860
) else (
    start http://localhost:7890
)

exit
