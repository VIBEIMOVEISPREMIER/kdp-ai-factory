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
pt.IncompatibleTitle=Computador incompatível com o KDP AI Factory
pt.IncompatibleRAM=Seu computador tem menos de 16 GB de RAM. O KDP AI Factory usa IA local e precisa de memória suficiente para trabalhar com livros, modelos e imagens sem travar.
pt.IncompatibleGPU=Sua placa de vídeo tem menos de 4 GB de memória de vídeo. Para a geração local de imagens, este computador não atende ao perfil mínimo recomendado.
pt.IncompatibleDisk=Há menos de 40 GB livres no disco do sistema. A instalação e os modelos locais precisam de espaço adicional.
pt.IncompatibleGeneric=O computador não atende aos requisitos mínimos do KDP AI Factory. A instalação foi interrompida para evitar uma experiência instável.
pt.IncompatibleDetails=Requisitos mínimos recomendados: Windows 10/11 64 bits, 16 GB de RAM, GPU com pelo menos 4 GB de VRAM quando detectável e 40 GB livres.

en.IncompatibleTitle=Computer not compatible with KDP AI Factory
en.IncompatibleRAM=This computer has less than 16 GB of RAM. KDP AI Factory runs local AI and needs enough memory to work with books, models and images without becoming unstable.
en.IncompatibleGPU=The detected graphics adapter has less than 4 GB of video memory. This computer does not meet the recommended minimum profile for local image generation.
en.IncompatibleDisk=There is less than 40 GB of free space on the system drive. Installation and local models require additional space.
en.IncompatibleGeneric=This computer does not meet the minimum KDP AI Factory requirements. Installation was stopped to avoid an unstable experience.
en.IncompatibleDetails=Recommended minimum: 64-bit Windows 10/11, 16 GB RAM, GPU with at least 4 GB VRAM when detectable, and 40 GB free space.

es.IncompatibleTitle=Ordenador no compatible con KDP AI Factory
es.IncompatibleRAM=Este ordenador tiene menos de 16 GB de RAM. KDP AI Factory ejecuta IA local y necesita memoria suficiente para trabajar con libros, modelos e imágenes de forma estable.
es.IncompatibleGPU=La tarjeta gráfica detectada tiene menos de 4 GB de memoria de vídeo. Este ordenador no cumple el perfil mínimo recomendado para generar imágenes localmente.
es.IncompatibleDisk=Hay menos de 40 GB de espacio libre en el disco del sistema. La instalación y los modelos locales necesitan espacio adicional.
es.IncompatibleGeneric=Este ordenador no cumple los requisitos mínimos de KDP AI Factory. La instalación se detuvo para evitar una experiencia inestable.
es.IncompatibleDetails=Mínimo recomendado: Windows 10/11 de 64 bits, 16 GB de RAM, GPU con al menos 4 GB de VRAM cuando sea detectable y 40 GB libres.

fr.IncompatibleTitle=Ordinateur incompatible avec KDP AI Factory
fr.IncompatibleRAM=Cet ordinateur dispose de moins de 16 Go de RAM. KDP AI Factory exécute l'IA localement et a besoin de suffisamment de mémoire pour travailler avec les livres, modèles et images de manière stable.
fr.IncompatibleGPU=La carte graphique détectée dispose de moins de 4 Go de mémoire vidéo. Cet ordinateur ne répond pas au profil minimal recommandé pour la génération locale d'images.
fr.IncompatibleDisk=Il reste moins de 40 Go d'espace libre sur le disque système. L'installation et les modèles locaux nécessitent de l'espace supplémentaire.
fr.IncompatibleGeneric=Cet ordinateur ne répond pas aux exigences minimales de KDP AI Factory. L'installation a été interrompue pour éviter une expérience instable.
fr.IncompatibleDetails=Minimum recommandé : Windows 10/11 64 bits, 16 Go de RAM, GPU avec au moins 4 Go de VRAM lorsqu'elle est détectable et 40 Go libres.

de.IncompatibleTitle=Computer nicht mit KDP AI Factory kompatibel
de.IncompatibleRAM=Dieser Computer verfügt über weniger als 16 GB RAM. KDP AI Factory führt KI lokal aus und benötigt ausreichend Arbeitsspeicher für Bücher, Modelle und Bilder.
de.IncompatibleGPU=Der erkannte Grafikadapter verfügt über weniger als 4 GB Videospeicher. Dieser Computer erfüllt nicht das empfohlene Mindestprofil für die lokale Bildgenerierung.
de.IncompatibleDisk=Auf dem Systemlaufwerk sind weniger als 40 GB frei. Installation und lokale Modelle benötigen zusätzlichen Speicherplatz.
de.IncompatibleGeneric=Dieser Computer erfüllt die Mindestanforderungen von KDP AI Factory nicht. Die Installation wurde abgebrochen, um eine instabile Nutzung zu vermeiden.
de.IncompatibleDetails=Empfohlenes Minimum: Windows 10/11 64 Bit, 16 GB RAM, GPU mit mindestens 4 GB VRAM, sofern erkennbar, und 40 GB freier Speicher.

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
    'if($ram -lt 16){exit 10};' +
    'if($disk -lt 40){exit 12};' +
    'if($vram -gt 0 -and $vram -lt 4){exit 11};' +
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
