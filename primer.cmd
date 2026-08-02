@echo off
REM Copies the Cowork start-prompt to the clipboard, ready to paste into a new chat.
REM Install creates a desktop shortcut to this; you can also pin it to taskbar.

type "%~dp0start-prompt.txt" | clip
echo Cowork start-prompt copied to clipboard.
echo Switch to Cowork, start a new chat, Ctrl+V, edit the [TOPIC] placeholder, send.
echo.
if exist "%~dp0graphify-out\graph.json" (
  echo Knowledge graph: found - the assistant will query it before reading files.
) else (
  echo Knowledge graph: MISSING - rebuild with: graphify update "%~dp0"
)
timeout /t 4 /nobreak > nul
