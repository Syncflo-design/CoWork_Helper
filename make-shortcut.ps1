# Standalone shortcut-creator. Run this if install.ps1 didn't put the
# desktop shortcut in place. Doesn't touch skills.

$KnowledgeBase = "C:\ClaudeCode\CoWork_Helper"
$PrimerPath = Join-Path $KnowledgeBase "primer.cmd"

if (-not (Test-Path $PrimerPath)) {
    Write-Host "ERROR: $PrimerPath not found." -ForegroundColor Red
    exit 1
}

# Resolve desktop. Handles OneDrive redirection.
$Desktop = [Environment]::GetFolderPath("Desktop")
Write-Host "Desktop resolved to: $Desktop" -ForegroundColor Cyan

if (-not (Test-Path $Desktop)) {
    Write-Host "ERROR: Desktop path doesn't exist: $Desktop" -ForegroundColor Red
    Write-Host "Try OneDrive Desktop or USERPROFILE\Desktop manually." -ForegroundColor Yellow
    exit 1
}

$LinkPath = Join-Path $Desktop "Cowork start-prompt.lnk"

try {
    $WScriptShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WScriptShell.CreateShortcut($LinkPath)
    $Shortcut.TargetPath = $PrimerPath
    $Shortcut.WorkingDirectory = $KnowledgeBase
    $Shortcut.Description = "Copies Cowork knowledge-base opener to clipboard"
    $Shortcut.IconLocation = "shell32.dll,134"
    $Shortcut.Save()
    Write-Host "OK: Shortcut created at $LinkPath" -ForegroundColor Green
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Fallback: copy primer.cmd to your desktop yourself, or right-click" -ForegroundColor Yellow
    Write-Host "  C:\ClaudeCode\CoWork_Helper\primer.cmd  ->  Send to  ->  Desktop (create shortcut)" -ForegroundColor Yellow
    exit 1
}

# Verify it's actually there
if (Test-Path $LinkPath) {
    Write-Host ""
    Write-Host "Verified: $LinkPath exists." -ForegroundColor Green
    Write-Host "If you don't see it on the desktop, press F5 on the desktop to refresh." -ForegroundColor DarkGray
} else {
    Write-Host "ODD: Shortcut creation reported success but file is missing." -ForegroundColor Yellow
}
