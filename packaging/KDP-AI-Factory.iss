; KDP AI Factory Windows installer

#define MyAppName "KDP AI Factory"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "KDP AI Factory"
#define MyAppExeName "KDP-AI-Factory.exe"

[Setup]
AppId={{C7F7B6F6-3B5E-4F2E-8B44-0E6B7A7D1E11}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\KDP AI Factory
DefaultGroupName=KDP AI Factory
DisableProgramGroupPage=yes
OutputDir=..\release
OutputBaseFilename=KDP-AI-Factory-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoDescription=KDP AI Factory local AI publishing factory
VersionInfoProductName=KDP AI Factory
VersionInfoProductVersion={#MyAppVersion}
VersionInfoCompany=KDP AI Factory
VersionInfoCopyright=Open-source project
UsePreviousLanguage=yes
LanguageDetectionMethod=uilanguage
ShowLanguageDialog=yes

[Languages]
Name: "pt"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "fr"; MessagesFile: "compiler:Languages\French.isl"
Name: "de"; MessagesFile: "compiler:Languages\German.isl"

[CustomMessages]
pt.IncompatibleTitle=Modo de compatibilidade do KDP AI Factory
pt.IncompatibleRAM=Seu computador tem pouca memória para alguns recursos de IA local. O aplicativo pode continuar em Modo Compatibilidade, com os recursos pesados desativados.
pt.IncompatibleGPU=Sua placa de vídeo tem pouca memória de vídeo para geração local de imagens. Você pode continuar usando uma VPS GPU ou uma API externa.
pt.IncompatibleDisk=Há menos de 10 GB livres no disco do sistema. Libere espaço antes de instalar.
pt.IncompatibleGeneric=O computador está abaixo do perfil recomendado para IA local. Você pode continuar com recursos leves e conectar uma VPS GPU ou API externa.
pt.IncompatibleDetails=Mínimo para instalar: Windows 10/11 64 bits, 8 GB de RAM e 10 GB livres. Os recursos de IA local serão ajustados ao hardware.

en.IncompatibleTitle=KDP AI Factory compatibility mode
en.IncompatibleRAM=This computer has limited memory for some local AI features. The application can continue in Compatibility Mode with heavy features disabled.
en.IncompatibleGPU=The detected graphics adapter has limited video memory for local image generation. You can continue with a GPU VPS or an external image API.
en.IncompatibleDisk=There is less than 10 GB of free space on the system drive. Free some space before installing.
en.IncompatibleGeneric=This computer is below the recommended profile for local AI. You can continue in Compatibility Mode and connect a GPU VPS or external API.
en.IncompatibleDetails=Installation minimum: 64-bit Windows 10/11, 8 GB RAM and 10 GB free space. AI capabilities are adjusted automatically.

es.IncompatibleTitle=Ordenador no compatible con KDP AI Factory
es.IncompatibleRAM=Este ordenador tiene menos de 16 GB de RAM. KDP AI Factory ejecuta IA local y necesita memoria suficiente para trabajar con libros, modelos e imágenes de forma estable.
es.IncompatibleGPU=La tarjeta gráfica detectada tiene menos de 4 GB de memoria de vídeo. Este ordenador no cumple el perfil mínimo recomendado para generar imágenes localmente.
es.IncompatibleDisk=Hay menos de 40 GB de espacio libre en el disco del sistema. La instalación y los modelos locales necesitan espacio adicional.
es.IncompatibleGeneric=Este ordenador no cumple los requisitos mínimos de KDP AI Factory. La instalación se detuvo para evitar una experiencia inestable.
es.IncompatibleDetails=Mínimo para instalar: Windows 10/11 de 64 bits, 8 GB de RAM y 10 GB libres. Las funciones de IA se ajustan automáticamente.

fr.IncompatibleTitle=Ordinateur incompatible avec KDP AI Factory
fr.IncompatibleRAM=Cet ordinateur dispose de moins de 16 Go de RAM. KDP AI Factory exécute l'IA localement et a besoin de suffisamment de mémoire pour travailler avec les livres, modèles et images de manière stable.
fr.IncompatibleGPU=La carte graphique détectée dispose de moins de 4 Go de mémoire vidéo. Cet ordinateur ne répond pas au profil minimal recommandé pour la génération locale d'images.
fr.IncompatibleDisk=Il reste moins de 40 Go d'espace libre sur le disque système. L'installation et les modèles locaux nécessitent de l'espace supplémentaire.
fr.IncompatibleGeneric=Cet ordinateur ne répond pas aux exigences minimales de KDP AI Factory. L'installation a été interrompue pour éviter une expérience instable.
fr.IncompatibleDetails=Minimum d'installation : Windows 10/11 64 bits, 8 Go de RAM et 10 Go libres. Les fonctions d'IA sont adaptées automatiquement.

de.IncompatibleTitle=Computer nicht mit KDP AI Factory kompatibel
de.IncompatibleRAM=Dieser Computer verfügt über weniger als 16 GB RAM. KDP AI Factory führt KI lokal aus und benötigt ausreichend Arbeitsspeicher für Bücher, Modelle und Bilder.
de.IncompatibleGPU=Der erkannte Grafikadapter verfügt über weniger als 4 GB Videospeicher. Dieser Computer erfüllt nicht das empfohlene Mindestprofil für die lokale Bildgenerierung.
de.IncompatibleDisk=Auf dem Systemlaufwerk sind weniger als 40 GB frei. Installation und lokale Modelle benötigen zusätzlichen Speicherplatz.
de.IncompatibleGeneric=Dieser Computer erfüllt die Mindestanforderungen von KDP AI Factory nicht. Die Installation wurde abgebrochen, um eine instabile Nutzung zu vermeiden.
de.IncompatibleDetails=Installationsminimum: Windows 10/11 64 Bit, 8 GB RAM und 10 GB freier Speicher. KI-Funktionen werden automatisch angepasst.

[Files]
Source: "..\dist\KDP-AI-Factory.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\KDP AI Factory"; Filename: "{app}\KDP-AI-Factory.exe"
Name: "{autodesktop}\KDP AI Factory"; Filename: "{app}\KDP-AI-Factory.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; Flags: unchecked

[Run]
Filename: "{app}\KDP-AI-Factory.exe"; Description: "Iniciar KDP AI Factory"; Flags: nowait postinstall skipifsilent

[Code]
function RunHardwareCheck: Integer;
var
  ResultCode: Integer;
  Params: String;
  PS: String;
begin
  PS := ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe');
  Params :=
    '-NoProfile -ExecutionPolicy Bypass -Command "' +
    '$ram=(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB;' +
    '$disk=(Get-PSDrive -Name C).Free/1GB;' +
    '$gpus=Get-CimInstance Win32_VideoController;' +
    '$vram=($gpus | Measure-Object -Property AdapterRAM -Maximum).Maximum/1GB;' +
    'if($ram -lt 8){exit 10};' +
    'if($disk -lt 10){exit 12};' +
    'if($vram -gt 0 -and $vram -lt 2){exit 11};' +
    'exit 0"';
  if Exec(PS, Params, '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    Result := ResultCode
  else
    Result := 99;
end;

function InitializeSetup: Boolean;
var
  Code: Integer;
  Title: String;
  MessageText: String;
begin
  Code := RunHardwareCheck;
  Result := True;
  if Code = 0 then
    exit;

  Title := CustomMessage('IncompatibleTitle');

  if Code = 10 then
    MessageText := CustomMessage('IncompatibleRAM')
  else if Code = 11 then
    MessageText := CustomMessage('IncompatibleGPU')
  else if Code = 12 then
    MessageText := CustomMessage('IncompatibleDisk')
  else
    MessageText := CustomMessage('IncompatibleGeneric');

  MessageText := MessageText + #13#10#13#10 + CustomMessage('IncompatibleDetails');
  MsgBox(Title + #13#10#13#10 + MessageText, mbError, MB_OK);
  Result := False;
end;
