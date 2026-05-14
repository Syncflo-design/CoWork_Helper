# Gotcha: Cowork Edit/Write tool silently flips a repo file from LF to CRLF

**Date:** 2026-05-14
**Environment:** Cowork mode — Claude Edit/Write tools (Windows host) vs a git repo that uses LF
**Status:** Confirmed live (erpnext_sbca reconciliation build)

## The Gotcha

After editing a single ~6-line block in `erpnext_sbca/hooks.py` with the Edit
tool, `git diff` showed the **entire file** changed — 590 lines of churn for a
6-line edit:

```
erpnext_sbca/hooks.py | 590 +++++++++++----------
1 file changed, 317 insertions(+), 294 deletions(-)
```

Cause: the Edit tool rewrote the whole file with **CRLF** line endings, even
though `HEAD` had it as **LF**. Every line then reads as deleted-and-readded.

The maddening part: it's **inconsistent**. In the same session, `journal_entry.py`
and `erpnext_sbca_settings.json` were edited the same way and stayed LF (clean
6-line and 16-line diffs). Only `hooks.py` got flipped. So you can't assume "all
my edits are fine" or "all my edits are broken" — you have to check each one.

## How to Recognise It

- `git diff --stat` shows churn wildly out of proportion to what you changed
  (whole file, or hundreds of lines, for a tiny edit).
- `git diff` shows long runs of `-line` immediately followed by `+line` with
  *identical visible content*.
- `file path/to/edited.py` reports `... with CRLF line terminators`.
- The tell-tale confirmation:
  ```bash
  git diff --ignore-cr-at-eol --stat path/to/edited.py
  ```
  If this shows the small, real change but plain `git diff --stat` shows the
  whole file — it's an EOL flip, not a content problem.

## The Fix

Strip the carriage returns from the bash side and re-check:

```bash
sed -i 's/\r$//' path/to/edited.py
file path/to/edited.py            # should no longer say CRLF
git diff --stat path/to/edited.py # should now show only the real change
```

For a JSON / Python file, re-validate after the strip (`python3 -m py_compile`,
`python3 -c "import json; json.load(...)"`) — stripping CR is safe, but confirm.

If several files are affected, normalise them all at once:
```bash
for f in $(git diff --name-only); do
  file "$f" | grep -q CRLF && sed -i 's/\r$//' "$f" && echo "fixed $f"
done
```

## Prevention

- **After ANY Edit/Write on an existing repo file, run `git diff --stat` before
  committing.** Churn out of proportion to the edit = EOL flip; fix with `sed`.
- Don't trust a "clean-looking" Read — the host Read tool renders CRLF and LF
  identically. `file` and `git diff --stat` from bash are ground truth.
- If the repo has a `.gitattributes` with `* text=auto eol=lf`, git *may* mask
  this on commit — but `erpnext_sbca` does not, so the CRLF lands in history.
- Cheapest safe habit: end every edit session with
  `for f in $(git diff --name-only); do file "$f"; done` and scan for CRLF.

## Also Confirmed This Session: host-vs-bash truncation (3rd occurrence)

The original host-vs-bash sync issue bit again. A freshly Write-created
~715-line `reconciliation.py` showed complete via the host Read tool, but the
bash mount saw it **truncated mid-line at line 708**, so `python3 -m py_compile`
failed with `SyntaxError: '[' was never closed`. `sleep 3` did not clear it.

Fix that worked: rewrite the file via a bash heredoc (`cat > file << 'EOF'`),
which writes through the Linux mount directly and is immediately visible to
tooling. This matches the workaround already documented in
`gotchas/2026-05-06-host-vs-bash-fs-sync.md` — noting here only that it is now
confirmed a **third** time (06 May, 11 May, 14 May) and is reliably reproducible
on large Write-tool files. Treat bash-heredoc as the default for any new file
over a few hundred lines.

## See Also

- `gotchas/2026-05-06-host-vs-bash-fs-sync.md` — truncated writes, stale mount,
  `.git/` corruption. The truncation note above is a recurrence of that issue.
- `gotchas/2026-05-11-host-vs-bash-write-truncation.md` — the NULL-padding
  variant of the same host/mount drift.
- Common thread across all three: **the host Read tool's view is for human
  reading only; `file`, `wc -c`, `git diff --stat`, and the compilers on the
  bash side are ground truth.** Always verify writes/edits from bash.
