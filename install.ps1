# CoWork_Helper installer
# Run this ONCE per Windows machine. From then on, every Cowork chat auto-loads
# the skills in this folder when their descriptions match.
#
# What it does:
#   1. Finds Claude's user-skills directory
#   2. Hard-links (or copies as fallback) each skill folder from
#      C:\ClaudeCode\CoWork_Helper\skills\  into  <claude-skills>\
#   3. Reports what it did
#
# Re-run any time you add a new skill — it's idempotent.

$ErrorActionPreference = "Continue"  # don't halt on a single skill error; we report at the end

$KnowledgeBase = "C:\ClaudeCode\CoWork_Helper"
$SkillsSource  = Join-Path $KnowledgeBase "skills"

# Claude's user-skills directory pattern. The two GUIDs are this install's
# marketplace ID and user/profile ID. We discover them from the existing path.
$ClaudeRoot = "$env:LOCALAPPDATA\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\local-agent-mode-sessions\skills-plugin"

if (-not (Test-Path $ClaudeRoot)) {
    Write-Host "ERROR: Claude skills-plugin directory not found at:" -ForegroundColor Red
    Write-Host "  $ClaudeRoot" -ForegroundColor Red
    Write-Host ""
    Write-Host "This script expects the Microsoft Store version of Claude. If you have" -ForegroundColor Yellow
    Write-Host "the .exe installer version, the path may be different. Search your" -ForegroundColor Yellow
    Write-Host "AppData for 'skills-plugin' and edit `$ClaudeRoot at the top of this script." -ForegroundColor Yellow
    exit 1
}

# There may be multiple GUID-named directories. Use the most recently modified.
$MarketplaceDir = Get-ChildItem $ClaudeRoot -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $MarketplaceDir) {
    Write-Host "ERROR: No marketplace directory under $ClaudeRoot" -ForegroundColor Red
    exit 1
}

$ProfileDir = Get-ChildItem $MarketplaceDir.FullName -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $ProfileDir) {
    Write-Host "ERROR: No profile directory under $($MarketplaceDir.FullName)" -ForegroundColor Red
    exit 1
}

$SkillsDest = Join-Path $ProfileDir.FullName "skills"

if (-not (Test-Path $SkillsDest)) {
    Write-Host "ERROR: Skills directory not found at $SkillsDest" -ForegroundColor Red
    exit 1
}

Write-Host "Installing CoWork_Helper skills" -ForegroundColor Cyan
Write-Host "  Source: $SkillsSource"
Write-Host "  Dest:   $SkillsDest"
Write-Host ""

# Each subfolder of skills/ is one skill. Mirror them into the destination.
$Installed = 0
$Failed = 0
foreach ($Skill in Get-ChildItem $SkillsSource -Directory) {
    $Target = Join-Path $SkillsDest $Skill.Name

    try {
        if (Test-Path $Target) {
            # CRITICAL: if Target is a junction, `Remove-Item -Recurse` follows
            # the link and deletes the source. Use `rmdir` to remove just the
            # junction itself.
            $Item = Get-Item $Target -Force
            $IsJunction = $Item.Attributes -band [IO.FileAttributes]::ReparsePoint
            if ($IsJunction) {
                cmd /c rmdir "`"$Target`"" | Out-Null
                Write-Host "  Replacing junction: $($Skill.Name)" -ForegroundColor Yellow
            } else {
                Remove-Item $Target -Recurse -Force
                Write-Host "  Replacing folder: $($Skill.Name)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  Installing: $($Skill.Name)" -ForegroundColor Green
        }

        # Junction (no admin needed). Capture both stdout and stderr from cmd.
        $LinkOutput = cmd /c mklink /J "`"$Target`"" "`"$($Skill.FullName)`"" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    -> Linked (changes auto-sync)" -ForegroundColor DarkGray
            $Installed++
        } else {
            # Junction failed; fall back to copy.
            Write-Host "    mklink output: $LinkOutput" -ForegroundColor DarkGray
            Copy-Item $Skill.FullName $Target -Recurse -Force
            Write-Host "    -> Copied (re-run installer after editing skills)" -ForegroundColor DarkGray
            $Installed++
        }
    } catch {
        Write-Host "  FAILED to install $($Skill.Name): $($_.Exception.Message)" -ForegroundColor Red
        $Failed++
    }
}

Write-Host ""
Write-Host "Skills: $Installed installed, $Failed failed." -ForegroundColor $(if ($Failed -eq 0) { "Green" } else { "Yellow" })
Write-Host ""

# --- Desktop shortcut for the clipboard primer ---
Write-Host "Creating desktop shortcut for the Cowork start-prompt..." -ForegroundColor Cyan
$Desktop = [Environment]::GetFolderPath("Desktop")
Write-Host "  Desktop resolved to: $Desktop" -ForegroundColor DarkGray
$LinkPath = Join-Path $Desktop "Cowork start-prompt.lnk"
$PrimerPath = Join-Path $KnowledgeBase "primer.cmd"

try {
    $WScriptShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WScriptShell.CreateShortcut($LinkPath)
    $Shortcut.TargetPath = $PrimerPath
    $Shortcut.WorkingDirectory = $KnowledgeBase
    $Shortcut.Description = "Copies Cowork knowledge-base opener to clipboard"
    $Shortcut.IconLocation = "shell32.dll,134"
    $Shortcut.Save()

    if (Test-Path $LinkPath) {
        Write-Host "  OK: Shortcut at $LinkPath" -ForegroundColor Green
    } else {
        Write-Host "  WARN: Save reported success but file not found at $LinkPath" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  FAILED to create shortcut: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Workaround: right-click primer.cmd in Explorer -> Send to -> Desktop (create shortcut)" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Restart Cowork (close and reopen) so it picks up the new skills."
Write-Host "  2. SKILLS: just mention the topic in chat (e.g. 'Insights v3 dashboard')"
Write-Host "     and the relevant skill auto-loads."
Write-Host "  3. KNOWLEDGE BASE (gotchas/playbooks/sites): double-click the new"
Write-Host "     desktop shortcut 'Cowork start-prompt' to copy the opener to your"
Write-Host "     clipboard, then Ctrl+V into a new Cowork chat."
Write-Host ""
Write-Host "Pro tip: pin the shortcut to your Windows taskbar so it's one click." -ForegroundColor DarkGray
