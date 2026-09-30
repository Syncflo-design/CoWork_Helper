# nesterp — Syncflo internal ERPNext (Frappe v16)

**Site name on Frappe Cloud:** `Syncflo_internal_V16`
**Canonical URL:** `https://syncflo-internal.c.frappe.cloud`
**Custom domain:** `https://www.nesterp.co.za` — the ERPNext desk. **2026-08-25: the apex `nesterp.co.za` now serves the Nest ERP marketing site** (a separate public site, not this bench). Use the `www.` form for anything desk- or asset-related; the apex is no longer a dead host.

Syncflo's internal ERPNext instance. Frappe v16 / ERPNext v16.

## MCP connector

`frappe-nesterp` (configured globally for this user). Authenticates as **`hello@syncflo.co.za`** (Russell's day-to-day profile). **As of 2026-05-25 this account has FULL access** — the old `Company` / `DocField` / `Account` read restrictions are gone (see the 2026-05-25 section below). The historic restriction in `gotchas/2026-05-06-mcp-user-restricted-doctypes.md` no longer applies on this site.

## Apps installed

- `frappe`, `erpnext`
- `builder`
- `custom_subscription` — recurring-billing engine (Business Subscription). **Assessed + repaired 2026-05-20/21** — see the dated section below.
- `drive`
- `helpdesk`
- `syncflo_internal` (Syncflo's existing private custom app — module `Syncflo Internal`)
- `telephony` (`FTelephony` module)
- `erpnext_sbca` — **CRITICAL: Russell's Sage ↔ ERPNext bridge, written by Doreen (9t9it).** Two-way sync with Sage Business Cloud Accounting: pulls items, prices, stock levels, suppliers, accounts, sales orders, purchase orders FROM Sage; pushes item price changes BACK to Sage. Per-Company credentials in Settings. On nesterp it's installed but the Settings panel is still empty — no Company credentials wired, so the 11 sync jobs fire every tick and no-op. Not broken; just not switched on yet. **Do not disable / uninstall.** Full plain-English overview: `projects/erpnext_sbca/ASSESSMENT.md`.
- *(2026-05-06)* `quick_purchase_invoice` — staged for deploy; see `projects/quick_purchase_invoice/DEPLOY.md`.
- *(2026-05-07)* `nest_theme` v0.3.0 — Syncflo-internal palette switcher + tightened headers + customer logo. Deployed.
- *(2026-05-11)* `nest_crm_tasks` **v0.0.4** — Lead Activity Hub + custom My Activities page. Repo: [Syncflo-design/nest_crm_tasks](https://github.com/Syncflo-design/nest_crm_tasks). Local checkout: `C:\ClaudeCode\nest_crm_tasks` on the Dell (primary dev machine going forward). **v0.0.4 fix on disk, push + deploy + smoke pending.**

## Companies on the site

(Inferred from tax templates; the MCP user can't list Company directly.)

| Name | Default? | Notes |
|---|---|---|
| `Syncflo (Pty) Ltd` | — | South Africa |
| `Syncflo Testing` | yes (per Quick PI default) | Used for prototyping |
| `TEMPLATE – MultiStore + Manufacturing` | — | Template company |

## Tax templates

| Template | Company |
|---|---|
| `South Africa Tax - Spl` | Syncflo (Pty) Ltd |
| `South Africa Tax - ST` | Syncflo Testing |
| `South Africa Tax - T–M+M` | TEMPLATE – MultiStore + Manufacturing |

None marked `is_default=1` → users have to pick the template explicitly on each PI. (Could promote one to default later.)

## Suppliers

`PNA` is the only supplier as of 2026-05-06. All Items are non-stock services (`is_stock_item: 0`), `last_purchase_rate=0` everywhere — meaning the "smart-fill rate from history" feature in `quick_purchase_invoice` will return blank on first use until invoices accumulate.

## Core integrations

### erpnext_sbca — Sage ↔ ERPNext bridge (CRITICAL infrastructure)

**Written by Doreen (`doreen@9t9it.com`, 9t9it partner).** Two-way sync between ERPNext and Sage Business Cloud Accounting (SBCA). Every few minutes the app:

- **Pulls from Sage:** items, item categories, price lists + additional prices, inventory qty-on-hand, chart of accounts, suppliers, sales orders, purchase orders.
- **Pushes to Sage:** item price updates, item updates (batched).

Each ERPNext Company gets its own credentials row in the Settings panel — so multiple companies on this bench can sync with separate Sage accounts.

**Status on nesterp (2026-05-12):** installed but **not yet switched on**. The Settings URL field is empty and there are no Company credential rows. The 11 scheduled jobs fire every cron tick but exit immediately because they have nothing to authenticate as. Nothing is broken — just unconfigured.

**To switch it on** (needs the Sage credentials Doreen would have):
1. Fill the **URL** field in the `Erpnext Sbca Settings` panel (the base Sage API URL).
2. Add a row to the credentials table for each ERPNext Company that should sync (username, password, API key, OAuth callback URL).
3. Run the one-time OAuth login — Sage redirects back with a session id, which gets stored in the row.
4. Watch `Scheduled Job Log` for a few ticks to confirm syncing is happening cleanly.

**Do not disable, stop the scheduled jobs, or uninstall this app** without explicit go-ahead from Russell — it's keystone infrastructure for his ecosystem.

Full plain-English overview, audit recipe, and filesystem map: `projects/erpnext_sbca/ASSESSMENT.md`.
Meta-lesson on auditing inherited Frappe apps: `gotchas/2026-05-12-frappe-chatty-cron-on-unconfigured-third-party-app.md`.

## Active builds

### Quick Purchase Invoice — 2026-05-06

QuickBooks-style fast capture form. Each row picks Type = Item or Account; the second column's lookup target switches accordingly. On submit, a real `Purchase Invoice` is created; users with `Accounts User` role auto-submit.

- Code: `projects/quick_purchase_invoice/` (in this knowledge base)
- Design: `projects/quick_purchase_invoice/DESIGN.md`
- Deploy steps: `projects/quick_purchase_invoice/DEPLOY.md`
- Status: scaffolded, not yet pushed to GitHub or installed on bench. Awaiting Russell to:
  1. `git init` + push to `Syncflo-design/quick_purchase_invoice`
  2. Add to bench via Frappe Cloud
  3. Install on `syncflo-internal.c.frappe.cloud (a.k.a. www.nesterp.co.za)`
  4. Run the smoke test in `DEPLOY.md` §3

### Workspace / desk configuration — 2026-05-07

**User: presales@syncflo.co.za (Lyndsay)**

Roles: Sales User, Stock User, Item Manager, Workspace Manager, Pre_Sales, Accounts User, Purchase User.

Visible workspaces after this session: CRM, Home, Invoicing, Selling, Buying (+ Helpdesk if she has access).

Changes made via MCP:
- **Buying** — removed from `block_modules` (was blocked, now visible).
- **Financial Reports** — cannot be hidden via API (see `gotchas/2026-05-07-frappe-workspace-per-user-api-blocked.md`). Workaround: log in as Lyndsay → sidebar ⋮ → Hide.

---

### nest_theme — 2026-05-07

Syncflo-internal Frappe v16 theme app: instance-locked palette + per-user toolbar widgets for density and font scale. Internal use only, no public release.

- Code: `projects/theme_studio/` (in this knowledge base) — scaffolded local repo at `C:\ClaudeCode\nest_theme`.
- Design + locked decisions + build log: `projects/theme_studio/SCOPE.md`.
- Deploy steps: `projects/theme_studio/DEPLOY.md`.
- Status: **v0.1 scaffolded 2026-05-07**. Pending push to `https://github.com/Syncflo-design/nest_theme` and install on bench.
- Custom domain reminder for asset URL hits: use `https://www.nesterp.co.za/assets/nest_theme/...` (apex has no DNS).

**v0.1 ships:**
- Soft Professional palette (light + dark) — slate-blue / sage / soft amber / dusty rose.
- Density (compact / cozy / comfortable) and font scale (xs..xl) via navbar toolbar widgets.
- Body class injection via `boot_session` → `frappe.boot.syn_classes` → JS applies on DOMContentLoaded.
- Per-user prefs in dedicated DocType `Nest Theme User Preference` (autoname=field:user, unique on user).
- Realtime palette swap via `publish_realtime("syn_palette_changed", ...)`.

**v0.2 adds**: 4 more palettes (Accounting Crisp, Warm Earth, Corporate Navy, Minimal Mono), admin gallery view.

**Body classes to verify** in DevTools after install:
```html
<body class="syn-palette-soft-pro syn-density-comfortable syn-font-md ...">
```

### nest_theme v0.2.0 — 2026-05-07 (afternoon)

Major scope cut from v0.1. The toolbar widgets (density / font scaler / per-user prefs) failed because v16's modern desk navbar (`header.desktop-navbar`) intercepts mouse clicks at a layer above document-level capture-phase listeners — even our deepest defensive stack couldn't catch them. See `gotchas/2026-05-07-frappe-v16-modern-desk-click-interception.md`.

**v0.2.0 ships:**
- Single locked Soft Professional palette (light + dark), body class `syn-palette-soft-pro`.
- Aggressively tightened section header padding (~22px instead of ~50-60px). Form controls 30px tall, labels 11px, list rows 32px. Targets `.form-section`, `.section-head`, `.collapsible-section .section-head`, `.frappe-control`, `.form-control`, `.list-row`, `.grid-row`, `.form-tabs-list .nav-link`, `.page-head`, `.form-layout`. !important throughout to defeat ERPNext bundle specificity.
- Default Nest logo at `/assets/nest_theme/images/nest_logo.svg` (slate-blue rounded square + stylised white "N").
- Customer logo override: `Nest Theme Settings.customer_logo` (Attach Image). JS swaps `header.desktop-navbar .navbar-home img` `src` at boot + on realtime `syn_logo_changed` event.

**v0.2.0 deletes:**
- `api.py` (whitelisted methods)
- `Nest Theme User Preference` doctype + `tabNest Theme User Preference` table (via `nest_theme.patches.drop_user_preference_doctype`)
- All `.syn-density-*`, `.syn-font-*`, `.syn-toolbar-widgets` CSS
- All widget JS (buildWidgets, attachObserver, density/font setters)
- Settings fields: palette, default_density, default_font_scale, allow_user_density_override, allow_user_font_override

**Bytes:** CSS 9.2 KB (was 8.1 KB — gained spacing rules), JS 3.5 KB (was 11.4 KB — lost widget code).

**v0.1 → v0.2 deploy:** push + Deploy + Update on the site (Update runs `bench migrate` which executes the patch). The patch drops the orphan doctype + table cleanly. Settings doctype is preserved (just shrinks); Frappe doesn't auto-drop unused MariaDB columns, so the v0.1 columns stay quiet in the DB. Harmless.

### nest_theme v0.3.0 — 2026-05-07 (evening)

Re-introduced the palette switcher per Russell ("just colour variants, no font/spacing"). Five palettes, admin-only via Settings, realtime swap. v0.2's tightened spacing carried forward unchanged; widget layer stays retired.

**Palettes shipping in v0.3.0:**
- `soft-pro` Soft Professional (slate-blue / sage / warm taupe) — was the v0.2 baseline
- `crisp` Accounting Crisp (cyan-600 / emerald) — lifted from QPI v0.0.4
- `warm-earth` Warm Earth (terracotta / cream / forest) — new
- `corp-navy` Corporate Navy (deep navy / steel / gold) — new
- `minimal` Minimal Mono (mono + single emerald accent) — new

Each ships light + dark variants under `body.syn-palette-<slug>` and `html[data-theme="dark"] body.syn-palette-<slug>`.

**Layout/spacing rules** were refactored from `body.syn-palette-soft-pro` to `body[class*="syn-palette-"]` so the v0.2 tightening applies across all palettes. Tokens (colours) stay scoped per palette block; the CSS rules pick them up via `var(--card-bg)`, `var(--primary-color)`, etc.

**Permission fence:** `Nest Theme Settings` is System Manager only. Client desk users can't see or modify the palette. Russell switches during onboarding from his Frappe Cloud admin login.

**Files:** CSS 16.3 KB (5 palettes × 2 modes + spacing). JS 3.8 KB (2 realtime listeners). Backend has `boot.publish_settings_change` firing both `syn_palette_changed` and `syn_logo_changed` after commit.

---

### nest_crm_tasks — 2026-05-11

Sales-rep activity / tasks toolkit. Frappe v16 custom app. Repo: [Syncflo-design/nest_crm_tasks](https://github.com/Syncflo-design/nest_crm_tasks). Local checkout: `C:\ClaudeCode\nest_crm_tasks` on the Dell (primary dev machine going forward; was previously on the Manifold machine at `C:\Users\Russell - Manifold\nest_crm_tasks`).

**Goal:** when a salesperson opens their tasks, one click should land them on the full activity history for the linked Lead — not a chain of screens.

**v0.0.4 ships** (v0.0.3 had the same files but both pages were broken — see "v0.0.3 → v0.0.4 fix" below):

- **Lead Activity Hub** — desk Page at `/desk/lead-activity/<lead>`. Header card with lead metadata; activity table showing all ToDos linked to that Lead. Per-row Mark Complete / Reopen actions. Add Task dialog.
- **My Activities** — desk Page at `/desk/my-activities`. Custom replacement for the standard ToDo list. Each task row has a "Lead / Reference" column; Lead-linked rows show a blue clickable `[👤 CRM-LEAD-...]` pill that navigates to the Lead Activity Hub. Row click (outside the pill) opens the standard ToDo form. Filters: My/All × Open/Closed/Any, persisted to localStorage. Add Task + Mark Complete / Reopen actions in the page header.
- `fixtures/client_script.json` — Client Script for ToDo listview. Effectively no-op on v16 modern desk (formatter HTML stripped to plain text — see gotcha). Shipped for legacy desk compatibility; harmless on v16.

**v0.0.3 → v0.0.4 fix (2026-05-11):**

Smoke test of v0.0.3 revealed the page rendered chrome (title, filters, Actions / Add Task buttons, sidebar entries for both pages) but the body was empty. Console showed zero errors. `frappe.db.get_list("ToDo", {limit_page_length: 5})` from the console returned 20+ rows — so data was reachable.

Root cause: both pages had `this.$main = $(wrapper).find('.my-activities-page')` (and the analogous selector for lead_activity) — pointing at a class nothing in the code creates. The `$main` jQuery collection was empty. Every subsequent `this.$main.html(...)`, `.append(...)`, and `.on('click', selector, handler)` silently did nothing because jQuery setters and event-bindings against empty collections fail silently.

Fix (`my_activities.js` + `lead_activity.js`, both constructors):

```diff
- this.$main = $(wrapper).find('.my-activities-page');
+ // v16 modern desk: page.body is a jQuery object. Create our own container
+ // — find('.my-activities-page') returned empty because nothing made that div.
+ this.$main = $('<div class="my-activities-page"></div>').appendTo(page.body);
```

This is "Variant 2" of `gotchas/2026-05-10-frappe-v16-page-api-drift.md` — same root cause as the Work Order WIP fix (page-body wrangling in v16) but with a silent-no-error symptom instead of the appendChild TypeError. Both gotchas should be on the pre-build checklist for any future custom Page.

**Why a custom Page and not a Client Script:**

Three Client-Script approaches to add a one-click Lead shortcut to `/desk/todo` all failed on v16 modern desk:

1. Bubble-phase click interceptor — Frappe's own row-click handler fires first, navigates to the ToDo form before our handler runs.
2. Capture-phase listener on `cur_list.$result[0]` and `document` — never fires. Same family as the navbar interception gotcha.
3. `listview_settings.formatters.description` — IS called; v16 modern desk strips all HTML from the return before insertion. Plain text survives, the `<a>` pill doesn't.
4. `listview_settings.button` — appears ignored too (no button rendered after `cur_list.refresh()`).

Conclusion captured in `gotchas/2026-05-11-frappe-v16-listview-formatters-stripped-to-text.md` and the meta-gotcha `gotchas/2026-05-11-frappe-v16-modern-desk-listview-hooks-untrustworthy.md`: don't fight v16's listview. Build a custom Page.

**Workspace cutover:** the workspace shortcut for ToDo gets replaced with one pointing at `Page/my-activities` (link type "Page", page `my-activities`). Desk-UI action, no code change.

**Smoke test checklist:**

1. `https://www.nesterp.co.za/desk/my-activities` renders. Summary bar shows counts. Table populates.
2. Lead-linked rows show the blue `[👤 CRM-LEAD-...]` pill.
3. Click a pill → lands on `/desk/lead-activity/<lead>` with the Lead Activity Hub rendered. (The critical one-click flow.)
4. Click elsewhere on a row → opens the standard ToDo form.
5. Mark Complete, Reopen, Add Task work.
6. Scope (My/All) and status (Open/Closed/Any) filters work.
7. Filter choices persist after page reload.

### nest_theme v0.3.2 — 2026-05-07 — Sage-inspired palette

6th palette added: "Sage-inspired" (slug `sage-inspired`). Green-forward, styled to resemble Sage Business Cloud Accounting so users moving across the `erpnext_sbca` Sage bridge get a visual link. Unofficial — disclaimer in the Settings palette field description ("not affiliated with or endorsed by Sage").

Colours: primary `#0a9e2e` (light) / `#2ecc5a` (dark); bright Sage accent `#00c805` / `#00dc06`; canvas `#f3f7f3` light / `#0d1a10` dark. Sage brand green is `#00DC06` — kept as accent only (fails white-text contrast as a button colour).

Six palettes total now. No JS/layout change; pure additive CSS block + boot/Settings entries.

### custom_subscription — 2026-05-20 / 05-21

Recurring-billing engine (originally by **Chipo Hameja**). One submittable parent **Business Subscription** (autoname `BS-.####`) + two child tables (**Business Subscription Item**, **Business Subscription Recipient**). A daily scheduler walks every *submitted* subscription whose `next_invoice_date` is due and creates the configured document — **Sales Order**, **Sales Invoice (Draft)**, or **Sales Invoice (Submitted)** — then optionally emails the recipients and advances `next_invoice_date` by the frequency.

- **Repo:** [Syncflo-design/custom-subscription](https://github.com/Syncflo-design/custom-subscription) — **default branch `version-16`** (NOT `main`).
- **Local checkout:** `C:\ClaudeCode\custom-subscription` (Dell).
- **Engine:** `custom_subscription/subscriptions.py` (scheduler entry) + controller `.../doctype/business_subscription/business_subscription.py`.

**Bugs found & fixed (2026-05-20):**

1. **Stuck-forever scheduler.** `validate_subscriptions` filtered `next_invoice_date == today` (exact match), so any missed scheduler day left the date in the past and it never matched again — why BS-0002/3/4 sat unprocessed since early May. Fixed to `["<=", today]` + per-subscription `try/except` + `frappe.db.commit()` so one bad record can't abort the whole run.
2. **`before_save` rewound the schedule.** It reset `last_processed_date`/`next_invoice_date` to `start_date` on *every* save, so editing a running sub sent it back to the start. Guarded with `if self.is_new()`.
3. **Wrong date step.** `set_next_invoice_date` advanced from `last_processed_date` (pinned to `start_date` by `before_save`) instead of from `next_invoice_date`. Fixed.
4. **Email attached the wrong document.** `send_email` ran `frappe.attach_print(doc.doctype, doc.name, ...)` where `doc` was the *Business Subscription* (with a Sales-Invoice print format) — it never attached the generated invoice. Fixed to take the created doc and attach it; tolerates a bad/missing print format without killing the run.

**Features added:**

- **`end_date`** (`allow_on_submit`) — auto-stops the subscription once the next run would fall after it (clears `next_invoice_date`). This is the stop mechanism — there is intentionally **no fixed invoice-count cap**.
- **Permissions** — added `Accounts Manager` (full) + `Accounts User` (no delete/cancel) alongside `System Manager`.
- **`Daily` frequency — UAT/TEST ONLY.** Advances the next run by one day. Clearly commented in `FREQUENCY_STEP` + the Select options for easy removal after UAT. (Note templates are month-anchored, so `build_subscription_note` returns "" for Daily — harmless.)
- **`print_format` made `allow_on_submit`** so the layout can be switched on a running subscription.
- **Open-document link in the email** — `send_email` appends `frappe.utils.get_url_to_form(doctype, name)` so recipients click straight through to the generated invoice.
- **07:00 run time.** Switched `hooks.py` from the generic `"daily"` slot to **cron `0 7 * * *`**. Frappe evaluates cron in the site timezone (`Africa/Johannesburg`), so it fires at **07:00 SAST** — invoice creation and the confirmation email happen together (no more midnight mail). Change the `7` to adjust.

**Operating notes / gotchas:**

- **Submit-locked fields:** `frequency` (and `print_format` before the fix) are not `allow_on_submit`, so they can't be changed on an already-submitted subscription — to switch a live sub to `Daily` you must amend it, or (cleaner) create a fresh subscription with the right frequency/print format set *before* submitting. `end_date`, `next_invoice_date`, `last_processed_date` ARE editable on submit.
- **Deploy overwrote live DocType permissions.** `bench migrate` reset the permission rows to the app JSON and dropped the role the MCP connector user (`hello@syncflo.co.za`) relied on → it lost access to Business Subscription mid-session. Fix: granted it **Accounts Manager** (a role that's in the JSON, so it survives future migrates). See `gotchas/2026-05-20-frappe-deploy-overwrites-doctype-permissions.md`.
- **Push/branch trap:** Git Bash eats backslash paths (use `/c/...`) and the branch is `version-16`, not `main`. See `gotchas/2026-05-20-gitbash-windows-path-and-default-branch.md`.

**Deploy state (as of 2026-05-21):**

- **Batch 1 — DEPLOYED** (live DocType `modified` = `2026-05-20 17:30`): reliability fixes + `Daily` + `end_date` + permissions. Confirmed working — the scheduler processed BS-0005 on 05-21 and correctly advanced `next_invoice_date` to 06-20; the first confirmation email was received.
- **Batch 2 — PENDING:** `print_format` editable-on-submit + email open-link + 07:00 cron. Committed to `version-16`. The deploy was actually blocked by an **unrelated** bug: `nest_home` shipped a DocType (`Nest Home Layout Tile`) without its controller `.py`, crashing every *site* migrate with `ModuleNotFoundError` (it looked like a bench→site propagation issue but wasn't). Fixed 2026-05-21 by adding the missing controller — see `gotchas/2026-05-21-frappe-doctype-missing-controller-crashes-migrate.md`. Once the redeploy is green, populate BS-0005's `print_format` = `"2026 Invoice"` and `end_date`.

**Test record:** `BS-0005` — Syncflo Testing / Arbor Care, item `Retainer` @ 8410 (Monthly), `send_email` on to `presales@syncflo.co.za` + `hello@syncflo.co.za`, submitted. For the 5-day **Daily** trial, create a fresh subscription with `Daily` + a 5-day `end_date` (don't try to flip BS-0005 — `frequency` is submit-locked).

### hello@syncflo.co.za — granted full access + admin — 2026-05-25

Russell asked for his day-to-day profile (`hello@syncflo.co.za`, also the account the `frappe-nesterp` MCP connector authenticates as) to have full access and admin rights.

**Findings on inspection:** the account already held `System Manager` (+ ~24 other manager roles, role profile `Administrator`), `user_type = System User`, enabled. So admin *roles* were already in place. What was actually limiting it:

1. **`block_modules`** — 19 modules hidden (Assets, Automation, Core, Custom, Manufacturing, Website, Workflow, Integrations, Telephony, Regional, etc.).
2. **One `User Permission`** — `allow=Account`, `for_value="Accounts Receivable - Spl"`, `apply_to_all_doctypes=1`. This single record was the real cause of the long-documented "MCP user can't read Company/Account" symptom (`gotchas/2026-05-06-mcp-user-restricted-doctypes.md`) — it constrained Account visibility everywhere.

**Changes made via MCP (as the user itself — System Manager let it edit its own User doc):**

- Cleared `block_modules` → `[]` (all modules now visible).
- Deleted the `Account` User Permission (`User Permission` record `fbl5phlv0t`).

**Verified after:** `User Permission` list for the user is now empty; `Account` list returns the full COA; `Company` list returns all 3 companies (`Syncflo (Pty) Ltd`, `Syncflo Testing`, `TEMPLATE – MultiStore + Manufacturing`) — previously `[]`.

**Side effect to remember:** because this is the MCP connector's identity, the `frappe-nesterp` connector now also has full read/write across the site. The "restricted by design" note in the 2026-05-06 gotcha is no longer true for nesterp. Did NOT touch the `api_key`/`api_secret`, so the connector keeps working.

### Clean go-live restart — new company `Syncflo Pty Ltd` — 2026-05-28

Tenant never went live on `Syncflo (Pty) Ltd` (test junk only). Wanted a zero-history 1-June start keeping the CRM. After fighting the in-place wipe (GL-link guards + Transaction Deletion Record UX), **pivoted to a new company**:

- **`Syncflo Pty Ltd`** (abbr **SYN**, CoA cloned from `Syncflo (Pty) Ltd`, ZAR/SA) created and set as **Global Default Company**. Books empty.
- **199 leads bulk-moved** from `Syncflo (Pty) Ltd` → (parked on `Syncflo Testing`) → `Syncflo Pty Ltd`. Customers/contacts/communications are site-wide, so they came along automatically. **Total lead count held at 199 throughout** (the safety metric).
- Lead bulk-edit was blocked by mandatory **Source** — temporarily relaxed `Lead-source-reqd` + `Lead-utm_source-reqd` to `value=0`, moved leads, **restored to `1`**.
- Old `Syncflo (Pty) Ltd` financials cleared to **0** via a UI Transaction Deletion Record (GL, SIs, payments, journals, orders, advance ledger). **Still pending:** `Payment Ledger Entry` (136 rows) — missed on first TDR pass; needs one more TDR row (`Payment Ledger Entry` / Company Field `company`) before the old company can be deleted.
- Old company can be deleted once that's clear; the new company is the live entity.

Full lessons (TDR API traps, lead protection, ledger-link guards): `gotchas/2026-05-28-erpnext-clean-company-restart.md`.
