# CoWork_Helper — Russell's working knowledge base

You are an AI assistant working with Russell on building his company. This folder is the persistent memory across all his projects. **Read this file first** in any session that touches Frappe, ERPNext, custom apps, or anything else covered below — it will save hours of repeated mistakes.

## What this folder is

A growing playbook of real lessons from real projects. Every entry was written *because* something failed first. Treat the contents as authoritative — if a gotcha here contradicts what you'd otherwise guess, the gotcha is right.

## Layout

```
CoWork_Helper/
├── CLAUDE.md           ← you are here. The entrypoint.
├── README.md           ← human-readable index
├── skills/             ← Claude-specific skills (auto-loadable)
├── playbooks/          ← long-form how-tos, model-neutral Markdown
├── gotchas/            ← short "this bit me, here's the fix" entries
├── templates/          ← reusable JSON / SQL / Python / config snippets
└── sites/              ← per-site notes (Frappe instances, credentials hints, quirks)
```

## How to use this in any session

1. **At session start** — read this file, then `README.md` to see the current index.
2. **Before tackling a task** — search `playbooks/` and `gotchas/` for the topic. Examples of good searches: "insights", "doctype", "frappe-cloud", "custom app", "site name".
3. **After hitting a snag and fixing it** — write the lesson down. See `templates/gotcha-template.md` and `templates/playbook-template.md`. This is the most important habit. If we don't capture it, we'll repeat it.
4. **When a topic gets thick enough** — promote a cluster of gotchas into a playbook, and a thick playbook into a skill.

## Cross-model note

Skills under `skills/` use Claude's auto-discovery format — Claude (this assistant) reads their `SKILL.md` when the description matches. Other LLMs (ChatGPT, Gemini, Cursor's models) can read the same content as plain Markdown:
- Tell them "Read `C:\ClaudeCode\CoWork_Helper\CLAUDE.md` first, then look for the relevant playbook"
- Or paste the relevant `playbooks/*.md` or `gotchas/*.md` into the chat
- The `playbooks/` folder is intentionally the same content as the skills, written in plain Markdown without Claude-specific frontmatter, so any model can use it

## Domains covered (and growing)

- **Frappe Insights v3** — dashboards, queries, charts. See `skills/frappe-insights-v3-dashboard/` and `playbooks/insights-v3.md`.
- **Frappe Insights v3 server-side theming** — fork-overlay pattern, Frappe Cloud deploy. See `playbooks/insights-fork-themeing.md` (verified live).
- **Frappe / ERPNext via MCP** — patterns for working over the Frappe REST/MCP connectors. See `playbooks/frappe-mcp-patterns.md` (forthcoming).
- **Frappe v16 custom apps** — scaffolding new Frappe apps from scratch (file layout, `pyproject.toml`, hooks.py, DocType JSON, child tables, deploy on Frappe Cloud). See `playbooks/frappe-custom-app-v16.md`.
- **Cowork-mode tooling quirks** — host vs bash sync, Git Bash bracketed-paste. See `gotchas/2026-05-06-host-vs-bash-fs-sync.md` and `gotchas/2026-05-06-git-bash-bracketed-paste.md`.
- *(more as we add them)*

## Working style

Russell prefers:
- **Action over chat.** When he asks for a fix, edit the actual files / call the actual APIs — don't paste code into chat for him to apply.
- **No empty content in demos.** If a chart returns 0 rows, remove it rather than ship a blank tile.
- **Honest reporting.** When something can't be done, say so plainly. Don't pretend a chat-only response is a delivered file.
- **Short responses unless depth is asked for.** No bullet-point bloat for casual replies.

## Active projects

| Site | Domain | Notes |
|---|---|---|
| `blomoplastics.jh.frappe.cloud` | Plastics manufacturer | Insights v3 — Manufacturing Ops + MD Overview dashboards live; **server-side soft-professional theme deployed via custom Insights fork** (`Syncflo-design/insights:syncflo-custom-theme`). See `sites/blomoplastics.md` and `playbooks/insights-fork-themeing.md`. |
| `ardmore.jh.frappe.cloud` | TBD | Frappe MCP connected, no work logged yet |
| `comstruct.jh.frappe.cloud` | TBD | Frappe MCP connected, no work logged yet |
| `syncflo-internal.c.frappe.cloud` (custom: `www.nesterp.co.za`) | Syncflo internal ERPNext (Frappe v16) | Site name on Frappe Cloud is `Syncflo_internal_V16`. `quick_purchase_invoice` custom app deployed 2026-05-06. `nest_theme` v0.3.0 — 5-palette switcher (Soft Pro / Crisp / Warm Earth / Corp Navy / Minimal Mono) + tightened section headers + customer logo branding (admin-only, realtime swap; deployed 2026-05-07). `nest_crm_tasks` v0.0.3 — Lead Activity Hub + custom My Activities page (replaces standard ToDo list for sales reps; one-click flow to a lead's full activity history; pushed 2026-05-11, **deploy underway, smoke test pending**). See `sites/nesterp.md`, `projects/quick_purchase_invoice/`, `projects/theme_studio/`. |
| `*.demo` | Demo data | Used for prototyping |

## Project sketches (designed, build pending)

| Project | Status |
|---|---|
| `projects/quick_purchase_invoice/` | Built, deployed to nesterp 2026-05-06. v0.0.4. |
| `projects/theme_studio/` | **v0.3.0 — 2026-05-07.** `nest_theme` custom Frappe v16 app at `C:\ClaudeCode\nest_theme`. **5 palettes** (Soft Professional, Accounting Crisp, Warm Earth, Corporate Navy, Minimal Mono) each with light + dark, admin-only switcher via Settings, realtime swap on save. Tightened section headers + customer logo branding from v0.2 carried forward. v0.1 widgets retired (v16 navbar click interception — see `gotchas/2026-05-07-frappe-v16-modern-desk-click-interception.md`). See `SCOPE.md` (full build log v0.1 → v0.3.0) + `DEPLOY.md`. |
| `nest_crm_tasks` | **v0.0.3 — 2026-05-11.** Frappe v16 custom app at `C:\Users\Russell - Manifold\nest_crm_tasks`. Repo: [Syncflo-design/nest_crm_tasks](https://github.com/Syncflo-design/nest_crm_tasks). Two desk Pages: **Lead Activity Hub** (`/desk/lead-activity/<lead>`) — header card + activity table of all ToDos linked to a Lead, with mark-complete / reopen / add-task per row. **My Activities** (`/desk/my-activities`) — custom replacement for standard ToDo list; Lead-linked rows get blue clickable `[👤 CRM-LEAD-...]` pill linking to Lead Activity Hub. Filters (My/All × Open/Closed/Any) persisted to localStorage. Replaces ToDo workspace shortcut for sales reps. Built as a Page because v16 modern desk strips HTML from `listview_settings.formatters` returns — see `gotchas/2026-05-11-frappe-v16-listview-formatters-stripped-to-text.md` and the meta-gotcha `gotchas/2026-05-11-frappe-v16-modern-desk-listview-hooks-untrustworthy.md`. |

## When you finish a task

If you learned something non-obvious, capture it before the session ends:
- **One-off snag** → write a `gotchas/YYYY-MM-DD-short-name.md` using the gotcha template.
- **Reusable workflow** → write a `playbooks/<topic>.md` using the playbook template.
- **Whole subsystem mastered** → wrap it as a `skills/<name>/SKILL.md` with templates so future sessions auto-load it.

If a session involved several site-specific decisions, append a dated section to `sites/<site>.md`.

The cost of writing a 5-line gotcha is small. The cost of re-debugging the same issue in three months is large. Always pay forward.
