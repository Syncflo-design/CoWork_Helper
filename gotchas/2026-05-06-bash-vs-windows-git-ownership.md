# Bash sandbox can't push a Windows-initialised git repo

**Date:** 2026-05-06
**Bit me on:** `quick_purchase_invoice` — tried `git add/commit/push` from the Linux bash sandbox after Russell had already initialised + pushed the repo from Windows.

## Symptom

```
warning: unable to unlink '.git/objects/3b/tmp_obj_zWLhlr': Operation not permitted
warning: unable to unlink '.git/objects/0d/tmp_obj_LMdkxx': Operation not permitted
fatal: Unable to create '.../.git/index.lock': File exists.

Another git process seems to be running in this repository, e.g.
an editor opened by 'git commit'. Please make sure all processes
are terminated then try again.
```

The "Another git process" message is misleading — there's no other process. The real cause is that Windows `git init` created `.git/objects/*` owned by the Windows user, and the Linux bash user (here `cool-happy-faraday`) cannot modify those files even though they're on a shared mount.

A subtle second symptom: the bash session may successfully `git add` (the index file gets updated) but fail at `git commit` because pack/object writes hit the permission wall. That leaves stale `.git/objects/*/tmp_obj_*` and `.git/index.lock` files that block subsequent runs from EITHER side.

## Fix

**Pick one side and stay there.** For repos that need pushing to GitHub, the practical answer is: do all `git` operations from Windows. Use bash only for editing files in the working tree, never for git plumbing.

To recover after a botched bash-side run:

1. From Windows CMD/PowerShell:
   ```cmd
   cd C:\ClaudeCode\<repo>
   if exist .git\index.lock del .git\index.lock
   git reset HEAD
   git add -A
   git status
   git commit -m "..."
   git push
   ```

2. If `git status` reports "Untracked files: tmp_obj_*" or similar artefacts under `.git/`, those can be deleted; they're failed write attempts:
   ```cmd
   for /r .git\objects %f in (tmp_obj_*) do del "%f"
   ```

## Why a simple `chown` doesn't fix it

The bash sandbox runs as a fixed unprivileged user (`cool-happy-faraday` here) and has no `sudo`. Even though the mount looks writable, the per-file ownership inherited from Windows blocks `unlink()`. There's no clean way to flip ownership from inside the sandbox.

## Side effect on `.bat` scripts

If your push script does:

```batch
git add .
git diff --cached --quiet
if errorlevel 1 ( git commit -m "..." )
```

…and a previous bash run left a half-staged commit, then `git add .` may make no further changes, `git diff --cached --quiet` will return success (nothing NEW to commit beyond what's already in the index), and the `if` block is skipped. The script reports "Nothing to commit" — which looks like a no-op but is actually a stale-state indicator. **Fix**: prepend `git reset HEAD` to drop any inherited staged state before the fresh `git add -A`. See `update-push.bat` in the `quick_purchase_invoice` project for a robust recipe.

## Cross-reference

- `gotchas/2026-05-06-host-vs-bash-fs-sync.md` — the same dual-environment system, but for plain file content rather than git plumbing.
- `gotchas/2026-05-06-bat-needs-pause-to-debug.md` — why the first symptom looked like "did nothing".
