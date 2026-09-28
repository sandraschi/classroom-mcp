@echo off
REM Double-click wrapper — delegates to start.ps1.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
