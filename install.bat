@echo off
REM Double-clickable wrapper for install.ps1
REM Right-click -> Run as administrator NOT required (uses junctions, not symlinks)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
echo.
pause
