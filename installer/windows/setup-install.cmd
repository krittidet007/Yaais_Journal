@echo off
rem Runs inside the IExpress package (YaiisJournal-Setup.exe) after it has
rem extracted this script + YaiisJournal.exe + icon.ico + README.md into a
rem temp folder. %~dp0 is that temp folder. No admin needed: installs to
rem %LOCALAPPDATA%\Programs\YaiisJournal.
setlocal
cd /d "%~dp0"

set "DEST=%LOCALAPPDATA%\Programs\YaiisJournal"
mkdir "%DEST%" 2>nul

echo Installing Yaai's Journal to %DEST% ...
copy /y YaiisJournal.exe "%DEST%\" >nul
copy /y icon.ico "%DEST%\" >nul
copy /y README.md "%DEST%\" >nul 2>nul

powershell -NoProfile -ExecutionPolicy Bypass ^
  -File make-shortcuts.ps1 ^
  -ExePath "%DEST%\YaiisJournal.exe" -IconPath "%DEST%\icon.ico" ^
  -UninstallBat "%DEST%\uninstall.bat" -AppDir "%DEST%"
if errorlevel 1 (
    echo Shortcut creation failed - run this setup again.
    pause
    exit /b 1
)

echo.
echo   ###  ###  INSTALLED  ###  ###
echo   Find "Yaai's Journal" on your Desktop and Start menu.
echo   Uninstall from "Add or remove programs" any time.
echo   Saves live in %%APPDATA%%\wicha and survive updates.
echo.
choice /c YN /m "Start the game now" /d Y /t 5
if errorlevel 2 exit /b 0
start "" "%DEST%\YaiisJournal.exe"
exit /b 0
