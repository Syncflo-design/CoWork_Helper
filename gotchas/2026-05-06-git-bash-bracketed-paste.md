# Git Bash on Windows: Bracketed-Paste Sequences Mangle Multi-Line Commands

**Date:** 2026-05-06
**Environment:** Git Bash (MINGW64) on Windows 10/11
**Status:** Confirmed in live session

## The Gotcha

When you paste multiple commands into Git Bash on Windows (especially across newlines), the terminal sometimes inserts "bracketed paste" escape sequences (`^[[200~` and `^[[201~`) into the input stream. These look like control characters that get glued to the start of your first command, breaking it:

```
$ ^[[200~rm -f .git/index.lock
git status
git add ...
bash: $'\E[200~rm': command not found
```

The first command (here `rm`) becomes `^[[200~rm` and bash can't find an executable by that name. As a result the lockfile never gets removed, and **every subsequent `git add` / `git commit` fails** for the same lock reason.

The downstream symptom is confusing: you see repeated `fatal: Unable to create '.git/index.lock'` errors and assume git is broken. It isn't — the actual problem is the first paste failed silently.

## How to Recognise It

- Look for `^[[200~` or `^[[201~` at the start of the first command in the pasted block
- The error message will reference a command name with `\E[200~` prefixed (e.g. `bash: $'\E[200~rm': command not found`)
- Subsequent commands that depended on the first one's effect will fail with confusing secondary errors

## The Fix

**Type the first command by hand instead of pasting**, then paste the rest. Or paste each command on its own line, hitting Enter after each, so the bracketed-paste markers don't span commands.

Cleanest workflow when feeding a sequence to a user in Git Bash:

```
type-this-line-1
type-this-line-2
type-this-line-3
```

— each in its own fenced block, so they paste one at a time.

## Avoiding It Permanently

Add this to `~/.bashrc` or `~/.inputrc` to disable bracketed-paste in Git Bash:

```
# In ~/.inputrc
set enable-bracketed-paste off
```

Restart Git Bash. Pasting multi-line blocks should now work cleanly.

Alternatively, switch to Windows Terminal hosting Git Bash — its paste handling is generally cleaner than the legacy mintty terminal Git for Windows ships with.

## Why This Mattered Here

Cost the deploy of the Insights fork ~10 minutes of confusion: lockfile errors looked like a git problem, but the real problem was that `rm -f .git/index.lock` had been silently swallowed by the bracketed-paste glue. Once we typed the `rm` by hand, everything proceeded normally.
