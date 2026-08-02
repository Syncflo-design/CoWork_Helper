# Start-of-task prompt

Paste `start-prompt.txt` at the start of any new Cowork / Claude session. It works from
any machine — it prefers the local clone when present, and falls back to GitHub raw
otherwise.

## Keeping it short

On a machine with the local clone, steps 1–2 are largely redundant: `C:\ClaudeCode\CLAUDE.md`
and `C:\ClaudeCode\CoWork_Helper\CLAUDE.md` auto-load into every session already. The full
prompt exists for **other** machines and for web/mobile Claude, where nothing auto-loads.

Once `graphify-out/` is committed (see below), the local-machine version collapses to:

```
Query the CoWork_Helper graph before answering. We're working on: [TOPIC].
```

## Graphify

`graphifyy` is installed via `uv tool install graphifyy`; the skill lives at
`C:\Users\User\.claude\skills\graphify\SKILL.md` and is registered in the global CLAUDE.md.

The graph is built from **inside a Claude session**, not from Git Bash. The `graphify`
CLI only installs/uninstalls the skill and runs maintenance sub-commands (`update`,
`path`, `explain`, `merge-graphs`) — there is no bare `graphify <path>` build command.

Build the knowledge-base graph once, then let sessions query it instead of re-reading a
26 KB README. In a Claude Code chat opened at `C:\ClaudeCode`:

```
/graphify CoWork_Helper
```

Refresh it after a batch of new gotchas — either re-run the skill, or from Git Bash:

```bash
graphify update /c/ClaudeCode/CoWork_Helper
```

Outputs land in `CoWork_Helper/graphify-out/` (interactive HTML, GraphRAG JSON,
`GRAPH_REPORT.md`). Commit that folder so other machines and the web client get the
same index.

## Why the prompt says "the README index lags"

`README.md` is hand-maintained and currently misses several committed and uncommitted
entries (the 2026-05-27/28 and 2026-06-10 gotchas, two playbooks, `sites/ardmore.md`).
Listing the directories is authoritative; the README is a convenience.

---

See `start-prompt.txt` for the paste-ready text.
