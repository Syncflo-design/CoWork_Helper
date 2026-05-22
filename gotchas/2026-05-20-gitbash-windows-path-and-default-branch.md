# Git Bash on Windows: backslash paths collapse, and Frappe apps push to `version-16` not `main`

**Date:** 2026-05-20
**Domain:** custom-app / Frappe Cloud / Cowork tooling
**Severity:** annoying (two separate time-wasters in one push)

## Symptom

Two failures in a row while pushing a custom Frappe app from Git Bash (MINGW64).

1. Pasting a Windows path with backslashes into `cd`:

```
$ cd C:\ClaudeCode\custom-subscription
bash: cd: C:ClaudeCodecustom-subscription: No such file or directory
fatal: not a git repository (or any of the parent directories): .git
```

2. After fixing the path and committing successfully, the push is rejected:

```
[version-16 5023d92] Reliable daily scheduler ...
 3 files changed, 141 insertions(+), 44 deletions(-)
error: src refspec main does not match any
error: failed to push some refs to 'https://github.com/Syncflo-design/custom-subscription'
```

(There are also benign `LF will be replaced by CRLF` warnings — ignore them.)

## Cause

1. In bash, `\` is the escape character, so `C:\ClaudeCode\custom-subscription` collapses to `C:ClaudeCodecustom-subscription` — a path that doesn't exist. Git Bash does NOT error on the backslashes; it silently builds the wrong path.
2. Frappe / ERPNext apps on Frappe Cloud track a version branch (`version-16`, `version-15`, …), **not** `main`/`master`. The commit landed on `version-16`; `git push origin main` references a local branch that doesn't exist → "src refspec main does not match any".

## Fix

Use forward slashes (or the `/c/` mount style) for the path, and push the actual branch:

```diff
- cd C:\ClaudeCode\custom-subscription
+ cd /c/ClaudeCode/custom-subscription

- git push origin main
+ git push origin version-16     # or: git push origin HEAD
```

Confirm the branch first when unsure: `git branch --show-current`.

## Why this is non-obvious

Git Bash quietly produces a garbage path from backslashes instead of throwing a clear "bad escape" error, so the real problem looks like "repo is missing." And `main` is the reflex default everywhere else — but Frappe Cloud-managed apps are pinned to a version branch, so the reflex push silently targets a non-existent ref. Neither message names the real cause.

Rule of thumb for these repos: always `git push origin HEAD` (pushes whatever branch you're on) and always paste Windows paths with `/` in Git Bash.

## See also

- Related gotchas: `gotchas/2026-05-06-git-bash-bracketed-paste.md`, `gotchas/2026-05-06-bash-vs-windows-git-ownership.md`, `gotchas/2026-05-07-git-stale-index-lock.md`
- App: https://github.com/Syncflo-design/custom-subscription (branch `version-16`)
