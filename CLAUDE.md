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
- **Short, direct answers.** No filler, no "blah blah", no option-menus. Give the single best production-grade choice. Ask only when genuinely unsure.
- **Action over chat.** When he asks for a fix, edit the actual files / call the actual APIs — don't paste code into chat for him to apply.
- **Never hand back code you haven't checked.** Always syntax-check before reporting it done.
- **No empty content in demos.** If a chart returns 0 rows, remove it rather than ship a blank tile.
- **Honest reporting.** When something can't be done, say so plainly. Don't pretend a chat-only response is a delivered file.
- **Short responses unless depth is asked for.** No bullet-point bloat for casual replies.

## Git / deploy conventions (Russell's machines)

- Git is run from **Git Bash (MINGW64)** on Windows. Use forward-slash paths: `cd /c/ClaudeCode/<repo>`. Backslash Windows paths get mangled.
- **Do NOT run git from the Linux bash sandbox** — `.git` was created by Windows and pushes fail. Hand Russell the commands; he runs them locally.
- Default branch is **per-repo**: `nest_crm_tasks` pushes to `main`; Frappe Cloud bench apps (`custom_subscription`, etc.) often use `version-16`. Confirm with `git branch` if unsure.
- After pushing a Frappe Cloud app, trigger a **fresh Deploy** (not just "Update") — Update runs migrations but skips `bench build`, so page JS/CSS stays stale.
- Host (Read/Write/Edit) and the Linux `bash` mount can desync **either way** — a host write can truncate, or the bash mount can serve a stale/truncated copy with an old mtime (remount doesn't reliably fix it). Route syntax checks through the fresh **outputs** mount. See `gotchas/2026-05-06-host-vs-bash-fs-sync.md` and `gotchas/2026-05-22-bash-mount-stale-not-host.md`.

## Active projects

| Site | Domain | Notes |
|---|---|---|
| `blomoplastics.jh.frappe.cloud` | Plastics manufacturer | Insights v3 — Manufacturing Ops + MD Overview dashboards live; **server-side soft-professional theme deployed via custom Insights fork** (`Syncflo-design/insights:syncflo-custom-theme`). See `sites/blomoplastics.md` and `playbooks/insights-fork-themeing.md`. |
| `ardmore.jh.frappe.cloud` | TBD | Frappe MCP connected, no work logged yet |
| `comstruct.jh.frappe.cloud` | TBD | Frappe MCP connected, no work logged yet |
| `syncflo-internal.c.frappe.cloud` (custom: `www.nesterp.co.za`) | Syncflo internal ERPNext (Frappe v16) | Site name on Frappe Cloud is `Syncflo_internal_V16`. `quick_purchase_invoice` custom app deployed 2026-05-06. `nest_theme` v0.3.2 — 6-palette switcher (Soft Pro / Crisp / Warm Earth / Corp Navy / Minimal Mono / Sage-inspired) + tightened section headers + customer logo branding (admin-only, realtime swap; deployed 2026-05-07). `nest_crm_tasks` **v0.0.4** — Lead Activity Hub + custom My Activities page (replaces standard ToDo list for sales reps; one-click flow to a lead's full activity history). v0.0.3 hit the page-api-drift Variant 2 (silent empty body) — fixed in v0.0.4 by mounting `$main` inside `page.body` instead of looking for a class that wasn't there. See `gotchas/2026-05-10-frappe-v16-page-api-drift.md`. **2026-05-11: v0.0.4 fix on disk, push + deploy + smoke pending.** **CRITICAL — `erpnext_sbca`:** Russell's Sage ↔ ERPNext bridge, written by Doreen (9t9it). Two-way sync with Sage Business Cloud Accounting — pulls items/prices/stock/suppliers/accounts/sales-orders/purchase-orders from Sage and pushes item price changes back. Per-Company credentials in Settings. On nesterp it's installed but the Settings panel is still empty, so the 11 sync jobs no-op. **Do not stop the jobs / uninstall.** Plain-English overview: `projects/erpnext_sbca/ASSESSMENT.md`. Audit recipe + lesson on inherited Frappe apps: `gotchas/2026-05-12-frappe-chatty-cron-on-unconfigured-third-party-app.md`. **2026-05-14: payment reconciliation + customer/supplier category->group sync built & deployed — see `projects/erpnext_sbca/PAYMENT_RECONCILIATION_DESIGN.md` and `ASSESSMENT.md`.** **2026-05-20/21: `custom_subscription`** — assessed & repaired Chipo Hameja's recurring-billing app (daily scheduler -> Sales Order / Sales Invoice draft|submitted + email to recipients). Fixed the `== today` scheduler match (missed days skipped forever) to `<=` + per-sub try/except, guarded `before_save`, corrected the next-date step, and fixed `send_email` (was attaching the subscription, not the invoice). Added `end_date` auto-stop, Accounts Manager/User perms, a **UAT-only `Daily`** frequency, `print_format` editable-on-submit, an Open-document link in the email, and a **07:00 SAST cron**. Repo `Syncflo-design/custom-subscription` (branch `version-16`), local `C:\ClaudeCode\custom-subscription`. Batch-1 deployed & verified; batch-2 (print_format/link/cron) pending the Frappe Cloud bench->site propagation issue. See `sites/nesterp.md`, `projects/quick_purchase_invoice/`, `projects/theme_studio/`. |
| `*.demo` | Demo data | Used for prototyping |

## Project sketches (designed, build pending)

| Project | Status |
|---|---|
| `projects/quick_purchase_invoice/` | Built, deployed to nesterp 2026-05-06. v0.0.4. |
| `projects/theme_studio/` | **v0.3.2 — 2026-05-07.** `nest_theme` custom Frappe v16 app at `C:\ClaudeCode\nest_theme`. **6 palettes** (Soft Professional, Accounting Crisp, Warm Earth, Corporate Navy, Minimal Mono, Sage-inspired) each with light + dark, admin-only switcher via Settings, realtime swap on save. Sage-inspired is an unofficial Sage-Business-Cloud-lookalike for the `erpnext_sbca` bridge (disclaimer in Settings field). Tightened section headers + customer logo branding. v0.1 widgets retired (v16 navbar click interception). v0.3.1 fixed realtime-listener timing (`gotchas/2026-05-07-frappe-v16-realtime-registration-timing.md`). See `SCOPE.md` (full build log v0.1 → v0.3.2) + `DEPLOY.md`. |
| `nest_crm_tasks` | **v0.0.4 — 2026-05-11.** Frappe v16 custom app at `C:\ClaudeCode\nest_crm_tasks` (Dell — primary dev machine going forward). Repo: [Syncflo-design/nest_crm_tasks](https://github.com/Syncflo-design/nest_crm_tasks). Two desk Pages: **Lead Activity Hub** (`/desk/lead-activity/<lead>`) — header card + activity table of all ToDos linked to a Lead, with mark-complete / reopen / add-task per row. **My Activities** (`/desk/my-activities`) — custom replacement for standard ToDo list; Lead-linked rows get blue clickable `[👤 CRM-LEAD-...]` pill linking to Lead Activity Hub. Filters (My/All × Open/Closed/Any) persisted to localStorage. Replaces ToDo workspace shortcut for sales reps. Built as a Page because v16 modern desk strips HTML from `listview_settings.formatters` returns — see `gotchas/2026-05-11-frappe-v16-listview-formatters-stripped-to-text.md` and the meta-gotcha `gotchas/2026-05-11-frappe-v16-modern-desk-listview-hooks-untrustworthy.md`. **v0.0.3 → v0.0.4 fix**: both pages had `$main = $(wrapper).find('.<class>')` against a class nothing created → empty jQuery collection → all `.html()` / `.on()` silently no-op. Page chrome rendered, body stayed empty, no console errors. Fixed by creating the container explicitly inside `page.body`. See variant 2 of `gotchas/2026-05-10-frappe-v16-page-api-drift.md`. |
| `nest_home` | **v0.0.1 — built 2026-05-20, deploy pending.** Reusable **NestERP standard** Frappe v16 app at `C:\ClaudeCode\nest_home`. Role-based, branded landing page on the *push-not-pull* principle. **Attention engine** (`api.py` + `attention/`): one normalised item schema (`schema.py`) + pluggable sources — `todos.py` (List A: ToDos allocated to me, Open; List C: ToDos I assigned to others, Open) and `awaiting.py` (List B: rules table `AWAITING_RULES`, v1 = Draft Sales/Purchase/Work Orders the user can submit; each rule guarded so a missing doctype never breaks the board). Whitelisted methods return truthy. Desk **Page** `/desk/nest-home` paints List A first then B/C, quick-launch tiles, rewarding empty states, quiet poll; CSS split from JS; built on the `nest_crm_mobile` page-bundle rules + `my_activities` ToDo pattern. Doctypes **Nest Home Settings** (Single) + **Nest Home Tile** (data-driven tiles). `role_home_page` + per-user **Preferred Landing Page** Select on User, resolved in `boot.py` (user pref → role default → app default) via `get_website_user_home_page` (verify desk-user behaviour on first deploy). Branding: Nest Home Settings logo wins, else `nest_theme` `customer_logo`; reuses nest_theme palette vars. Repo: Syncflo-design/nest_home (push from Windows — sandbox can't git-init on the mount,  see `gotchas/2026-05-20-cowork-sandbox-cannot-git-init-on-windows-mount.md`). **2026-05-21 fix:** the `Nest Home Layout Tile` child DocType shipped without its controller `.py`, crashing every site migrate with `ModuleNotFoundError` and blocking unrelated apps' deploys (incl. `custom_subscription`). Added the controller; see `gotchas/2026-05-21-frappe-doctype-missing-controller-crashes-migrate.md`. |
| `custom_subscription` | **Assessed + fixed 2026-05-20/21.** Recurring-billing engine (Business Subscription + 2 child tables) — daily scheduler creates Sales Order / Sales Invoice (draft|submitted) and emails recipients. Repaired the stuck-forever `== today` scheduler (-> `<=` + per-sub try/except), the `before_save` date-rewind, the wrong date step, and the email-attaches-wrong-doc bug. Added `end_date` auto-stop, Accounts Manager/User perms, a **UAT-only `Daily`** cadence, `print_format` editable-on-submit, an Open-document email link, and a **07:00 SAST cron** (`hooks.py` `0 7 * * *`). Repo `Syncflo-design/custom-subscription` branch **`version-16`**, local `C:\ClaudeCode\custom-subscription`. Batch-1 live; batch-2 pending Frappe Cloud bench->site propagation. Full log: `sites/nesterp.md`. Gotchas: `gotchas/2026-05-20-frappe-deploy-overwrites-doctype-permissions.md`, `gotchas/2026-05-20-gitbash-windows-path-and-default-branch.md`. |

## When you finish a task

If you learned something non-obvious, capture it before the session ends:
- **One-off snag** → write a `gotchas/YYYY-MM-DD-short-name.md` using the gotcha template.
- **Reusable workflow** → write a `playbooks/<topic>.md` using the playbook template.
- **Whole subsystem mastered** → wrap it as a `skills/<name>/SKILL.md` with templates so future sessions auto-load it.

If a session involved several site-specific decisions, append a dated section to `sites/<site>.md`.

The cost of writing a 5-line gotcha is small. The cost of re-debugging the same issue in three months is large. Always pay forward.
