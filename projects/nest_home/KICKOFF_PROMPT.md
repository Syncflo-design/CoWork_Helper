# nest_home — kickoff prompt (paste into a new task)

> Copy everything below the line into a fresh chat to start the build.
> It is written to be self-contained for a session with no prior context.

---

You are helping me (Russell) build a **new NestERP custom Frappe v16 app called `nest_home`**. This is a reusable product feature that will ship as a **NestERP standard** across all client sites — it is **not** specific to any one client.

## Step 0 — read these first, before writing anything

This repo is my persistent knowledge base. Read it before touching code; it will save hours.

1. `C:\ClaudeCode\CoWork_Helper\CLAUDE.md` — the entrypoint and working-style rules.
2. `C:\ClaudeCode\CoWork_Helper\playbooks\frappe-custom-app-v16.md` — how I scaffold Frappe v16 custom apps (file layout, pyproject.toml, hooks.py, DocType JSON, deploy on Frappe Cloud).
3. `C:\ClaudeCode\CoWork_Helper\playbooks\frappe-role-based-access-control.md` — roles, permissions, `role_home_page`.
4. These gotchas are directly relevant — read them, they are non-obvious and each one cost real debugging time:
   - `gotchas\2026-05-10-frappe-v16-page-api-drift.md` — desk Page API drift; mount `$main` inside `page.body`, not a class that doesn't exist (this bit nest_crm_tasks twice).
   - `gotchas\2026-05-11-frappe-v16-listview-formatters-stripped-to-text.md` and `gotchas\2026-05-11-frappe-v16-modern-desk-listview-hooks-untrustworthy.md` — why we build rich UIs as Pages, not via listview hooks.
   - `gotchas\2026-05-07-frappe-workspace-per-user-api-blocked.md` — per-user workspace API is blocked; informs how we do the per-user landing override.
   - `gotchas\2026-05-13-frappe-whitelisted-action-needs-return-value.md` — whitelisted method return-value gotcha.
   - `gotchas\2026-05-17-cowork-write-tool-silent-truncation.md` and `gotchas\2026-05-11-host-vs-bash-write-truncation.md` — **the Write/Edit tool silently truncates files around ~20 KB.** For any file >15 KB, write via bash heredoc and verify with `wc -c`, `tail`, and `node --check`. Split JS and CSS into separate files from the start.
   - `gotchas\2026-05-07-frappe-v16-realtime-registration-timing.md` — realtime listener timing (relevant to the phase-2 live-push feature).
   - `gotchas\2026-05-14-cowork-edit-tool-flips-lf-to-crlf.md` — line-ending flips.

5. **Pattern references — existing apps that already solve most of this:**
   - `C:\ClaudeCode\nest_crm_tasks` (repo: `Syncflo-design/nest_crm_tasks`, **v0.0.4**) — its **"My Activities"** desk Page is the direct ancestor of our List A. It already queries ToDos for the current user, renders a custom Page UI, persists filters to localStorage, and deep-links Lead-linked rows. **Reuse its query and rendering patterns.** Read its `CLAUDE.md` and the `my_activities` page source.
   - `C:\Users\User\production_floor\nest_crm_mobile` (repo: `Syncflo-design/nest_crm_mobile`) — read its `CLAUDE.md` for the **five non-negotiable rules** of our desk-Page bundle pattern (HTML in a JS string array joined with `\n` not backticks; the `.html` file stays a placeholder; controller is `window.xxx = {...}` not `const`; deploy cycle; bump a BUILD_MARKER each deploy). The `nest_home` page must follow the same rules.
   - `C:\ClaudeCode\nest_theme` (repo: `Syncflo-design/nest_theme`, v0.3.2) — the branding/palette app. `nest_home` should visually align with it (read its palette tokens) and ideally read the customer logo the same way (`Nest Theme Settings.customer_logo`).
   - `C:\Users\User\production_floor\DEMO_LAUNCHER.html` — the visual bar to clear. This launcher is the look-and-feel target: card grid, sequence, brand header, professional dark UI. `nest_home` should feel this polished, not like stock Frappe.

## The product concept

NestERP's native desk/workspace UI is functional but not beautiful, and it makes users **go and look** for their work. We are inverting that.

**Philosophy — push, not pull:** *"Any information I need comes to me. I should NOT need to go look for it."* When a user logs in, their landing page already shows everything that needs their attention — their tasks, the things awaiting their decision, and the things they are waiting on from others. Doing your job comes first; a dashboard is something you choose to open, not the front door.

`nest_home` is a **role-based landing page** (set via `role_home_page`) with a **professional, configurable, branded custom UI**. Every landing page has two zones:

1. **Quick-launch** — large, attractive buttons/tiles to that role's most-used functions. **Data-driven and role-aware** (admin configures which tiles a role sees; no code change to add one).
2. **Attention lists** — live, **per-user** worklists, already populated on landing.

## The attention engine (the core abstraction)

Build one server-side **attention engine** that aggregates items from pluggable sources and returns them normalised to a single **item schema**:

