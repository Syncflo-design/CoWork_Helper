@echo off
REM Copies the Cowork start-prompt to the clipboard, ready to paste into a new chat.
REM Install creates a desktop shortcut to this; you can also pin it to taskbar.

type "%~dp0start-prompt.txt" | clip
echo Cowork start-prompt copied to clipboard.
echo Switch to Cowork, start a new chat, Ctrl+V, edit the [TOPIC] placeholder, send.
timeout /t 3 /nobreak > nul
