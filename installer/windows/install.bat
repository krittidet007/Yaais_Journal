@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Yaai's Journal - Installer
cd /d "%~dp0"

rem ============================================================
rem  Yaai's Journal - Windows installer (runs from the source
rem  folder; installs to %LOCALAPPDATA%\Programs\YaiisJournal,
rem  no admin rights needed, and adds Desktop + Start menu
rem  shortcuts and an uninstaller.)
rem ============================================================

echo.
echo   ###  ###  YAAI'S JOURNAL  ###  ###
echo   A Southern Thailand Adventure - a Python-teaching tale
echo   --------------------------------------------
echo.

set "DEST=%LOCALAPPDATA%\Programs\YaiisJournal"
set "APPDIR=%DEST%\app"

rem ------------------------------------------------ find python
set "PY="
py -3 --version >nul 2>nul
if not errorlevel 1 (
    set "PY=py -3"
) else (
    python --version >nul 2>nul
    if not errorlevel 1 set "PY=python"
)

if "%PY%"=="" (
    echo   Python was not found. Installing it with winget...
    echo   (a Microsoft tool that ships with Windows 10/11)
    echo.
    winget install --id Python.Python.3.12 --source winget --silent ^
        --accept-package-agreements --accept-source-agreements --scope user
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    )
)

if "%PY%"=="" (
    echo.
    echo   Could not install Python automatically.
    echo   Please install Python 3.10+ from https://python.org
    echo   (tick "Add python.exe to PATH"), then run this installer again.
    echo.
    pause
    exit /b 1
)

echo   Using Python:  %PY%
echo.

rem ------------------------------------------------ install the game
echo   Installing to %DEST% ...
if exist "%DEST%" rd /s /q "%DEST%"
mkdir "%APPDIR%"

echo   Copying game files...
copy /y main.py "%APPDIR%\" >nul
copy /y requirements.txt "%APPDIR%\" >nul
copy /y README.md "%APPDIR%\" >nul
mkdir "%APPDIR%\game"
robocopy game "%APPDIR%\game" /E /NFL /NDL /NJH /NJS /NP >nul
if errorlevel 8 goto :failed

mkdir "%DEST%\icons"
copy /y installer\icons\icon.ico "%DEST%\icons\" >nul
copy /y installer\windows\make-shortcuts.ps1 "%DEST%\" >nul

echo   Setting up the game's own Python (one-time, few seconds)...
"%PY%" -m venv "%DEST%\venv"
if errorlevel 1 goto :failed
"%DEST%\venv\Scripts\python" -m pip install --upgrade pip >nul 2>nul
"%DEST%\venv\Scripts\python" -m pip install --no-input -r "%APPDIR%\requirements.txt"
if errorlevel 1 goto :failed

rem ------------------------------------------------ launcher
> "%DEST%\play.cmd" echo @echo off
>> "%DEST%\play.cmd" echo start "" /d "%APPDIR%" "%DEST%\venv\Scripts\pythonw.exe" main.py

rem ------------------------------------------------ shortcuts + uninstall entry
echo   Creating shortcuts...
powershell -NoProfile -ExecutionPolicy Bypass ^
  -File "%DEST%\make-shortcuts.ps1" ^
  -ExePath "%DEST%\play.cmd" -IconPath "%DEST%\icons\icon.ico" ^
  -UninstallBat "%DEST%\uninstall.bat" -AppDir "%APPDIR%" -VenvDir "%DEST%\venv"
if errorlevel 1 goto :failed

echo   All done!
echo.
echo   ###  ###  INSTALLED  ###  ###
echo.
echo   Look for "Yaai's Journal" on your Desktop and in the
echo   Start menu. Uninstall it any time from "Add or remove
echo   programs", or by running:
echo      %DEST%\uninstall.bat
echo.
echo   Saves live in %%APPDATA%%\wicha and survive updates.
echo.
choice /c YN /m "Start the game now" /d Y /t 5
if errorlevel 2 goto :end
start "" /d "%APPDIR%" "%DEST%\venv\Scripts\pythonw.exe" main.py
goto :end

:failed
echo.
echo   Installation failed - please read the messages above.
echo   Common fixes: check your internet connection, or run
echo   this installer as a normal user (no admin needed).
pause
exit /b 1

:end
endlocal
exit /b 0
