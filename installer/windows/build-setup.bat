@echo off
rem ============================================================
rem  Builds the standalone Windows SETUP EXE:
rem    dist\YaiisJournal.exe        (the game, via PyInstaller)
rem    dist\YaiisJournal-Setup.exe  (single-file installer via
rem                                  IExpress, which ships with
rem                                  Windows - no extra tools)
rem  Run this ON a Windows machine, from the repo root or by
rem  double-clicking it in explorer.
rem ============================================================
setlocal
cd /d "%~dp0.."

set "PY=python"
python --version >nul 2>nul || set "PY=py -3"
python --version >nul 2>nul

echo Installing build tools (one-time)...
%PY% -m pip install --upgrade pyinstaller pygame-ce
if errorlevel 1 goto :failed

echo.
echo Building the game exe...
%PY% -m PyInstaller --noconfirm --clean YaiisJournal.spec
if errorlevel 1 goto :failed

echo.
echo Packaging the installer (IExpress)...
copy /y installer\windows\setup-install.cmd dist\ >nul
copy /y installer\windows\make-shortcuts.ps1 dist\ >nul
copy /y installer\icons\icon.ico dist\ >nul

iexpress /N /O installer\windows\setup.sed
if not exist dist\YaiisJournal-Setup.exe goto :failed

echo.
echo   ###  ###  DONE  ###  ###
echo   Game installer:  %CD%\dist\YaiisJournal-Setup.exe
echo   Give that single file to any Windows player.
echo.
pause
exit /b 0

:failed
echo.
echo Build failed - read the errors above.
pause
exit /b 1