```
{ title, subtitle, deep_link (route), source_doctype, source_name,
  age / created, priority, owner_or_party, list_category }
```

Getting this schema right is the keystone — every future source must plug in without touching the page.

Three list categories, composed per role:

- **List A — "My Activities"** — ToDos where `allocated_to = current user`, status Open. *Do these.* (Reuse nest_crm_tasks query.)
- **List B — "Awaiting My Action"** — documents in a state needing a decision from the user's seat. **v1 sources: Work Orders, Purchase Orders, Sales Orders** (e.g. draft/submitted docs awaiting approval or acceptance, gated by the user's role + permissions). Build List B as **rules/config**, not hardcoded, so more doctypes plug in later.
- **List C — "Waiting On Others"** — ToDos where `assigned_by = current user` and `allocated_to ≠ current user`, still Open. *Chase these.* (Same ToDo table as A, different filter — nearly free.)

Optional fourth source if cheap: **Notification Log** (mentions, assignments, shares) — covers "I shouldn't have to check notifications."

**Role composition:**
- General users → List A (+ notifications) + their quick-launch tiles.
- Operators → a thin List A (their assigned runs) + operator quick-launch tiles.
- **Management → all three lists (A + B + C)** on one screen — *what's on me, what needs my call, what I'm owed.* + management quick-launch tiles.

## Configurability requirements

- **Role-based shell** via `role_home_page` in hooks.py.
- **Per-user landing override:** add a custom field on **User** (e.g. "Preferred Landing Page", Select/Link) + a small `on_login` / boot hook that honours it, falling back to role default → app default. (Heed `gotchas\2026-05-07-frappe-workspace-per-user-api-blocked.md`.)
- **`Nest Home Settings` single doctype** for app-wide config: default landing, whether users may override, brand logo, which lists each role shows.
- **`Nest Home Tile` doctype** (data-driven quick-launch): fields like label, icon, target route, allowed roles, sort order. Admins add a tile by creating a record — no code.
- Dashboards are **demoted to a tile**, never the front door.

## The four design decisions to honour

1. **Item schema is the keystone** — normalise every source to one shape (above). Spend the first effort here.
2. **Performance is the promise** — login must feel instant. Bounded queries with limits, a single aggregation pass, List A paints first while B/C fill behind it. No twenty-query login.
3. **List B is the real engineering** — A and C are nearly free (one ToDo table). Build B as extensible rules/config; start with WO/PO/SO; don't let its richness stall v1.
4. **Freshness** — v1: load on landing + manual refresh + optional quiet poll. **Live socket push is phase 2** (see realtime-timing gotcha). Don't over-build the first cut.

Also: **empty states are a feature** — an empty list means "you're clear" and should feel rewarding, not broken.

## v1 scope (build this first)

- The **attention engine**: server-side aggregator + the normalised item schema + sources for **List A** and **List C** (ToDos) and optionally Notification Log.
- **List B** wired with the three real sources — **Work Orders, Purchase Orders, Sales Orders** awaiting action — proving the rules/config framework end-to-end.
- The **role-based shell** with data-driven quick-launch tiles.
- **Per-user landing override** field + login hook (first-class, not bolted on later).
- `Nest Home Settings` + `Nest Home Tile` doctypes.
- Management role sees A+B+C; general roles see A (+ notifications); operators see thin A + tiles.

## App / deploy specifics

- **App name:** `nest_home`. **Frappe module:** decide a clean name (e.g. "Nest Home"). **Page route:** `/desk/nest-home` (or `nest-home`).
- **GitHub:** new repo under `Syncflo-design` (org I use for NestERP apps).
- **Dev/test site:** `syncflo-internal.c.frappe.cloud` (custom domain `www.nesterp.co.za`; Frappe Cloud site name `Syncflo_internal_V16`) — this is my NestERP internal box and the right home for a NestERP-standard app. MCP connector for it is `frappe-nesterp`.
- **Deploy cycle:** push → Frappe Cloud Bench → **Pull Updates** (do not skip) → Deploy → incognito reload. Bump a `BUILD_MARKER` constant each deploy so deploys are verifiable.

## Working style (from CLAUDE.md)

- Action over chat — edit the actual files / call the actual APIs; don't paste code for me to apply.
- For files >15 KB, **bash heredoc**, then verify (`wc -c`, `tail`, `node --check`). Split JS/CSS into separate files.
- When something non-obvious works after a debug, **append the lesson** to the app's `CLAUDE.md` and, if reusable, a `gotchas/` entry in CoWork_Helper.
- Honest reporting. No empty/blank tiles. Short responses unless depth is asked for.

## First moves I expect from you

1. Read the files in Step 0.
2. Confirm the app skeleton plan and the **item schema** with me before building (one short round).
3. Scaffold `nest_home`, build the attention engine + the two doctypes, then the Page UI, then wire `role_home_page` + per-user override.
4. Deploy to `Syncflo_internal_V16` and smoke-test in incognito.

Build it as a reusable NestERP standard from line one.
