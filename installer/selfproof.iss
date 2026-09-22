; Inno Setup script for the Selfproof Windows installer.
; Produces installer/Output/Selfproof_Setup.exe from the PyInstaller binary.
; Build (needs Inno Setup 6 and dist/selfproof-windows.exe):
;   iscc /DAppVersion=0.1.1 installer/selfproof.iss
; CI passes the version from the git tag.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppName=Selfproof
AppVersion={#AppVersion}
AppPublisher=Renker Industries
DefaultDirName={autopf}\Selfproof
DefaultGroupName=Selfproof
DisableProgramGroupPage=yes
OutputDir=installer\Output
OutputBaseFilename=Selfproof_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
ChangesEnvironment=yes
UninstallDisplayName=Selfproof

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"
Name: "addtopath"; Description: "Add Selfproof to my PATH"; GroupDescription: "Command line:"

[Files]
Source: "..\dist\selfproof-windows.exe"; DestDir: "{app}"; DestName: "selfproof.exe"; Flags: ignoreversion

[Icons]
Name: "{group}\Selfproof"; Filename: "{app}\selfproof.exe"
Name: "{group}\Uninstall Selfproof"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Selfproof"; Filename: "{app}\selfproof.exe"; Tasks: desktopicon

[Registry]
; Append the install dir to the user PATH when the task is selected.
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; \
  ValueData: "{olddata};{app}"; Tasks: addtopath; Check: NeedsAddPath('{app}')

[Run]
Filename: "{app}\selfproof.exe"; Description: "Launch Selfproof (opens the dashboard)"; \
  Flags: nowait postinstall skipifsilent

[Code]
function NeedsAddPath(Param: string): Boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + ExpandConstant(Param) + ';', ';' + OrigPath + ';') = 0;
end;
