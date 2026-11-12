@echo off
rem Uninstalls Yaai's Journal (either install: source venv or packaged exe).
setlocal
set "DEST=%LOCALAPPDATA%\Programs\YaiisJournal"

echo Removing Yaai's Journal...
rd /s /q "%DEST%" >nul 2>nul

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "Remove-Item 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\YaiisJournal' -ErrorAction SilentlyContinue; ^
  Remove-Item ([Environment]::GetFolderPath('Desktop') + '\Yaai''s Journal.lnk') -ErrorAction SilentlyContinue; ^
  Remove-Item (([Environment]::GetFolderPath('Programs')) + '\Yaai''s Journal') -Recurse -ErrorAction SilentlyContinue" >nul 2>nul

echo Removed.
echo (Your saves in %%APPDATA%%\wicha were kept - delete that folder to
echo  erase them too.)
pause
