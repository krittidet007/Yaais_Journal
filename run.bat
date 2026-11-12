@echo off
setlocal
cd /d "%~dp0"

rem `python` is not always on PATH on Windows; fall back to the py launcher.
set "PY=python"
python --version >nul 2>nul || set "PY=py -3"

%PY% -m pip install -r requirements.txt
%PY% main.py
pause
