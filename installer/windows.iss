; Build: iscc /DAppVersion=1.0.0 installer\windows.iss  (after pyinstaller)
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#define AppName "Universal Clipboard"
#define AppExe "Universal Clipboard.exe"

[Setup]
; Never change AppId - updates and uninstall are matched by it
AppId={{6E2B9A41-3C7D-4F58-9B1E-2D4A7C8F0E13}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Molyn597
AppPublisherURL=https://github.com/Molyn597/universal-clipboard-sync
DefaultDirName={localappdata}\Programs\{#AppName}
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist
OutputBaseFilename=Universal-Clipboard-Setup-{#AppVersion}
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#AppExe}
WizardStyle=modern
Compression=lzma2
SolidCompression=yes
CloseApplications=force
RestartApplications=no
; Makes Explorer drop cached icons after install, so a changed app icon shows up right away
ChangesAssociations=yes

[Languages]
Name: "czech"; MessagesFile: "compiler:Languages\Czech.isl"

[Tasks]
Name: "autostart"; Description: "Spouštět automaticky po přihlášení (doporučeno)"; GroupDescription: "Další možnosti:"
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[InstallDelete]
; Drop libraries from the previous version so stale files never mix with the new build
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "..\dist\{#AppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Icon from the bundled .ico rather than the exe: Explorer caches icons per file path, and the exe path
; never changes between versions, so a new icon inside the exe would keep showing the old cached one
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"; IconFilename: "{app}\_internal\assets\icon.ico"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; IconFilename: "{app}\_internal\assets\icon.ico"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#AppName}"; ValueData: """{app}\{#AppExe}"" --hidden"; Flags: uninsdeletevalue; Tasks: autostart

[Run]
; No skipifsilent: the in-app updater runs this installer with /VERYSILENT and relies on it relaunching the app
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall

[UninstallRun]
Filename: "{sys}\taskkill.exe"; Parameters: "/IM ""{#AppExe}"" /F"; Flags: runhidden; RunOnceId: "StopApp"
