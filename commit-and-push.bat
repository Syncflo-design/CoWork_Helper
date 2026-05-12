@echo off
REM Commits + pushes the latest CoWork_Helper changes to GitHub.
REM Run from anywhere; this script cd's to the repo.
REM
REM Why a .bat and not bash: bash sandbox can't push a repo whose .git was
REM created by Windows (see gotchas/2026-05-06-bash-vs-windows-git-ownership.md).
REM Always do git plumbing from Windows here.

cd /d C:\ClaudeCode\CoWork_Helper || (
    echo Could not cd to C:\ClaudeCode\CoWork_Helper
    pause
    exit /b 1
)

echo.
echo === Current status ===
git status --short
echo.

REM Stash a stale index.lock if it's still sitting around from a previous run.
REM (gotchas/2026-05-07-git-stale-index-lock.md)
if exist .git\index.lock (
    echo Removing stale .git\index.lock
    del /q .git\index.lock
)

git add -A || (
    echo git add failed
    pause
    exit /b 1
)

git diff --cached --quiet
if errorlevel 1 (
    git commit -m "docs: audit erpnext_sbca (9t9it Sage integration) on nesterp + chatty-cron gotcha" || (
        echo git commit failed
        pause
        exit /b 1
    )
) else (
    echo Nothing new to commit.
    pause
    exit /b 0
)

git push origin main || (
    echo git push failed - check your remote auth ^(token / SSH key^)
    pause
    exit /b 1
)

echo.
echo === Done ===
echo View at https://github.com/Syncflo-design/CoWork_Helper
pause
