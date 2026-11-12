[Version]
Class=IEXPRESS
SEDVersion=3

[Options]
PackagePurpose=InstallApp
ShowInstallProgram=1
HideExtractAnimation=1
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
TargetName=%TARGETNAME%
FriendlyName=%FriendlyName%
PlatformLaunchedStudio=2048
FILE0="setup-install.cmd"
FILE1="YaiisJournal.exe"
FILE2="icon.ico"
FILE3="make-shortcuts.ps1"
FILE4="README.md"

[SourceFiles]
SourceFiles0=.\dist\

[SourceFilesNames]
FILE0=.\dist\setup-install.cmd
FILE1=.\dist\YaiisJournal.exe
FILE2=.\dist\icon.ico
FILE3=.\dist\make-shortcuts.ps1
FILE4=.\dist\README.md

[Strings]
TARGETNAME="dist\YaiisJournal-Setup.exe"
FriendlyName="Yaai's Journal"
InstallPrompt=Ready to install Yaai's Journal? This needs no admin rights.
DisplayLicense=
FinishMessage=Yaai's Journal is installed! Look for it on your Desktop and in the Start menu.
PACKAGE_DISPLAYNAME=Yaai's Journal
PACKAGE_FILENAME=YaiisJournal-Setup.exe
INSTALLTYPE=1
ADMININSTALLPRG=
POSTINSTALLCMD=
POSTINSTALLARGS=
POSTINSTALLNAME=
POSTINSTALLPATH=
POSTINSTALLTYPE=0
InstallProgram="setup-install.cmd"
POSTINSTALLCMD=
POSTINSTALLNAME=
