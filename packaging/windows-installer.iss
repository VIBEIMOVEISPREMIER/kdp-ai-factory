; KDP AI Factory Windows installer
#define AppName "KDP AI Factory"
#define AppVersion "1.1.1"
#define AppExeName "KDP-AI-Factory-Windows.exe"

[Setup]
AppId={{A9D7F6B8-6A2D-4C9E-9E6C-1234567890AB}}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\KDP AI Factory
DefaultGroupName=KDP AI Factory
OutputDir=..\dist\installer
OutputBaseFilename=KDP-AI-Factory-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#AppExeName}

[Files]
Source: "..\dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\KDP AI Factory"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\KDP AI Factory"; Filename: "{app}\{#AppExeName}"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Abrir KDP AI Factory"; Flags: nowait postinstall skipifsilent
