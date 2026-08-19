[Setup]
AppId={A7612FC8-2F53-45AB-A3CF-GCOMENGINE001}
AppName=GCOM Engine
AppVersion=1.0.1
AppPublisher=GCOM
DefaultDirName={localappdata}\Programs\GCOM Engine
DefaultGroupName=GCOM Engine
OutputDir=installer
OutputBaseFilename=GCOM_Engine_Setup_v1.0.1
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=assets\gcom_engine.ico
UninstallDisplayIcon={app}\GCOM Engine.exe
PrivilegesRequired=lowest
CloseApplications=yes
RestartApplications=no

[Files]
Source: "dist\GCOM Engine.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "credentials\google_oauth_client.json"; DestDir: "{app}\credentials"; Flags: ignoreversion
Source: "pw-browsers\*"; DestDir: "{app}\pw-browsers"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\credentials"
Name: "{app}\data"
Name: "{app}\data\database"
Name: "{app}\data\sessions"
Name: "{app}\logs"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"

[Icons]
Name: "{group}\GCOM Engine"; Filename: "{app}\GCOM Engine.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\GCOM Engine"; Filename: "{app}\GCOM Engine.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\GCOM Engine.exe"; Description: "Abrir GCOM Engine"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent
