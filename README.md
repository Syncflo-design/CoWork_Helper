# CoWork_Helper

Russell's working knowledge base for AI-assisted development. Every entry here was earned through a failure that won't happen twice.

If you're an AI assistant: read `CLAUDE.md` first.
If you're a human: this is the index.

## First-time setup (run once per machine)

Double-click **`install.bat`** (or run `install.ps1` in PowerShell). It:

1. Hard-links every skill in `skills/` into Claude's user-skills directory so Cowork auto-discovers them in every chat.
2. Creates a desktop shortcut **"Cowork start-prompt"** that copies the knowledge-base opener to your clipboard.

After install, the workflow per new chat is:

- **For skill-covered topics** (Insights v3 dashboards, etc.): just describe the task in normal language. The skill auto-loads on description match — no setup prompt needed.
- **For everything else** (gotchas, playbooks, sites, ad-hoc lookups): double-click the desktop shortcut → switch to Cowork → Ctrl+V → fill in the `[TOPIC]` placeholder → send. The AI then mounts this folder and reads `CLAUDE.md`.

Re-run `install.bat` any time you add a new skill (junctions stay live, but the script also creates fresh ones for new folders).

## Index

### Skills (Claude auto-loadable)

| Skill | What it covers |
|---|---|
| [`frappe-insights-v3-dashboard`](skills/frappe-insights-v3-dashboard/SKILL.md) | Build dashboards in Frappe Insights v3 via API/MCP — queries, charts, layout |

### Playbooks (model-neutral)

| Playbook | What it covers |
|---|---|
| [`insights-v3.md`](playbooks/insights-v3.md) | Same content as the Insights skill, plain Markdown for non-Claude LLMs |
| [`insights-fork-themeing.md`](playbooks/insights-fork-themeing.md) | Minimal-fork strategy for theming Insights v3 server-side (all users, all devices). Covers the additive-overlay pattern, exact files to add/edit, deploy steps on Frappe Cloud, and update procedure |
| [`frappe-custom-app-v16.md`](playbooks/frappe-custom-app-v16.md) | Scaffolding a Frappe v16 / ERPNext v16 custom app from scratch — file layout, `pyproject.toml`, hooks.py, DocType JSON, child tables, form scripts, deploy via Frappe Cloud |
| [`frappe-role-based-access-control.md`](playbooks/frappe-role-based-access-control.md) | Creating restricted custom roles that truly remove DocType access (incl. search) — full provisioning process, reusable across all company instances |

### Gotchas (short fix-it entries)

