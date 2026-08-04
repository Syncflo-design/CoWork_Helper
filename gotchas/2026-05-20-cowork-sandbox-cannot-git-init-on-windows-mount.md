# Cowork sandbox can't create/own a git repo on the Windows-mounted folder

**Date:** 2026-05-20
**Domain:** Cowork mode — Linux sandbox (`mcp__workspace__bash`) vs Windows host mount
**Severity:** annoying (blocks self-serve git push; easy workaround)
**Bit me on:** scaffolding `nest_home` — tried to `git init && git commit` the new
repo from the sandbox so it would be push-ready.

## Symptom

Running git from the sandbox against a connected Windows folder
(`/sessions/<s>/mnt/ClaudeCode/nest_home`) fails partway through:

```
git init -q            # appears to work, creates a partial .git/
git config user.email  # → fatal: bad config line 1 in file .git/config
                       #   warning: unable to unlink '.git/config.lock':
                       #   Operation not permitted
rm -rf .git            # → rm: cannot remove '.git/branches': Operation not permitted
```

The `.git/` dir is left half-created and **cannot be deleted from the sandbox**
(`Operation not permitted` on `.git/config.lock`, `.git/branches`, etc.). It has
to be removed on the Windows side.

## Cause

The sandbox sees the host folder through a 9p/virtio-style mount. Git's rapid
create-lock-rename-unlink dance on tiny dotfiles (`config`, `config.lock`,
`HEAD`, `branches/`) races the mount's writeback, so locks can't be unlinked and
`.git/config` lands corrupt ("bad config line 1"). Same host-vs-bash drift family
as the Write/Edit truncation and NULL-padding gotchas — `.git/` is just the most
fragile victim because it's many small files mutated fast.

Also relevant: the sandbox has **no GitHub credentials, no `gh`, no token**, so
even a clean repo can't be pushed or created remotely from here.

## Fix / workflow

**Don't run `git init` / `commit` / `push` from the sandbox on a mounted repo.**
Build all the app files on disk (that part works fine), then do git on Windows:

```bash
# On Windows (Git Bash), from the repo root:
rm -rf .git                      # clear any partial .git the sandbox left
git init && git add -A && git commit -m "..."
# create the empty repo on github.com under the org first, then:
git remote add origin https://github.com/<org>/<repo>.git
git branch -M main && git push -u origin main
```

The sandbox is still the right place to **author and verify** files
(`py_compile`, `node --check`, JSON load, `file` for CRLF). Just hand the actual
git/push to the host.

## Tell-tale

`fatal: bad config line 1 in file .git/config` + `unable to unlink
'.git/config.lock': Operation not permitted` immediately after `git init` on a
`/sessions/.../mnt/...` path. As soon as you see it, stop; the repo is on a
mount. Delete `.git` on Windows and do git there.

## See also

- `gotchas/2026-05-06-host-vs-bash-fs-sync.md` — original mount drift (incl. `.git/` corruption).
- `gotchas/2026-05-17-cowork-write-tool-silent-truncation.md` — sibling: big-file Write truncation.
- `gotchas/2026-05-14-cowork-edit-tool-flips-lf-to-crlf.md` — sibling: Edit LF→CRLF flip.
