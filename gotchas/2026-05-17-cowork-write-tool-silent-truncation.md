# Cowork mode: Write / Edit tools silently truncate files around ~20 KB

**Family:** Cowork host/bash sync (related to `2026-05-06-host-vs-bash-fs-sync.md`)
**Affects:** Any file the Cowork host writes via `Write` or `Edit` tools larger than ~15–20 KB
**Date discovered:** 2026-05-17 — during `nest_crm_mobile` v0.1 build and `DEMO_LAUNCHER.html` v05-CRM section add

## Symptom

- `Write` or `Edit` reports success — no error, no warning, no truncation indicator
- The `Read` tool shows the file as **complete** (because Read serves the harness's tracked intent, not what's on the actual disk)
- bash sees the file is truncated mid-line at around 20,000–21,000 bytes
- For JS files: `node --check` from bash fails near the end with `Invalid or unexpected token`, caret pointing at a truncated string literal
- For HTML files: closing tags, the `<script>` block, and end-of-file `</body></html>` are missing
- Whatever Russell pushes from Windows Git Bash is the truncated version, because the disk is the source of truth for git

## What's happening

The Cowork host's Write / Edit tools serialise the file through a pipeline that silently truncates somewhere around the 20 KB mark. The harness keeps a complete tracked-state of what the file *should* be, so the Read tool reassures you that everything is fine. Git, the browser, Frappe Cloud, and `node` all read the actual disk, which has whatever fit through the pipeline.

This is the same family as `2026-05-06-host-vs-bash-fs-sync.md` (host vs. bash mount can desync) but with two important refinements:

1. The cap is around **~20 KB**, not the 13 KB previously assumed
2. The truncation also bites `Edit` calls that grow a file past the cap, not just fresh `Write`s

## Fix — write big files via bash heredoc

Bash talks to the real disk directly and has no size cap.

```bash
cat > path/to/file.ext <<'EOF_UNIQUE_MARKER'
... full file content ...
EOF_UNIQUE_MARKER
```

Use a **single-quoted** heredoc delimiter (`'EOF_UNIQUE_MARKER'`) so bash treats the content as literal — no `$` interpolation, no backtick eval, no escape processing.

### If the file is too big for one heredoc, split + concat

```bash
cat > /tmp/file_head.txt <<'EOF_PART1'
... first half ...
EOF_PART1

cat > /tmp/file_tail.txt <<'EOF_PART2'
... second half ...
EOF_PART2

cat /tmp/file_head.txt /tmp/file_tail.txt > path/to/file.ext
```

### If a file is already broken on disk, keep the good lines and append the missing tail

```bash
head -n <last_good_line_number> path/to/file.ext > /tmp/keep.txt
cat > /tmp/tail.txt <<'EOF_TAIL'
... missing tail content here ...
EOF_TAIL
cat /tmp/keep.txt /tmp/tail.txt > path/to/file.ext
```

## Verify after every big write

```bash
wc -c path/to/file.ext       # size matches expectation?
wc -l path/to/file.ext       # line count matches?
tail -5 path/to/file.ext     # ends with the expected closing tags / braces?
node --check path/to/file.js # syntax valid (for JS)
```

The Read tool's view is **not reliable** for big-file verification — always cross-check via bash.

## Rule of thumb

| File size | Approach |
|---|---|
| < 15 KB | `Write` / `Edit` is fine |
| 15–20 KB | `Write` is risky but usually OK — always verify via bash after |
| > 20 KB | Use bash heredoc from the start, or split across multiple `Write`s + bash `cat` to assemble |

## Why this matters

A truncated file on disk gets pushed to GitHub, built by Frappe Cloud, served to the browser, and breaks on stage. The Read tool reassures you the file is fine the whole time. The first sign of trouble is a blank page, a `node --check` failure, or a missing `<script>` block — by which point you've burned 30+ minutes assuming the deploy or the framework was at fault.

For a five-minute build cycle that's irritating. For a demo-tomorrow build cycle it's a disaster.

## Real-world bites

- **2026-05-17, `nest_crm_mobile/.../crm_mobile.js`** — Write tool reported success at 20,677 bytes; file was actually truncated mid-string inside the `loadDrafts` method. Discovered when `node --check` failed. Fixed by full rewrite via bash heredoc (file grew to 21,218 bytes when properly written).
- **2026-05-17, `DEMO_LAUNCHER.html`** — `Edit` call adding the section-05 card to a ~26 KB file produced a 27.5 KB file on disk, but the disk version was truncated mid-string inside the presenter notes, missing the closing `</div>`s, footer, and entire `<script>` block. Fixed by `head -n 584` + heredoc-append of the missing tail.

## See also

- `gotchas/2026-05-06-host-vs-bash-fs-sync.md` — the broader Cowork host/bash desync gotcha (this entry is a specific, more aggressive case)
- `production_floor/CLAUDE.md` — operational guidance referenced in every NestERP custom-app session
- `nest_crm_mobile/CLAUDE.md` — repeat of this gotcha, app-scoped (already in the repo)