| Date | Entry | One-line summary |
|---|---|---|
| 2026-05-06 | [`insights-code-vs-sql.md`](gotchas/2026-05-06-insights-code-vs-sql.md) | Insights v3 `code` op runs Python, not SQL — use `type:"sql"` with `raw_sql` |
| 2026-05-06 | [`insights-data-query-empty-stub.md`](gotchas/2026-05-06-insights-data-query-empty-stub.md) | Chart `data_query` is auto-created empty; charts won't render until you set its operations |
| 2026-05-06 | [`insights-dashboard-layout-i-key.md`](gotchas/2026-05-06-insights-dashboard-layout-i-key.md) | Dashboard `items` layout needs unique `i` key per item or vue-grid-layout silently drops it |
| 2026-05-06 | [`insights-table-needs-rows-values.md`](gotchas/2026-05-06-insights-table-needs-rows-values.md) | Table charts on a dashboard need explicit `rows` + `values` config; standalone view is more forgiving |
| 2026-05-06 | [`insights-kpi-friendly-label.md`](gotchas/2026-05-06-insights-kpi-friendly-label.md) | Number-card KPI label comes from `measure_name` — set it to a friendly string, not the column name |
| 2026-05-06 | [`insights-spa-no-frappe-runtime.md`](gotchas/2026-05-06-insights-spa-no-frappe-runtime.md) | Insights v3 is a standalone Vue SPA — Client Scripts, head_html, Server Scripts all fail; use Tampermonkey OR the fork-overlay (see playbook) |
| 2026-05-06 | [`git-bash-bracketed-paste.md`](gotchas/2026-05-06-git-bash-bracketed-paste.md) | Git Bash on Windows mangles pasted multi-line commands with `^[[200~`; type the first command by hand or disable bracketed-paste in `~/.inputrc` |
| 2026-05-06 | [`host-vs-bash-fs-sync.md`](gotchas/2026-05-06-host-vs-bash-fs-sync.md) | Cowork mode: Read/Write tools (host) and bash mount (Linux) can desync — truncated writes, packed-refs corruption. Verify writes via bash; prefer heredoc for big files |
| 2026-05-06 | [`frappe-dynamic-link-in-grid.md`](gotchas/2026-05-06-frappe-dynamic-link-in-grid.md) | Per-row Dynamic Link in a Frappe grid needs a hidden Link-to-DocType helper field synced from a form-script when the visible Select changes |
| 2026-05-06 | [`erpnext-purchase-invoice-blank-item-row.md`](gotchas/2026-05-06-erpnext-purchase-invoice-blank-item-row.md) | ERPNext Purchase Invoice rows can omit `item_code` if you supply `item_name`/`expense_account`/`uom`; enables direct GL-expense rows without a placeholder Item |
| 2026-05-06 | [`mcp-user-restricted-doctypes.md`](gotchas/2026-05-06-mcp-user-restricted-doctypes.md) | Frappe Cloud MCP API user can't read `Company`/`DocField`/`Account` directly; cross-reference via `Purchase Taxes and Charges Template` etc., final smoke testing has to happen on the bench |
| 2026-05-06 | [`bat-needs-pause-to-debug.md`](gotchas/2026-05-06-bat-needs-pause-to-debug.md) | A double-clicked `.bat` flashes its CMD window and closes — `pause` at the end (and on error paths) keeps it open so you can see what happened |
| 2026-05-06 | [`bash-vs-windows-git-ownership.md`](gotchas/2026-05-06-bash-vs-windows-git-ownership.md) | Linux bash sandbox can't `git push` a repo whose `.git/` was created by Windows; do all git plumbing from Windows, use `git reset HEAD` to recover from half-staged state |
| 2026-05-06 | [`frappe-cloud-update-vs-deploy-assets.md`](gotchas/2026-05-06-frappe-cloud-update-vs-deploy-assets.md) | Frappe Cloud's "Update" runs migrations but skips `bench build`, so changes under `public/` (CSS/JS) stay stale — trigger a fresh Deploy, or SSH and run `bench build --app <name>` |
| 2026-05-06 | [`frappe-cloud-cdn-stale-assets.md`](gotchas/2026-05-06-frappe-cloud-cdn-stale-assets.md) | Even after a clean Deploy, Frappe Cloud's CDN can keep serving the old `app_include_css` content. Cache-bust with `?v=N` to confirm; permanent fix is to rename the asset file or migrate to `.bundle.css` |
| 2026-05-06 | [`insights-dashboard-filter-needs-source-column.md`](gotchas/2026-05-06-insights-dashboard-filter-needs-source-column.md) | Dashboard filter does nothing if the linked column isn't in the SOURCE query's SELECT — refactor aggregate queries to row-level + summarize in data_query |
| 2026-05-06 | [`insights-filter-order-vs-css-nth-child.md`](gotchas/2026-05-06-insights-filter-order-vs-css-nth-child.md) | Putting a filter at items[0] shifts every chart's `:nth-child(N)` index — keep the filter LAST in the array; visual placement comes from layout coords |
| 2026-05-06 | [`insights-data-query-order-by-shape.md`](gotchas/2026-05-06-insights-data-query-order-by-shape.md) | Adding an `order_by` op to a data_query crashes with NoneType error — put `order_by` in the chart's config instead |
| 2026-05-06 | [`insights-explicit-join-wrong-schema.md`](gotchas/2026-05-06-insights-explicit-join-wrong-schema.md) | Explicit `JOIN ... ON` in raw_sql sends child tables to the empty `temp.main` schema (returns 0 rows). Use comma-join `FROM A, B WHERE A.x = B.y` instead |
| 2026-05-06 | [`insights-vue-grid-vertical-compact.md`](gotchas/2026-05-06-insights-vue-grid-vertical-compact.md) | Dashboards vertical-compact by default (localStorage flag, not the doctype field). Empty x-space on a row pulls items below upward — fill gaps with a `type:"text"` spacer to lock the layout |
| 2026-05-07 | [`frappe-v16-modern-desk-click-interception.md`](gotchas/2026-05-07-frappe-v16-modern-desk-click-interception.md) | v16 modern desk navbar (`header.desktop-navbar`) swallows mouse clicks even at document-level capture phase. Programmatic `.click()` works, real mouse clicks don't. Don't render interactive widgets into the navbar — use a floating panel or a Frappe page instead |
| 2026-05-07 | [`frappe-v16-realtime-registration-timing.md`](gotchas/2026-05-07-frappe-v16-realtime-registration-timing.md) | Realtime listeners registered before `socket.connected === true` get silently thrown out by Frappe v16's realtime init. Gate `frappe.realtime.on(...)` on the socket connection event, not just on `frappe.realtime.on` existing. Also re-register on `reconnect` |
| 2026-05-07 | [`frappe-workspace-per-user-api-blocked.md`](gotchas/2026-05-07-frappe-workspace-per-user-api-blocked.md) | No API path exists to create per-user workspace overrides for other users. `frappe.client.insert` fails on name uniqueness; `new_page` raises PermissionError. Workaround: log in as the target user and hide via desk UI |
| 2026-05-07 | [`git-stale-index-lock.md`](gotchas/2026-05-07-git-stale-index-lock.md) | `git add` fails with "Unable to create index.lock: File exists" — stale lock from crashed process. Fix: `rm .git/index.lock` then retry |
| 2026-05-08 | [`frappe-module-folder-vs-modulestxt-mismatch.md`](gotchas/2026-05-08-frappe-module-folder-vs-modulestxt-mismatch.md) | Renaming a module in `modules.txt` without renaming the on-disk folder makes Frappe v16 register the new module name but find no DocType/Page/Workspace content. Migrate half-completes; the site's Update Available pill never clears. Fix: `git mv <old_folder> <new_folder>` so the folder matches the snake_case of `modules.txt` |
| 2026-05-08 | [`frappe-cloud-site-update-is-the-app-install-path.md`](gotchas/2026-05-08-frappe-cloud-site-update-is-the-app-install-path.md) | New custom apps land on a site via **Sites → \<site\> → Update Available** — there is no separate "Install App" button. The Bench → Apps "Update Bench" modal only lists apps with newer commits, not site-installs |
| 2026-05-08 | [`frappe-patches-txt-needs-both-section-headers.md`](gotchas/2026-05-08-frappe-patches-txt-needs-both-section-headers.md) | `patches.txt` must contain both `[pre_model_sync]` AND `[post_model_sync]` headers, even if one section is empty. Migrate Site fails with `ValidationError: Patch type PatchType.post_model_sync not found in patches.txt` if either is missing. Empty file is fine; one-section file is not. The pre_sync patches run successfully BEFORE the failure, so it looks like everything's fine until post-sync explodes |
| 2026-05-10 | [`frappe-v16-page-api-drift.md`](gotchas/2026-05-10-frappe-v16-page-api-drift.md) | Custom desk Page JS ported v15→v16 fails with three sequential errors: (a) `wrapper.main` is undefined in modern desk — use `page.body` instead, (b) `page.body` is a jQuery object, not a DOM element — wrap in `$(...)` and use `.append()`, (c) `frappe.client.get_list` throws "Field not permitted in query: <field>" because v16 tightened field-level perms — drop offending fields (e.g. `item_code` on Work Order) or use a backend whitelisted method |
| 2026-05-11 | [`frappe-new-app-missing-nested-module-folder.md`](gotchas/2026-05-11-frappe-new-app-missing-nested-module-folder.md) | A hand-built (not `bench new-app`) Frappe app needs a nested `<app>/<module_snake>/` folder even when there's only one module — collapsing it because the app name and module-snake match silently breaks Page / DocType discovery. Title-case in `modules.txt`, snake-cased on disk, every fixture's `"module"` field matching. Sibling case to the 2026-05-08 rename gotcha |
| 2026-05-11 | [`frappe-app-init-needs-version.md`](gotchas/2026-05-11-frappe-app-init-needs-version.md) | `<app>/__init__.py` must contain `__version__ = "0.0.1"`. Frappe reads it directly; `pyproject.toml`'s `version` doesn't substitute. Empty `__init__.py` → `AttributeError: module has no attribute '__version__'` at install. Easy to miss when handcoding the scaffold |
| 2026-05-11 | [`frappe-v16-listview-formatters-stripped-to-text.md`](gotchas/2026-05-11-frappe-v16-listview-formatters-stripped-to-text.md) | v16 modern desk's listview calls `listview_settings.formatters.<field>` but strips all HTML from the return value before insertion — only plain text survives. Console-invoking the formatter returns full HTML; the rendered DOM has only the text. Don't ship interactive UX through formatters on v16 — build a custom Page instead |
| 2026-05-11 | [`frappe-v16-modern-desk-listview-hooks-untrustworthy.md`](gotchas/2026-05-11-frappe-v16-modern-desk-listview-hooks-untrustworthy.md) | Meta-gotcha: most classic `listview_settings` hooks (`formatters`, `button`, capture-phase clicks) are ignored or have surprising behaviour on v16 modern desk. Default to a custom Page for any non-trivial custom UX. Cross-refs the navbar interception (2026-05-07) and Page JS drift (2026-05-10) gotchas |
| 2026-05-11 | [`host-vs-bash-write-truncation.md`](gotchas/2026-05-11-host-vs-bash-write-truncation.md) | Sibling to `host-vs-bash-fs-sync.md`: when Write tool overwrites with smaller content, bash mount can keep the OLD file size with trailing `\x00` NULL padding. Host Read looks correct; JSON/JS/Python parsers crash on "Extra data" / "Unterminated string" / `invalid syntax` at a line near the real end. Fix: `python3 -c "open(p,'wb').write(open(p,'rb').read().rstrip(b'\\x00'))"` from bash, or re-Write to force a clean overwrite |

