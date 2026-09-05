@echo off
set "SCRIPT_DIR=%~dp0"
set "TARGET_BAT=%SCRIPT_DIR%Universal Clipboard.bat"
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
set "ICON_PATH=%SCRIPT_DIR%assets\icon.ico"

echo Vytvarim styloveho zastupce na plose s vlastni ikonou...

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP_DIR%\Universal Clipboard.lnk'); $s.TargetPath = '%TARGET_BAT%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.WindowStyle = 7; if (Test-Path '%ICON_PATH%') { $s.IconLocation = '%ICON_PATH%' } else { $s.IconLocation = 'shell32.dll,260' }; $s.Save()"

echo.
echo [✓] Zastupce 'Universal Clipboard' s novou moderni ikonou byl uspesne vytvoren na plose!
echo.
pause
