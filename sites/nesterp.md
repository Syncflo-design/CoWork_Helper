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

### Frappe CRM installed as "Prospects" for big-client pipeline — 2026-10-12

- **Frappe CRM v1.87.0** installed (route `/crm`). Split agreed with Russell: Frappe CRM = big,
  long-cycle clients (demos, several stakeholders, e.g. Leader, Protea Tyres, DatronX), converted
  to ERPNext Projects "as and when" (manual step, not auto on Won). ERPNext CRM (Lead/Opportunity +
  `nest_crm_tasks`) **stays** for quick product sign-ups. Nothing deleted from ERPNext CRM.
- **No bulk data copy.** Russell picks which prospects move over (Lyndsay to review the live leads).
  First record: `CRM-DEAL-2026-00007` Leader Rubber Company, status **Won**, primary contact Anton
  Walters; Griesel Consulting & Advisory (ERPNext Sales Partner, 35% commission to 2026-12-17)
  added as a CRM Organization with contacts Abrie and Friedrich Springhorn (Director, involved in
  the Leadertread implementation) — contacts also linked to the Sales Partner in ERPNext.
- **nest_home tiles:** `NEST-TILE-0019` **Prospects** (`/crm`, allowed roles Sales User/Manager +
  System Manager) and `NEST-TILE-0020` **Projects** (`/app/project`, Projects User/Manager + System
  Manager), first two tiles on all three layouts (Administrator, Administrator Profile, PreSales).
