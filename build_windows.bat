@echo off
rem Builds the standalone Windows SETUP EXE (game + installer in one file).
rem Delegates to installer\windows\build-setup.bat - see installer\README.md.
call "%~dp0installer\windows\build-setup.bat" %*
