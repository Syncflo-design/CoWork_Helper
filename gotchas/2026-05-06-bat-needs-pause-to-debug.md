# Windows .bat scripts need `pause` or you can't see why they failed

**Date:** 2026-05-06
**Bit me on:** `quick_purchase_invoice/push-to-github.bat` and `update-push.bat`. First version of the update script ran and the CMD window flashed open then closed — looked like the script "did nothing".

## Symptom

Double-click a `.bat` file from Explorer. The CMD window opens for a fraction of a second, then closes. Looks like nothing happened. In reality the script ran, hit a non-fatal condition like `git diff --cached --quiet` returning 0 (= "nothing to commit"), printed a message you couldn't read, and exited.

## Fix

Always end interactive `.bat` files with `pause`:

```batch
@echo off
REM ... script body ...

echo === Done ===
pause
```

Even better, also pause on error paths:

```batch
git push origin main
if errorlevel 1 (
    echo PUSH FAILED.
    pause
    exit /b 1
)
```

## Why this is easy to miss

When you launch a `.bat` from a CMD prompt that's already open, it inherits that window — output stays visible after the script ends. When you double-click from Explorer, Windows opens a fresh CMD just for the script and closes it on exit. Same script, completely different debuggability.

## Alternatives

- Run the script from an already-open CMD/PowerShell prompt (`./push-to-github.bat`) — output stays.
- Redirect output: `script.bat > log.txt 2>&1` then read `log.txt`.
- Add `pause` only in dev; remove for fully unattended scheduled runs.

## Related

- See `gotchas/2026-05-06-bash-vs-windows-git-ownership.md` for why the script appeared "to do nothing" the first time — the prior bash session left half-staged files but Windows git's `git add` saw no further changes, so the conditional commit step short-circuited.
