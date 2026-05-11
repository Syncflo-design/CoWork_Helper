# nesterp — Syncflo internal ERPNext (Frappe v16)

**Site name on Frappe Cloud:** `Syncflo_internal_V16`
**Canonical URL:** `https://syncflo-internal.c.frappe.cloud`
**Custom domain:** `https://www.nesterp.co.za` (apex `nesterp.co.za` has no DNS — always use the `www.` form)

Syncflo's internal ERPNext instance. Frappe v16 / ERPNext v16.

## MCP connector

`frappe-nesterp` (configured globally for this user). Restricted permissions on `Company` / `DocField` / `Account` — see `gotchas/2026-05-06-mcp-user-restricted-doctypes.md`.

## Apps installed

- `frappe`, `erpnext`
- `builder`
- `custom_subscription`
- `drive`
- `helpdesk`
- `syncflo_internal` (Syncflo's existing private custom app — module `Syncflo Internal`)
- `telephony` (`FTelephony` module)
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