### Templates (reusable snippets)

| Template | Purpose |
|---|---|
| [`gotcha-template.md`](templates/gotcha-template.md) | Format for new gotcha entries |
| [`playbook-template.md`](templates/playbook-template.md) | Format for new playbook entries |
| [`skill-template/`](templates/skill-template/) | Skeleton for promoting a playbook into a Claude skill |
| [`dashboard-theme-soft-professional.css`](templates/dashboard-theme-soft-professional.css) | Reference CSS — current Soft Professional palette with verified selectors. Do NOT use as Client Script (see gotcha) |
| [`insights-theme-all-sites.user.js`](templates/insights-theme-all-sites.user.js) | **Master Tampermonkey userscript** — add a new site block to `SITE_THEMES`, colours only. Install once, covers all sites. |

### Sites

| Site | Notes |
|---|---|
| [`blomoplastics`](sites/blomoplastics.md) | Plastics manufacturer; Insights v3 Manufacturing Operations dashboard live |
| [`nesterp`](sites/nesterp.md) | Syncflo's internal ERPNext (Frappe v16); `quick_purchase_invoice` + `nest_theme` deployed; `nest_crm_tasks` v0.0.3 deploying 2026-05-11 |

### Projects (in-flight builds)

| Project | What it is |
|---|---|
| [`quick_purchase_invoice`](projects/quick_purchase_invoice/) | Frappe v16 custom app — QuickBooks-style fast capture of Purchase Invoices with an Item-or-Account row toggle. Scaffolded, ready to push to GitHub + install on `nesterp`. See its [DESIGN.md](projects/quick_purchase_invoice/DESIGN.md) and [DEPLOY.md](projects/quick_purchase_invoice/DEPLOY.md) |
| [`theme_studio`](projects/theme_studio/) | Frappe v16 custom app `nest_theme` — Syncflo-internal: **5-palette admin-only switcher** (Soft Professional, Accounting Crisp, Warm Earth, Corporate Navy, Minimal Mono — each with light + dark) + aggressively tightened section header padding + default Nest logo with customer logo override. Realtime swap on Settings save. **v0.3.0 (2026-05-07)** at `C:\ClaudeCode\nest_theme`. v0.1 toolbar widgets retired due to v16 click interception (`gotchas/2026-05-07-frappe-v16-modern-desk-click-interception.md`). **Internal use only**, no public release. See [SCOPE.md](projects/theme_studio/SCOPE.md) and [DEPLOY.md](projects/theme_studio/DEPLOY.md). |
| `nest_crm_tasks` | Frappe v16 custom app — sales-rep activity / tasks toolkit. Two desk Pages: **Lead Activity Hub** (`/desk/lead-activity/<lead>`) shows a lead's full ToDo history with mark-complete / reopen / add-task actions. **My Activities** (`/desk/my-activities`) is a custom replacement for the standard ToDo list — Lead-linked rows get a clickable `[👤 CRM-LEAD-...]` pill that one-shots to the Lead Activity Hub. Built as a Page (not via listview hooks) because v16 modern desk strips HTML from `listview_settings.formatters` returns. **v0.0.3 (2026-05-11)**. Repo: [Syncflo-design/nest_crm_tasks](https://github.com/Syncflo-design/nest_crm_tasks). |

## Adding to this knowledge base

Run a session, hit a snag, fix it, then before closing the session: write a 5-line gotcha. The format is in `templates/gotcha-template.md`. Don't optimise for prose — optimise for "would this save me 30 minutes if I read it before doing X again".
