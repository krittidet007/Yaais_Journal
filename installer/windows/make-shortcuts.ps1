# Creates Desktop + Start menu shortcuts and the "Add or remove programs"
# entry for Yaai's Journal. Called by install.bat / setup-install.cmd:
#
#   powershell -File make-shortcuts.ps1 -ExePath <play.cmd> -IconPath <icon.ico> `
#              -UninstallBat <uninstall.bat> -AppDir <dir> [-VenvDir <dir>]
param(
    [Parameter(Mandatory = $true)] [string] $ExePath,
    [Parameter(Mandatory = $true)] [string] $IconPath,
    [Parameter(Mandatory = $true)] [string] $UninstallBat,
    [Parameter(Mandatory = $true)] [string] $AppDir,
    [string] $VenvDir = ""
)

$ErrorActionPreference = "Stop"

function New-GameShortcut([string] $shortcutPath) {
    $shell = New-Object -ComObject WScript.Shell
    $sc = $shell.CreateShortcut($shortcutPath)
    $sc.TargetPath = $ExePath
    $sc.WorkingDirectory = [System.IO.Path]::GetDirectoryName($ExePath)
    $sc.IconLocation = $IconPath
    $sc.Description = "Yaai's Journal - A Southern Thailand Adventure"
    $sc.Save()
}

$desktop = [Environment]::GetFolderPath("Desktop")
$startMenu = [Environment]::GetFolderPath("Programs")
$menuDir = Join-Path $startMenu "Yaai's Journal"
New-Item -ItemType Directory -Force -Path $menuDir | Out-Null

New-GameShortcut (Join-Path $desktop "Yaai's Journal.lnk")
New-GameShortcut (Join-Path $menuDir "Yaai's Journal.lnk")

# Uninstall entry (per-user, HKCU - no admin needed)
$reg = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\YaiisJournal"
New-Item -Path $reg -Force | Out-Null
Set-ItemProperty $reg -Name DisplayName     -Value "Yaai's Journal"
Set-ItemProperty $reg -Name DisplayVersion  -Value "1.0"
Set-ItemProperty $reg -Name Publisher      -Value "Yaai's Journal team"
Set-ItemProperty $reg -Name DisplayIcon     -Value $IconPath
Set-ItemProperty $reg -Name UninstallString -Value ('"' + $UninstallBat + '"')
Set-ItemProperty $reg -Name InstallLocation -Value $AppDir
Set-ItemProperty $reg -Name NoModify        -Value 1 -Type DWord
Set-ItemProperty $reg -Name NoRepair        -Value 1 -Type DWord

Write-Host "shortcuts + uninstall entry created"
