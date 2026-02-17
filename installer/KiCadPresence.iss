; Inno Setup script for KiCad Discord Presence

#ifndef MyAppVersion
#define MyAppVersion "1.0.0"
#endif

[Setup]
AppId={{7F98F95B-CC17-4A73-8A4A-EA2344E65AB9}}
AppName=KiCad Discord Presence
AppVersion={#MyAppVersion}
AppPublisher=KiCad Presence
DefaultDirName={localappdata}\KiCadPresence
DefaultGroupName=KiCad Discord Presence
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist\installer
OutputBaseFilename=KiCadDiscordPresence-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\KiCadPresence.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\KiCadPresence.exe"; DestDir: "{app}"; DestName: "KiCadPresence.exe"; Flags: ignoreversion

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "KiCadPresence"; ValueData: """{app}\KiCadPresence.exe"""; Flags: uninsdeletevalue

[Icons]
Name: "{autoprograms}\KiCad Discord Presence"; Filename: "{app}\KiCadPresence.exe"

[Run]
Filename: "{app}\KiCadPresence.exe"; Description: "Launch KiCad Discord Presence"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
