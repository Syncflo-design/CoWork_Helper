# Git fails with "Unable to create index.lock: File exists"

**Date:** 2026-05-07
**Domain:** Git / Windows / Cowork-mode tooling
**Severity:** annoying

## Symptom

Running `git add` or any git write command fails immediately:

```
fatal: Unable to create '.git/index.lock': File exists.
Another git process seems to be running in this repository,
or the lock file may be stale
```

## Cause

A previous git process (or a crashed Cowork bash session) left a stale `.git/index.lock` file behind. Git refuses to proceed while the lock exists.

## Fix

Remove **both** common lock files (either or both may exist), then retry. The `2>/dev/null` suppresses errors if a file is already gone:

```bash
rm C:/ClaudeCode/<repo>/.git/HEAD.lock C:/ClaudeCode/<repo>/.git/index.lock 2>/dev/null; git add -A && git commit -m "your message" && git push origin main
```

Or if you're already in the repo directory:

```bash
rm .git/HEAD.lock .git/index.lock 2>/dev/null; git add -A && git commit -m "your message" && git push origin main
```

Note: use `;` (not `&&`) before `git add` so the rm failure (if files don't exist) doesn't abort the rest of the command.

## Why this is non-obvious

The error message says "another git process seems to be running" which makes you think something is actively using the repo. In practice it's almost always a ghost lock from a crashed or cancelled process — nothing is actually running. Safe to delete immediately.

The first attempt may clear `index.lock` but leave `HEAD.lock` (or vice versa), causing a second failure with a different filename. Always nuke both at once.

## See also

- `gotchas/2026-05-06-bash-vs-windows-git-ownership.md` — related git plumbing gotcha on this setup
- `gotchas/2026-05-06-git-bash-bracketed-paste.md` — other Git Bash on Windows quirks
