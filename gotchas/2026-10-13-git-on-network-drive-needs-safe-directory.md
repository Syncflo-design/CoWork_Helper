# git on the S: network drive needs `-c safe.directory='*'`

**Date:** 2026-10-13
**Domain:** Git Bash / Windows / network share (S:\Products\Fuse\*)
**Severity:** trivial

## Symptom

```
fatal: detected dubious ownership in repository at '//SYNCFLO-.../Products/Fuse/fuse_water_chemical'
```

on any git command in a repo on S:, including read-only ones like `git status`.

## Cause

The share's files are owned by an account git cannot match to the current Windows user, so git's
ownership check refuses the repo.

## Fix

Pass it per command (works in hand-over one-liners, changes no config):

```bash
git -c safe.directory='*' status
```

## Why this is non-obvious

The same repo works on C:. The message names ownership, not the network path.

## See also

- `gotchas/2026-05-06-bash-vs-windows-git-ownership.md`
