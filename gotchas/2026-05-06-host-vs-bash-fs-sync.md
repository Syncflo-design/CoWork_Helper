# Cowork Mode: File-System Sync Mismatch Between Host (Read/Write) and Linux Mount (bash)

**Date:** 2026-05-06
**Environment:** Cowork mode — Claude file tools (Read/Write/Edit) on Windows host vs. mcp__workspace__bash on Linux sandbox
**Status:** Confirmed in live session, twice

## The Gotcha

When Claude is using Cowork mode, the **Read/Write/Edit/Grep/Glob** tools operate on the Windows host filesystem directly. The **bash** tool operates on a Linux sandbox where the user's folders are exposed via a mount (`/sessions/<id>/mnt/<folder>`).

These two views are **not always in sync**. Specific symptoms observed:

1. **Truncated writes via Write tool.** A `Write` call returns "successfully created/updated", and a follow-up `Read` shows the full intended content — but `bash`-side `wc -l`/`cat` shows the file truncated mid-line. The truncation point is usually a multi-hundred-line offset (~247 lines was where it hit us on a userscript edit).

2. **Phantom modifications and packed-refs corruption.** A long-running Edit/Write sequence on a `.git/`-adjacent file (here, `.git/packed-refs` after a `git clone`) ended up with valid content followed by hundreds of trailing null bytes (`\x00`), causing `git status` and `git branch` to fail with:
   ```
   fatal: unterminated line in .git/packed-refs: ...
   ```

3. **Stale mount view.** After a Write, `bash` may continue to see the OLD file contents for several seconds — sometimes minutes — even though the host-side `Read` returns the NEW contents immediately.

## How to Recognise It

- `node --check` or any parser reports an unexpected end-of-input or syntax error AFTER you've successfully written/edited a file
- `wc -l` from bash shows fewer lines than `Read` shows
- `git` commands fail with "unterminated line" or similar parser errors on `.git/` internal files
- Bash commands behave as if your latest write didn't happen, while Read shows it did

## The Workarounds

**For writes:** Prefer `bash` heredoc (`cat > path << 'EOF' ... EOF`) over the `Write` tool when the file is large (>5 KB) or contains many backticks/special chars. Heredoc writes go through the Linux mount directly and are visible to subsequent bash commands immediately.

**For verifying writes:** After a `Write` or `Edit`, validate via `bash` (`wc -c`, `node --check`, `python3 -c "open(p).read()"`). Don't trust the Read tool's view alone — it's the host's view, not the bash mount's.

**For corrupted `.git` files (e.g. packed-refs with trailing nulls):**
```
python3 -c "
import sys
p = '.git/packed-refs'
data = open(p, 'rb').read()
clean = data.rstrip(b'\\x00')
if not clean.endswith(b'\\n'): clean += b'\\n'
open(p, 'wb').write(clean)
print(f'Truncated {len(data)} → {len(clean)} bytes')
"
```

This strips trailing nulls from any binary-corrupted file. Adjust the path for the affected file.

## Prevention

- Big code/text files: write via `bash` heredoc rather than the Write tool.
- After ANY write, do a `node --check` (for JS/TS), `python3 -m py_compile` (for Python), or at least `wc -c` to confirm bash sees the file at the expected size.
- Before any `git` operation against a freshly-cloned repo, give the host-side filesystem ~1–2 seconds to settle, then run `git status` from bash to confirm the working tree looks clean.

## Why This Mattered Here

- Cost ~15 minutes during the Insights theme work (truncated `.user.js` write, multiple node-check failures).
- Cost another ~5 minutes after the Insights clone (packed-refs corruption blocking `git branch`/`git status`).
- Both fixed once recognised, but easy to misdiagnose as "my edit didn't take" or "git is broken".

The pattern: **trust the bash view as ground truth for anything that will be consumed by tooling (compilers, git, build systems). Use the Read tool's view only for human reading.**
