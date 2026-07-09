; Script de Inno Setup para generar el instalador autoejecutable de CellSite.
; Se compila en el workflow de GitHub Actions (build-windows-installer.yml)
; sobre el resultado de PyInstaller en dist\CellSite\
;
; Compilacion manual (Windows, con Inno Setup instalado):
;   ISCC.exe /DMyAppVersion=1.0.0 installer.iss

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0-dev"
#endif

#define MyAppName "CellSite"
#define MyAppPublisher "CellSite"
#define MyAppExeName "CellSite.exe"

[Setup]
AppId={{B4C1D9E2-3F5A-4C8B-9D6E-1A2B3C4D5E6F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
; Instala en una carpeta del usuario actual: no requiere permisos de administrador
; y garantiza que la app pueda escribir su carpeta data/ sin problemas de permisos.
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=installer_output
OutputBaseFilename=CellSite_Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}
DisableWelcomePage=no
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el Escritorio"; GroupDescription: "Accesos directos adicionales:"; Flags: unchecked

[Files]
; Copia todo el contenido generado por PyInstaller (onedir) tal cual.
Source: "dist\CellSite\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName} ahora"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Al desinstalar se conserva la carpeta data\ con la base de datos del usuario
; salvo que la borre manualmente; solo se limpian los binarios de la app.
Type: filesandordirs; Name: "{app}\__pycache__"