- **Layout trap:** the browser signed in as the `Administrator` *user* has no role profile, so it
  resolves the **Administrator** (System Manager role) layout, not **Administrator Profile**
  (Russell's `hello@syncflo.co.za`). Update both when changing admin tiles.
- Frappe CRM defaults worth knowing: deal statuses Qualification → Demo/Making →
  Proposal/Quotation → Negotiation → Ready to Close → Won/Lost; setting Won stamps `closed_date`
  = today; new CRM Organizations default `no_of_employees` to "1-10".
- Planned, not built: "Deals slipping" nest_home attention source; Convert to Project button;
  SaaS project templates per product (Fuse, NestERP); contractor (partner developer) access +
  timesheets; Teams transcript → AI meeting note.
- **2026-10-13 Kanban + consultant field:** Custom Field `CRM Deal.custom_consulting_organization`
  (Link → CRM Organization, label "Consulting Organisation"), added to the `CRM Deal-Side Panel`
  CRM Fields Layout after `organization`. Shared Deals Kanban = `CRM View Settings` #10 with
  `is_standard=1` and `user=""` — `crm.api.views.get_views` returns `user==""` rows to EVERY user, so
  one record sets the board for all current and future users (a user who saves their own Kanban
  settings gets a personal standard view instead). Cards: consulting org, email, mobile, assigned,
  modified — `annual_revenue` (the "value") removed. Frontend caches views (`crm-views`): hard refresh.
  PE Chemicals = `CRM-DEAL-2026-00008` (Demo/Making), consultants Enable CFO (Reynier Koen, Beon Smit).
- **2026-10-13 Next Step = next task:** Server Scripts `CRM Deal - Next Step from Tasks (save)`
  (CRM Task, After Save) and `(delete)` (After Delete) set `CRM Deal.next_step` to the earliest-due
  CRM Task that is not Done/Canceled and has a due date, as "<title> (dd MMM)"; blank when none.
  Written with `frappe.db.set_value(..., update_modified=False)`. `next_step` made read-only
  (Property Setter) and added to the shared Kanban card fields. Sandbox trap hit:
  `date.strftime` raises `KeyError: '__import__'` — use `frappe.utils.formatdate`.
- **2026-10-13 Primary contact on the card:** Custom Field `CRM Deal.custom_primary_contact` (Data,
  read-only) filled by Server Script `CRM Deal - Primary Contact Name` (CRM Deal, Before Save) from the
  `contacts` row with `is_primary`. Kanban card fields now: primary contact, consulting org, next step,
  email, mobile, modified — `_assign` (deal-owner avatar) removed because Russell read it as "the contact".
  CEA Group = `CRM-DEAL-2026-00009` (Ready to Close, SNG Grant Thornton lead consultant, Enable CFO
  Intacct partner); built from the "CEA Group Proposal" email + engagement letter, reusing Lyndsay's
  ERPNext Customer/Contact "CEA Group" / "Wendy Hlupeko".
- **2026-10-13 Demo brief + Debrief (Claude):** no app, all site records. Single custom DocType
  `Prospects AI Settings` (module FCRM; Password `api_key`, `model` = claude-opus-5-5, `effort` = low,
  `product_notes` DRAFT for Russell to correct). API Server Scripts `prospects_demo_brief` (deal facts +
  contacts + notes + comments + tasks -> Anthropic Messages API raw HTTP via `frappe.make_post_request`,
  `fallbacks: "default"` + beta `server-side-fallback-2026-07-01`, timeout (10,110); saves FCRM Note
  "Demo brief - dd MMM yyyy"; skips earlier briefs when gathering notes) and `prospects_debrief` (text ->
  escaped, dated Comment on the deal). Buttons via legacy CRM Form Script `Deal - Demo Brief and Debrief`
  (`setupForm` returning `actions`; `$dialog` html + browser SpeechRecognition `en-ZA` for dictation).
  Sandbox notes: `frappe.make_post_request` is the SSRF-guarded wrapper (default timeout (10,300), pass
  `timeout`), error body is not readable; safe utils include strip_html, escape_html, fmt_money, formatdate.
  Tested: brief stops cleanly without key; debrief comment saved + escaped (test deleted). Brief itself
  untested until the key is in.
- **2026-10-28 — Helpdesk opened for client fault logging (first client: Ardmore).** HD Customer `Ardmore`; HD Ticket Type `Improvement`; service user `ardmore-support@syncflo.co.za` (Agent role, HD Agent, API token used by Ardmore's "Report a Problem" tile; secret stored only on the Ardmore site); Russell (hello@) made an HD Agent by adding Agent + Agent Manager to Role Profile `Administrator`. HD Agent perms were broken (a single Custom DocPerm from 7 May had replaced the standard ones) - Custom DocPerm rows added for Agent Manager and System Manager. Tickets are worked at /helpdesk. Incoming switched ON the same day (IMAP mail.syncflo.co.za:993, INBOX -> HD Ticket, UNSEEN only; the save validated the login). Still to do: review the Default SLA. Pattern for the next client: HD Customer + a service user per client + the same tile/page/script on their site (see sites/ardmore.md 2026-10-28).
- **2026-10-28 (later) — Tickets tile + per-agent visibility.** Nest Home Tile `NEST-TILE-0021` "Tickets" (-> /helpdesk/tickets) on all three layouts (Administrator, Administrator Profile, PreSales). Permission Query Server Script `HD Ticket - assigned tickets are private`: unassigned tickets visible to every agent, an assigned ticket only to its assignee; admin = role **Agent Manager** (Russell) or Administrator, NOT System Manager (the PreSales profile carries System Manager). PROVEN with the Ardmore service user (plain Agent): it listed the unassigned tickets and not 0104 while 0104 was assigned to Russell. Agent role added to the PreSales profile so Lindsay can work tickets. Server Script API `hd_ticket_tile_counts` returns the two numbers for the tile (orange unallocated / green mine); nest_home 0.0.32 adds header icons + multi-count pills (0.0.29-0.0.31 from the laptop already had the single red badge) on Nest Home Tile - push, pull, deploy, THEN set `count_method = hd_ticket_tile_counts` on NEST-TILE-0021. **Traps:** (1) a Permission Query condition goes through %-formatting -> write LIKE wildcards as `%%` or every list on that doctype dies with ProgrammingError (seen as a 500 for the agent, AttributeError in the MCP client). (2) `frappe.get_roles` / `frappe.db.escape` are not safe to use in the sandbox for this - use `frappe.db.exists("Has Role", ...)` and strip the user string by hand. (3) `frappe.get_list(..., user=X)` is not a way to test a permission query (the script reads frappe.session.user); test with a real non-admin token instead. **Found:** 21 old website test tickets (Feb 2026, "Website Support: Bug - ...") sit Open and unassigned and inflate the orange count; and switching incoming on pulled a REAL email into ticket 0105 ("Assistance", rochelle@nxco.co.za, 28 Oct 16:01) - someone must answer it. Russell to decide on closing the Feb test tickets.

- **2026-11-11 — Implementation Partner access + request tracking (first: Com-Struct).** All site records, no app.
  Project `PROJ-0003` "Com-Struct Implementation" (customer Com-Struct, company Syncflo (Pty) Ltd) with 13 starter
  tasks (TASK-2026-00002..14, no dates yet). Task custom fields: `custom_requested_by` (Data), `custom_requested_on`
  (Date, default Today), `custom_waiting_on` (Select Syncflo/Partner/Client), `custom_waiting_since` (read-only),
  `custom_received_on`. Project fields: `custom_client_contact_email`, `custom_digest_cc`. Server Scripts:
  `Task - Request Tracking` (Before Save: stamps requested by/on, restarts Waiting Since when Waiting On changes,
  stamps Received On when it moves off a party or a waiting task completes, blocks partners saving outside their
  projects); `Project - Monday Waiting On Client Email` (cron 0 7 * * 1, sends nothing while Client Contact Email
  is blank; email linked to the Project); Permission Queries `Task - Partner sees own projects only`,
  `File - Partner sees own project files only`, `Event - Partner sees own events only`. Script Report `Waiting On`
  (get_list, so permission-scoped). Role `Implementation Partner` (Task read/write/create/report/email/print, no
  delete; Project read/report/print). Nest Home layout `Implementation Partner` (tiles NEST-TILE-0022 My Projects,
  0023 Tasks, 0024 Waiting On); 0024 also added to Administrator + Administrator Profile layouts.
  **Add a partner:** System User with ONLY role Implementation Partner, then add them to the implementation's
  User Group (since 2026-11-17 the group carries the Project and the User Permission follows; see the
  2026-11-17 entry at the end). Nothing else.
  **Traps found:** (1) Task Custom DocPerm only had Projects User, so Russell (Projects Manager, no Projects User)
  could not open Tasks - Projects Manager row added. (2) Non-strict user permissions let a restricted user open a
  doc whose link is EMPTY by exact name; permission queries only hide lists. Strict mode is unsafe here because
  presales@ has an apply-to-all Workspace User Permission (User.default_workspace would hide most users), so
  Task.project was made mandatory (`mandatory_depends_on = eval:!doc.is_template`). Old TASK-2026-00001 (no project)
  is still openable by exact link until it gets a project or is deleted. (3) v16 desk users can LIST private File
  metadata (names of other clients' ticket screenshots); open/download is still 403 - hence the File query.
  Proven with a throwaway token user (lists, by-name reads, create/move/delete, report, upload, home tiles), then
  user, tasks, comment and file deleted.
- **2026-11-11 (later) — Project Tracker replaces Waiting On.** Russell wanted ONE screen per project, no separate
  report. Script Report `Project Tracker` (ref Task, roles Implementation Partner/Projects Manager/Projects User/System
  Manager): filters in the report's own `javascript` field (Project reqd, defaults to the user's default Project =
  the partner's is_default User Permission; Show All/Outstanding/Completed; Waiting On), "New Task" button pre-filled
  with the project, summary cards (Tasks / Completed / Outstanding / Overdue / Waiting on Client, always whole
  project), columns Requested On / Due (exp_end_date) / Received On / Days Late (received or completed or today minus
  due; blank when not late). Report `Waiting On` and tile NEST-TILE-0023 deleted. Partner layout = one tile
  NEST-TILE-0022 "Projects"; NEST-TILE-0024 "Project Tracker" on both admin layouts. Workflow for a client request:
  one task per request, Waiting On = Client, Due = +3 days, mark Completed when it arrives (keeps Waiting On = Client
  so the row shows who was late). **Traps:** nest_home URL-encodes tile routes - write `/app/query-report/Project
  Tracker` with a literal space (`%20` became `%2520`, "Nothing to show"); a Frappe `Int` column renders null as 0, so
  blank it in the JS formatter; v16 `exp_end_date` comes back as a datetime - getdate() it for a Date column;
  full-page loads on nesterp redirect to Nest Home, so test report URLs by clicking the tile.
- **2026-11-11:** partner login colin@cjkconnect.co.za (Colin Kaiser, CJK Connect) created: role Implementation Partner only, User Permission Project PROJ-0003 (default), no password, no welcome email (Russell: dry run first, no invite yet).
- **2026-11-11:** preview login partner.preview@syncflo.co.za ("Partner Preview") = exact mirror of Colin (Implementation Partner + PROJ-0003 default) for Russell's dry run; Russell sets its password himself. DELETE it (and any tasks it created) after the dry run.
- **2026-11-11 (later) — Project Contacts + Given To.** Custom DocType `Project Contact` (module Projects, PC-.#####;
  project reqd, full_name, side Client/Partner/Syncflo, role, organisation, email, phone, hidden source_contact) -
  deliberately SEPARATE from ERPNext Contact/Customer/CRM. Perms: Implementation Partner read/write/create/delete
  (no export/share), scoped by the Project User Permission. Task `custom_given_to` (Link Project Contact, before
  Waiting On); Client Script `Task - Given To` filters it to the task's project and sets Waiting On to the
  contact's side; `Task - Request Tracking` re-checks project match server-side and now: handing to a new party
  CLEARS Received On, clearing Waiting On or completing a waiting task stamps it (fixes Received On showing on
  still-open tasks). Server Script `Project - Copy Customer Contacts` (Project After Save, only when customer
  is set/changed) copies the customer's ERPNext Contacts in as side Client (copies, not links). PROJ-0003 got
  PC-00001 Liza Hoffman. Tracker: Given To column + Contacts button. Proven with a token test user (own-project
  only, cross-project contact blocked on read/create/assign, side auto-set) and visually as Partner Preview;
  test records deleted. Trap: get_all on Dynamic Link needs `parent_doctype="Contact"`.
- **2026-11-11 (later) — one-click task updates.** Russell: updating via the Task form is too complicated. Tracker
  rows now start with an **Update** button opening a dialog with Complete / Hand over / Yes / No / Roadblock (or
  Clear roadblock). Hand over = pick a project contact + due back (defaults today + 3 days); Roadblock = reason
  (required) + optional "who is holding it up"; Yes/No records `custom_answer` and completes the task. API Server
  Script `task_quick_update` (Task - Quick Update) does the change through a normal doc.save() (check_permission
  write first, so partners can't touch other projects - proven 403 on a PROJ-0002 task) and logs a signed comment
  ("Handed over to X (Client), due back dd-mm-yyyy: note") as the evidence trail. New Task fields
  `custom_roadblock` (Small Text) and `custom_answer` (Select Yes/No). Tracker: Task-ID column replaced by the
  button, status pill shows Roadblock (red, hover = reason) or "Completed · Yes/No", new Roadblocks summary card.
  Dialog JS lives in the report's `javascript` (open_update). Trap: partners have no Comment list permission -
  timeline comments still show (docinfo), but don't call frappe.db.get_list('Comment') as a partner.
- **2026-11-11 (later) — simple New Task.** Tracker "New Task" now opens a 4-field dialog (Task, Hand to optional,
  Due back optional - fills today + 3 when a person is picked, Details optional -> description) instead of the
  full Task form. API Server Script `task_quick_create` (Task - Quick Create) inserts through a normal doc.insert()
  (partner 403 on another project proven) and logs a signed "Created and handed to X, due back ..." comment.
  Tested as Partner Preview; test task deleted. Full Task form still reachable via "Open full task" in Update.
- **2026-11-11 (later) — one "Who Has It" field + compulsory fields + dictation.** Given To relabelled
  **Who Has It** (`custom_given_to`); Waiting On is now hidden/read-only and ALWAYS derived from that person's side
  in `Task - Request Tracking` (blank when nobody has it) - it still drives the clock, the Waiting on Client card and
  the Monday email. Tracker: single "Who Has It" column ("Liza Hoffman (Client)"), Who Has It filter replaces the
  Waiting On filter, Due column renamed **Due Complete Date**. New Task: Who Has It + Due Complete Date compulsory
  (dialog reqd + `task_quick_create` throws); Hand over also requires the date. Dictation: nest_assistant adds its
  mic to any dialog field named `description`, `note`, `notes` or `comment` (on shown.bs.modal) and to the
  description field on ToDo/Task/Event forms - so dialog Details uses fieldname `description`. Local nest_assistant
  clone lacks this (deployed bundle is newer - laptop commits). Tested as Partner Preview; test task deleted.
- **2026-11-11 (later) — Update screen redesign + clickable tiles.** Russell found the Yes/No buttons confusing.
  Update dialog now asks "What's happened?" with three stacked cards (inline Lucide SVG icons): **Done**, **Hand
  over**, **Roadblock** (or **Roadblock cleared**); the chosen card highlights and the Save button renames itself
  (Mark done / Hand over / Flag roadblock / Clear roadblock). Yes/No folded into Done as an optional "If you asked a
  yes/no question, what was the answer?" select; `task_quick_update` takes `answer` with `complete` (old yes/no
  actions still accepted). Show filter options are now "All tasks / Outstanding tasks / Completed tasks / Overdue
  tasks / Waiting on client / Roadblocks" (the label vanished once a value was picked, so the options say it), and
  clicking a summary tile sets that filter (delegated click on `.report-summary .summary-item`, active tile marked in
  `after_datatable_render`). Verified in Chrome as Partner Preview. Russell's own dry-run data on PROJ-0003
  (TASK-2026-00002 completed, answer Yes; contact PC-00002 Jim Beam) left in place.
- **2026-11-11 (later):** Russell: the yes/no answer is a waste of time - removed from the Update screen and the status pill; Task.custom_answer hidden (kept only for the one dry-run value). Done = just Done + optional note.
- **2026-11-11 (later) - final Update screen (Russell: stop complicating it).** Back to the button grid: Complete | Hand over, Roadblock (or Clear roadblock) full width. Complete reveals a Yes/No toggle: Yes completes; on a completed task the screen shows Complete | Hand back, and Complete + No reopens it (undo - status Open, completed_on/progress/received cleared, comment 'Reopened - marked not complete'); Hand back reopens and hands to the chosen person with a new due date. Every hand-over restarts Waiting Since. Toggle colour is driven by a data-pt-complete attribute on the dialog because the depends_on HTML field re-renders and drops inline styles. Tested via API (complete -> undo -> complete -> hand back, comments correct) and visually as Partner Preview; test task deleted.
- **2026-11-11 (later) - Update button sizing, phone layout, Board view.** Grid Update button sized inline (22px) so it fits the row. Phones (<768px) get one card per task instead of the grid (body.pt-tracker class set only on this report via frappe.router change hook; CSS in a single #pt-style tag). 'Board view' / 'List view' inner button (remembered in localStorage pt_board_mode) shows open tasks in one column per Project Contact (empty contacts too) + 'Nobody yet'; dragging a card onto another person opens Update on Hand over pre-filled. Handlers namespaced (.pt) and guarded by report_name so revisits don't double-bind. Verified as Partner Preview (desktop + forced phone CSS; Chrome window won't resize below desktop width). Home-screen-as-tracker for partners needs a nest_home code change (LANDING_ROUTES is a fixed list) - not done, awaiting Russell.
- **2026-11-11 (later) - four statuses.** Update screen now has a Status row Open / In Progress / Complete / Cancelled (current one highlighted, colour via data-pt-status on the dialog) plus Hand over (Hand back on closed tasks) and Roadblock. In Progress = ERPNext 'Working' relabelled; Complete = 'Completed'. Setting Open/In Progress on a closed task reopens it (completed_on, progress, Received On cleared); Cancelled requires a reason. task_quick_update action 'status' (old 'complete' Yes/No still mapped). Tracker: In Progress tile + filter, Cancelled filter, pill labels mapped. **Stopped Scheduled Job Type task.set_tasks_as_overdue** (ERPNext's nightly job flipped open tasks to 'Overdue', wiping In Progress) - overdue is shown from the due date instead; check it stays stopped after bench updates. Saving a past-due task does NOT set Overdue (tested). All transitions tested via API with signed comments; screen checked as Partner Preview; test task deleted.
- **2026-11-11 (later) - In Progress takes ownership + one-row tiles.** Clicking In Progress moves Who Has It to the clicker (comment "... - now with X (Side)", Waiting Since restarts) UNLESS the task is held by a Client contact (clients don't log in; the partner/Syncflo is relaying their progress). The clicker is matched to a Project Contact by email on that project; if none exists one is auto-created (side Partner for an Implementation Partner without internal roles, else Syncflo). Tested all three cases (client-held stays with client; Syncflo clicker; partner clicker) then deleted test tasks 19-21 and contacts PC-00003/4/5. Tracker tiles: Frappe gives each summary-item min-width 160px + 20px margins, so 7 tiles wrapped at 1366px; #pt-style (now re-injected on every load) makes them flex 1 1 0 / min-width 0 / smaller text on one row, wrapping only below 576px. Verified one row at 1366px.
- **2026-11-11 (later) - tighter tiles + partner home screen.** Tile strip cut from 104px to 57px tall (#pt-style: summary margin 8px 16px / padding 6px 8px, tile padding 4px, value padding 2px top). Partner home = tracker needs **nest_home 0.0.33** (new `Nest Home Layout.landing_route`); after deploy set layout "Implementation Partner" Landing Page = `query-report/Project Tracker` (literal space). Seen in passing: a fresh full-page load of a deep desk link sometimes bounces to the user's landing page (nest_home_redirect.js reads an empty route before the router settles) - intermittent, not fixed.
- **2026-11-11 (later) - partner home = tracker LIVE.** nest_home 0.0.33 deployed; layout "Implementation Partner" Landing Page = `query-report/Project Tracker`. Verified as Partner Preview: /desk and the breadcrumb Home both open the tracker (project defaulted). An already-logged-in user keeps the old landing until their cache is cleared (user menu Reload / `frappe.sessions.clear`) - Preview needed it; Colin has never logged in. Post-login redirect itself not tested (needs a password entry).
- **2026-11-11 (later) - Home icon 403 fixed (nest_home 0.0.34, live).** Breadcrumb Home on the tracker raised "No permission for Page" for partners: the desk renders /desk by fetching a Page named boot.home_page, and a report route isn't a Page. boot now leaves home_page at Frappe's default (`desktop`) for route landings and nest_home_redirect.js sends the empty route straight to the landing. Verified as Partner Preview from the tracker and from the Contacts list: lands on the tracker, no getpage call, no dialog. Browsers holding the old cached nest_home_redirect.js (plain asset, no version stamp) still work via the server half. Gotcha: `gotchas/2026-11-11-frappe-v16-boot-home-page-must-be-a-page.md`.
- **2026-11-11 (later):** Colin Kaiser added as Project Contact PC-00005 on PROJ-0003 (side Partner, CJK Connect, email = his login so In Progress matches him, no duplicate). Russell is sending the invite himself.
- **2026-11-11 (later) - Administrator landed on the tracker (fixed).** The built-in Administrator holds EVERY role, so both the "Administrator" (System Manager) and "Implementation Partner" Role layouts matched; equal priority -> most recently modified wins (the partner layout, after its Landing Page edit). Set layout "Administrator" priority = 10. Rule: any Role layout for a narrow role (partners etc.) must sit below the admin layout's priority. Cleared Administrator's cache, verified /desk -> nest-home. Also cleared the due date on TASK-2026-00002 (Kick-off meeting) at Russell's request.
- **2026-11-12 - second Com-Struct login: Liza Hoffman.** Russell: Liza (Com-Struct accountant / office manager, their first point of contact and Colin's closest link) needs the same view as Colin. Created System User liza@comstruct.co.za with ONLY role Implementation Partner + User Permission Project = PROJ-0003 (apply to all doctypes, default) - identical to Colin. No password, no welcome email (Email Queue checked empty). She matches layout "Implementation Partner" so lands on the Project Tracker. Her Project Contact PC-00001 (side Client) still carries csaccounts@comstruct.co.za, not her login email, so In Progress clicks by her will not match PC-00001 and will auto-create a new Partner-side contact - change PC-00001's email to liza@ if Russell wants her matched to her existing contact.
- **2026-11-12 (later):** PC-00001 (Liza Hoffman) email changed to liza@comstruct.co.za so the tracker matches her login (Russell: project contact only, NOT the CRM Contact). CRM Contact "Alan Christie" (Liza Hoffman, primary csaccounts@) left as is. Note: creating a User whose email is already on a Contact (here as a secondary Contact Email) makes Frappe re-save that Contact - no data changed (no Version), but its modified date moves.
- **2026-11-12 - Nest Home lists cut to My Activities (nest_home 0.0.36, all sites).** Russell: nest_home keeps only My Activities; Awaiting My Action (incl. presales invoices "Submit for Approval") and Waiting On Others removed from the app. Layouts Administrator, Administrator Profile and PreSales (previously B+C only) set show_list_a = 1 ahead of the deploy. Com-Struct gets its PO list via the layout's own list method (nest_po_management 0.0.3) instead.
- **2026-11-17 - one User Group per implementation drives project access.** Custom Field `User Group.custom_project` (Link Project, in list view). Server Script `User Group - Project Access` (DocType Event, After Save): each member who has role Implementation Partner and NONE of System Manager / Projects Manager / Projects User gets a User Permission Project = the group's project (apply to all doctypes; is_default only if they have no other Project default, because Frappe allows one default per allow). Removing a member, or changing the group's project, deletes that permission unless another group with the same project still holds the user. `User Group - Project Access on Delete` (Before Delete) does the same when a group is deleted. Internal staff in a group are skipped on purpose: a Project User Permission would hide every other project from them. A msgprint says who was given / taken away / skipped. Tested with partner.preview on a throwaway group for PROJ-0002 (grant, skip internal, remove, delete) - all clean, test group deleted. Live group: `Com-Struct Implementation` = PROJ-0003, members Colin, Liza, Kavida (their hand-made permissions were adopted, nothing duplicated). Same day: Kavida Naidoo (kavida@comstruct.co.za, on-site contact) added like Liza + Project Contact PC-00006; Colin + Liza invited by Russell via Reset Password after System Settings reset-link expiry was raised from 1200 s to 259200 s (3 days).
