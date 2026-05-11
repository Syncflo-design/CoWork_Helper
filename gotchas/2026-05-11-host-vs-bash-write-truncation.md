# Write tool overwrite with smaller content can leave NULL-padded tail on bash mount

**Date:** 2026-05-11
**Domain:** Cowork mode — host Write/Edit tool vs Linux bash mount
**Severity:** annoying (silent corruption of JSON/JS files that parses-ish but breaks tooling)

## Symptom

You overwrite a file via the Write tool (host) with **smaller** content than the previous version. The host-side Read tool shows the new, shorter content correctly. But on the bash mount, the file's on-disk size is still the OLD length, with the difference padded by trailing NULL bytes (`\x00`).

Downstream symptoms when a parser hits the file:

```
$ python3 -c "import json; json.load(open('hooks.py.json'))"
json.decoder.JSONDecodeError: Extra data: line 47 column 1 (char 1823)

$ node -e "JSON.parse(require('fs').readFileSync('hooks.json','utf-8'))"
SyntaxError: Unterminated string in JSON at position 1820
```

Or, less specifically:

```
$ bench migrate
... CompileError ...
SyntaxError: invalid syntax (some_file.py, line 47)
```

…where line 47 is somewhere shortly after the legitimate file content ends.

Sister symptom: `wc -c` on bash shows a byte count larger than the line-by-line content suggests. A `hexdump -C <file> | tail` reveals a trailing run of `00 00 00 00 …`.

## Cause

The host filesystem and the Linux mount in Cowork mode have a "second-mover" pattern for some writes. When the host's Write tool overwrites with shorter content, the new bytes land correctly but the **file size metadata on the bash mount isn't updated atomically** — instead the tail of the old content gets zeroed-out in place, leaving NULLs from the new end-of-content up to the old length.

For human readers (and the host Read tool), this is invisible: trailing NULLs don't render. For parsers reading the raw bytes — JSON, `node --check`, `python3 -m py_compile`, `git hash-object`, anything that respects file length — the NULL run is treated as garbage AFTER the real content. JSON parsers complain about "Extra data". JS parsers complain about an unterminated string. Python often reports `invalid syntax` at the line after content ends.

This is closely related to (but distinct from) the **truncation** failure mode in `gotchas/2026-05-06-host-vs-bash-fs-sync.md`. That one is: file ends shorter than intended. This one is: file is the OLD length but the tail is NULL padding. Both stem from the same host-vs-mount drift but produce opposite-shaped failures.

## Fix

After ANY Write-tool overwrite where the new content is smaller than the previous version:

```bash
# 1. Detect: file size on bash differs from host's actual content length
ls -l <file>            # how big does bash think it is?
wc -c <file>            # same number — but does this match what Read shows?
hexdump -C <file> | tail # any trailing 00 00 00 ...?

# 2. Clean fix from bash — read what's there, strip NULLs, rewrite
python3 -c "
p = '<file>'
data = open(p, 'rb').read()
clean = data.rstrip(b'\\x00')
open(p, 'wb').write(clean)
print(f'{len(data)} -> {len(clean)} bytes')
"
```

Or, easier in many cases: re-Write the file via the Write tool with the same content. A clean overwrite at the same length usually clears the NULL padding because the size metadata gets refreshed on the second write. (Not 100% reliable but often works.)

## Why this is non-obvious

Three things make this hard to spot:

1. **The host Read tool hides it.** Read returns text content, NULLs are non-printing, so the file looks correct on the host side. You'll swear your write went through fine.
2. **`git diff` may or may not show it.** Depending on how git treats trailing NULLs (often as a binary diff or as no-change), the diff output is misleading. You can `git commit` a file that looks clean and have it still be corrupted on the bash mount until the next checkout.
3. **The parser error points at a plausible-looking line.** "Unterminated string at line 47" makes you re-read line 47 carefully, looking for a missing quote — instead of looking at the bytes AFTER line 47.

A specific tell: if your error is at a line number `N+1` where `N` is the last line of the actual content, and you can SEE the file is complete, and the file ends in a newline — strongly suspect NULL padding. Run `hexdump -C <file> | tail -5` and confirm.

## Detection recipe

After any Write tool overwrite of an existing file:

```bash
# Quick check on bash side:
F=<path>
HOST_LINES=$(wc -l < "$F")
echo "Lines: $HOST_LINES"
hexdump -C "$F" | tail -3
# If you see a line ending in "00 00 00 00  ..." that's the trailing NULL tail.
```

For JSON/Python/JS files where you're about to feed them to a parser/build:

```bash
# Validate immediately after write:
python3 -c "import json; json.load(open('$F'))"        # JSON
node --check "$F"                                      # JS / JSON
python3 -m py_compile "$F"                             # Python
```

If validation fails on a parse error pointing at a line near (or after) the end of legitimate content — apply the rstrip-NULL fix above.

## When this is most likely to bite

- You're iterating on a config / fixture JSON, repeatedly shrinking it as you simplify.
- You're trimming a JS file (removed a function, replaced a verbose block with a one-liner).
- You're refactoring a Python file down to a smaller version.
- ANY case where Write replaces content with strictly shorter content than the previous version.

Append-only writes don't seem to trigger this. Same-length writes don't trigger it. It's the shrink-overwrite case that's the trap.

## See also

- `gotchas/2026-05-06-host-vs-bash-fs-sync.md` — the original host-vs-bash sync gotcha. That one covers truncation (file ends shorter than intended) and `.git/` corruption. This entry extends it with the NULL-padding mode for shrink-overwrites.
- `gotchas/2026-05-06-bash-vs-windows-git-ownership.md` — distinct but related family of host/sandbox quirks under Cowork mode.
- General prevention strategy in `CLAUDE.md`: trust the bash view as ground truth for anything that will be consumed by tooling; the Read tool's view is for human reading.
