# theme_studio — Scope (skinny / internal)

A Frappe v16 / ERPNext custom app that gives a Syncflo instance a **branded palette plus per-user accessibility controls**. Internal use only — installed on Syncflo's own sites and their managed clients. **No public release, no marketplace.** Working name: `syncflo_theme` (or whatever we settle on at build-start).

## What it does

Three layers, surfaced through native Frappe UX with no modals or page reloads:

1. **Instance-locked palette.** Admin picks from a small curated gallery (4-5 polished palettes, each with light + dark variants). Setting lives on a Single DocType. Applies to every user on that site.
2. **Per-user density toggle.** Toolbar widget with three options: compact / cozy / comfortable. Each user picks their own; instance default applies until they touch it.
3. **Per-user font scaler.** Toolbar `+` / `−` buttons. Each click bumps `--text-base` by ~1px; everything in Frappe sizes via rem so the whole UI scales proportionally. Persists to user defaults so it survives across browsers/devices.

Frappe's existing dark/light toggle stays untouched — we just make sure every palette has light AND dark variants so it works in either mode.

## Architecture

Four orthogonal axes resolved into body classes at boot:

```html
<body class="syn-palette-soft-pro syn-density-cozy syn-font-md">
```

Plus Frappe's existing `data-theme="dark|light"` on `<html>`. Browser engine matches the active classes and ignores the rest. No DOM rewrites, no asset refetches.

**Pipeline:**
- `boot_session` server hook reads instance settings + user prefs, computes effective classes, attaches to `bootinfo`.
- A small `app_include_js` hook reads `frappe.boot.syn_classes` early in page render and applies them to `<body>`.
- One CSS bundle (`public/css/syn_theme.bundle.css`) contains every palette × density × font variant scoped by class. Browser picks at runtime.

## Settings

### `Syncflo Theme Settings` (Single DocType, admin-only)

| Field | Type | Default | Notes |
|---|---|---|---|
| `palette` | Select | "Soft Professional" | The 4-5 curated palettes |
| `default_density` | Select | "comfortable" | comfortable / cozy / compact |
| `default_font_scale` | Select | "md" | xs / sm / md / lg / xl |
| `allow_user_density_override` | Check | 1 | If 0, locked instance-wide |
| `allow_user_font_override` | Check | 1 | If 0, locked instance-wide |

### User prefs (Custom Fields on User)

Two fields on the standard User doctype: `syn_density` and `syn_font_scale`. Empty means "use instance default". Toolbar widgets write to these via debounced API call.

## Toolbar widgets

Three items in the navbar (collapse to a dropdown on narrow screens):

1. **Density segment-control** — three small icons (compact / cozy / comfortable). Click → JS swaps body class → debounced write.
2. **Font scaler** — `−` and `+` icons with a small percentage indicator (100%, 110%, 90%...). Click → JS bumps body class one step → debounced write. Right-click resets.
3. **(Frappe's existing dark/light toggle)** — untouched.

Total real estate: ~80px. Keyboard shortcuts: `Ctrl+=` / `Ctrl+-` for font, `Ctrl+Shift+D` for density cycle.

## Initial palette set

To be confirmed at build-start. Strong candidates (we already have two from prior work):

| Palette | Source | Mood |
|---|---|---|
| Soft Professional | Lifted from blomoplastics Insights theme | Muted slate-blue / sage / warm taupe |
| Accounting Crisp | Lifted from QPI v0.0.4 | Cyan + emerald + slate, white surfaces |
| (TBD) | New design | Likely warm earth / cream / forest |
| (TBD) | New design | Likely corporate navy / steel / gold |
| (TBD, optional) | New design | Likely minimal mono + single accent |

Each palette ships with both light AND dark variants. Open question: do we need 4 or 5? Decide at build-start based on how much variety Syncflo's clients actually want vs maintenance burden.

## CSS variable contracts (sketch)

To be refined against Frappe v16's actual variable surface during the build:

- **Palette:** `--bg-color`, `--fg-color`, `--card-bg`, `--card-border`, `--text-color`, `--text-muted`, `--primary-color`, `--primary-hover`, `--btn-primary-bg`, `--btn-primary-color`, semantic alert/badge colors, `--shadow-sm`, `--shadow-md`.
- **Density:** `--padding-xs/sm/md/lg`, `--margin-sm/md/lg`, `--input-height`, `--btn-height`, `--row-height`.
- **Font scale:** `--text-base` (everything else relative). May need explicit overrides on `--text-sm`, `--text-md`, `--text-lg` if Frappe doesn't compute them from `--text-base`.

## Phasing

### v0.1 — internal prototype
- Settings DocType + boot_session hook + body class injection working
- One palette only (Soft Professional, light + dark)
- No toolbar widgets yet — verify the rendering pipeline first
- Install on nesterp, smoke test across 4-5 ERPNext flows (Sales Invoice, Purchase Invoice, Item, Customer, Stock Entry)

### v0.2 — full palette gallery
- Expand to 4-5 palettes, each with light + dark
- Settings page in Frappe Desk for admin to switch
- Verify palette switch propagates without page reload

### v0.3 — per-user controls
- Toolbar density widget
- Toolbar font +/- widget
- User pref Custom Fields + boot_session integration
- Instance-level "allow override" toggles wired up

### v0.4 — polish + roll out
- Tighten coverage on any surface where the palette didn't quite land (lists, dashboards, modals)
- Install on blomoplastics
- Document the deploy + settings recipe in `playbooks/syncflo-theme.md`

That's it. No public release work. No documentation polish for external users. No license agonising. Internal app, internal needs.

## Out of scope (deferred)

- Custom palette via color pickers — defer until the curated gallery proves insufficient
- Insights v3 propagation — for now, the existing Insights fork-overlay does Insights theming separately; if it ever becomes worth unifying, that's a separate project
- Print Format builder, Frappe Builder app theming — these have their own stylesheet paths; out of scope
- Mobile (React Native) coverage — desk web only
- Public marketplace listing, contribution guide, test coverage for external use — none of it

## Build-start open questions

1. **App name:** `syncflo_theme` or `syncflo_design`? (Pick one, stick with it.)
2. **Repo location:** new private repo under `Syncflo-design` org, same as the Insights fork pattern?
3. **Body class prefix:** `syn-` (short) or `syncflo-` (explicit)? Affects every CSS selector — pick early.
4. **User pref storage:** Custom Fields on User (proposed) vs separate single DocType? Custom Fields is simpler; revisit if it becomes constraining.
5. **Initial palette count:** 4 or 5? Pick at the start of v0.2 based on appetite.
6. **Realtime palette propagation:** when admin saves a palette change, do we push a `frappe.realtime` event so logged-in users repaint without reload? Worth ~20 LoC for a polished feel.

## Cross-references

- `playbooks/frappe-custom-app-v16.md` — scaffolding reference for the app structure.
- `gotchas/2026-05-06-frappe-cloud-cdn-stale-assets.md` — important: use `.bundle.css` naming or rotate filenames to avoid the CDN cache trap that hit QPI v0.0.2.
- `gotchas/2026-05-06-frappe-cloud-update-vs-deploy-assets.md` — important: use full Deploy (not Update) when CSS bundle changes.
- `gotchas/2026-05-06-host-vs-bash-fs-sync.md` — for any complex JSON writes during the build.
- `sites/blomoplastics.md` — source of the Soft Professional palette.
- `projects/quick_purchase_invoice/` — source of the Accounting Crisp palette.

---

## Locked decisions (2026-05-07 build session)

After SCOPE.md was written, the six build-start questions were resolved as follows:

| # | Question | Decision |
|---|---|---|
| 1 | App name | `nest_theme` (Frappe app, Python package, GitHub repo). Body class prefix stays `syn-` despite the package being `nest_theme` — same brand-vs-package split as the `Syncflo-design/insights` fork shipping `syncflo-custom-*` files. |
| 2 | Repo location | Private repo `Syncflo-design/nest_theme` on GitHub. |
| 3 | Body class prefix | `syn-`. Examples: `syn-palette-soft-pro`, `syn-density-cozy`, `syn-font-md`. Locked at boot via `boot_session` → `frappe.boot.syn_classes` → JS applies to `<body>`. |
| 4 | User pref storage | Dedicated DocType **`Nest Theme User Preference`**. Regular DocType (NOT a Single), `autoname: "field:user"`, `unique: 1` link to User, "All" role with `if_owner: 1` write so each user can manage their own row, "System Manager" role with full permissions. Cleaner uninstall, scales to more prefs without re-architecting, doesn't pollute the User doctype. |
| 5 | Initial palette count | 5 — Soft Professional, Accounting Crisp, Warm Earth, Corporate Navy, Minimal Mono+Accent. v0.1 ships only Soft Pro; the other 4 land in v0.2. |
| 6 | Realtime palette propagation | Yes. `doc_events.on_update` on `Nest Theme Settings` → `frappe.publish_realtime("syn_palette_changed", {palette: slug}, after_commit=True)`. JS listens via `frappe.realtime.on(...)`, swaps body class, no reload. ~10 LoC. |

**Phasing change**: v0.1 expanded to include the v0.3 toolbar widgets (per Russell, "I like the toolbar widget for font-size and density, please include them"). The v0.1 build now ships the density segment + font ± scaler. The "allow override" toggles are wired. The only remaining v0.3 work is an admin gallery view in v0.2.

## Build log

### v0.1 — 2026-05-07 — scaffolded

Files written to `C:\ClaudeCode\nest_theme`. All Python compiles, both DocType JSONs parse, JS parses cleanly, CSS braces balanced (34 / 34). Host filesystem and bash mount agree on bytes (md5 verified) — host/bash sync gotcha did not bite this build because every non-trivial file was written via `bash` heredoc.

**Repo layout (final):**

```
nest_theme/
├── pyproject.toml                       409 B   flit_core, dynamic version
├── README.md                          1.6 KB
├── license.txt                        1.1 KB    MIT
├── .gitignore                          95 B
└── nest_theme/                                  ← Python package
    ├── __init__.py                              __version__ = "0.1.0"
    ├── hooks.py                       818 B    bundle CSS/JS, boot_session, on_update realtime
    ├── modules.txt                              "Nest Theme"
    ├── patches.txt                              empty pre/post sync sections
    ├── boot.py                       3.8 KB    boot_session + publish_palette_change + helpers
    ├── api.py                        1.9 KB    set_user_pref, reset_user_pref (whitelisted)
    ├── public/
    │   ├── css/syn_theme.bundle.css   8.1 KB   palette + density × 3 + font × 5 + widget styles
    │   └── js/syn_boot.bundle.js      7.9 KB   boot apply + widgets + realtime + shortcuts
    └── nest_theme/                              ← module folder (snake of "Nest Theme")
        └── doctype/
            ├── nest_theme_settings/             Single, System Manager only
            │   ├── nest_theme_settings.json    1.8 KB   7 fields incl. 2 section breaks
            │   └── nest_theme_settings.py       834 B    validate() guards palette/density/font slugs
            └── nest_theme_user_preference/      regular, autoname=field:user, unique on user
                ├── nest_theme_user_preference.json   1.3 KB
                └── nest_theme_user_preference.py      463 B    validate() guards density/font slugs
```

**Behaviour wired:**
- `boot_session` reads `Nest Theme Settings` (cached via `frappe.get_cached_doc`) + per-user `Nest Theme User Preference`, resolves palette/density/font with precedence `user pref → instance default → hardcoded default`, attaches `frappe.boot.syn_classes` plus raw settings/prefs.
- `syn_boot.bundle.js` applies body classes at DOMContentLoaded (no FOUC because `app_include_js` loads sync before page render), builds navbar widget `<li>` with density segment + font ± scaler + percentage indicator, debounces saves to `nest_theme.api.set_user_pref` at 350 ms, listens on `syn_palette_changed` for live swaps, binds `Ctrl+=` / `Ctrl+-` / `Ctrl+Shift+D`, right-click on the font scaler resets to instance default.
- CSS Soft Professional light + dark scoped under `body.syn-palette-soft-pro:not([data-theme="dark"])` and `[data-theme="dark"]` respectively. Density × font tokens applied to `.frappe-control input`, `.form-section`, `.list-row`, `.grid-row`. No DOM rewrites, no asset refetches on swap.
- Admin saves Settings → `doc_events.on_update` → `publish_realtime` after commit → all open desks repaint.

**Asset hygiene baked in (so the QPI v0.0.2 saga doesn't repeat):**
- Both bundles named `*.bundle.css` / `*.bundle.js` so Frappe's bundler hash-fingerprints the URLs (kills the CDN cache trap by default — see `gotchas/2026-05-06-frappe-cloud-cdn-stale-assets.md`).
- `hooks.py` references bundle filenames only, no `/assets/...` prefix (lets the bundler resolve and rewrite).
- README + DEPLOY explicitly tell future-us: full Deploy on Frappe Cloud after any `public/` change, never Update.

**Known unknowns (verify on live site for v0.2):**
- Frappe v16 navbar selector: JS uses `'.navbar .navbar-nav, header.navbar ul'`. If v16 changed the navbar shell, widgets won't render and we update the selector. (Captured in DEPLOY.md § troubleshooting.)
- Density CSS tokens. The selectors targeting `.frappe-control`, `.form-section`, `.list-row`, `.grid-row` cover the dominant surfaces but Frappe may have added new layout primitives in v16. v0.2 polish pass extends coverage.
- `app_include_css` precedence vs ERPNext's own bundle. If ERPNext wins specificity wars on certain selectors, we add `body.syn-palette-*` to the LHS or bump specificity. Caught at smoke test.

## Patterns used (reusable for future Frappe apps)

- **Body class injection at boot.** `boot_session` hook computes a `frappe.boot.<key>` string, the JS bundle reads it on DOMContentLoaded and applies to `<body>`. No flash of unstyled content if the JS bundle is in `app_include_js` (loaded sync before page render). No CSS gymnastics — the browser engine matches the active class and ignores the rest.
- **Per-user prefs via dedicated DocType keyed by user.** `autoname: "field:user"` + `unique: 1` on the user link gives one row per user, indexed, removable on uninstall. Permissions: System Manager full + "All" role with `if_owner: 1` write. Cleaner than Custom Fields on User for app-specific prefs that may grow.
- **Realtime instance-config push.** `doc_events.on_update` on a Single → `frappe.publish_realtime(event, payload, after_commit=True)` → client listens on `frappe.realtime.on(event, fn)`. ~10 LoC, polished UX.
- **`.bundle.css` / `.bundle.js` naming.** Defaults the asset URL to be hash-fingerprinted by Frappe's bundler. Sidesteps CDN cache traps on Frappe Cloud.
- **Cached settings read in boot_session.** `frappe.get_cached_doc("My Settings")` keeps every page load cheap; cache is invalidated on save automatically.

---

## v0.2.0 — 2026-05-07 — scope cut (afternoon session)

**Why:** v0.1 / v0.1.1 / v0.1.2 shipped the toolbar widgets but mouse clicks never fired their handlers in v16's modern desk shell. v0.1 used the wrong anchor (legacy `.navbar .navbar-nav`, which matched a hidden notification-tabs ul); v0.1.1 fixed the anchor (`header.desktop-navbar .desktop-notifications`) and added a MutationObserver — widgets rendered correctly but mouse clicks still didn't reach our handlers; v0.1.2 moved click handling to document-level capture phase with stopPropagation — still nothing. Programmatic `.click()` on the buttons fired handlers fine; only real mouse clicks were swallowed. Frappe v16 is doing something at a layer above our reach (Vue-internal handler, pointer-events manipulation, or capture listener registered before us on `window`). See `gotchas/2026-05-07-frappe-v16-modern-desk-click-interception.md`.

**Decision:** drop the toolbar widgets entirely. Lock Soft Pro as the only palette. No more density, no more font scaling, no more per-user prefs. Pivot to **theme + logo branding**. The big visible win Russell saw on v0.1.x — the Soft Professional palette landing across the desk — is what v0.2 keeps and tightens.

### What v0.2.0 ships

| Layer | Behaviour |
|---|---|
| Body class | Single class `syn-palette-soft-pro`, applied at boot via `frappe.boot.syn_classes` and `app_include_js`. |
| Palette | Soft Professional (slate-blue / sage / warm taupe), light + dark variants both still scoped under the same body class. |
| Spacing | Tightened. Section headers (`.section-head`, `.collapsible-section .section-head`) reduced from ~30px to ~22px vertical. Form controls 30px tall (was ~40px). Field labels 11px / 2px margin-bottom. List rows 32px. |
| Branding | Default Nest logo at `/assets/nest_theme/images/nest_logo.svg` — slate-blue rounded square with stylised "N". Customer override field on `Nest Theme Settings` (Attach Image). JS swaps `header.desktop-navbar .navbar-home img` `src` at boot + on realtime `syn_logo_changed`. |
| Realtime | `on_update` on Nest Theme Settings → `frappe.publish_realtime("syn_logo_changed", {logo_url})` → JS swaps logo without reload. |

### What v0.2.0 deletes

- `nest_theme/api.py` (was `set_user_pref` / `reset_user_pref` whitelisted methods)
- `nest_theme/nest_theme/doctype/nest_theme_user_preference/` (entire directory)
- All density CSS (`.syn-density-*`)
- All font scale CSS (`.syn-font-*`)
- All toolbar widget CSS (`.syn-toolbar-widgets`, `.syn-density-segment`, `.syn-font-scaler`)
- Toolbar widget JS (DENSITIES, FONT_STEPS, buildWidgets, attachObserver — all gone)
- Keyboard shortcuts (Ctrl+= / Ctrl+- / Ctrl+Shift+D)
- Settings doctype fields: `palette`, `default_density`, `default_font_scale`, `allow_user_density_override`, `allow_user_font_override`

### Migration v0.1.x → v0.2.0

`nest_theme/patches/drop_user_preference_doctype.py` runs in `[post_model_sync]`:
- Deletes the orphan `Nest Theme User Preference` DocType from the desk
- Drops the `tabNest Theme User Preference` MariaDB table

The Settings doctype itself is preserved — only the fields shrink. MariaDB columns for the dropped fields stay (Frappe doesn't auto-drop columns on field removal). They're harmless and `bench drop-doctype` would only matter if we wanted them gone for cleanliness.

### v0.2.0 file inventory

| Path | Size | What |
|---|---|---|
| `nest_theme/__init__.py` | 22 B | `__version__ = "0.2.0"` |
| `nest_theme/hooks.py` | 843 B | Bundle filenames, boot_session, on_update logo realtime |
| `nest_theme/boot.py` | 1.2 KB | boot_session injects `syn_classes` + `syn_logo_url` |
| `nest_theme/modules.txt` | 11 B | "Nest Theme" |
| `nest_theme/patches.txt` | 84 B | post_model_sync drop patch |
| `nest_theme/patches/drop_user_preference_doctype.py` | 606 B | Removes orphan doctype + table |
| `nest_theme/nest_theme/doctype/nest_theme_settings/nest_theme_settings.json` | 946 B | Single Attach Image field: `customer_logo` |
| `nest_theme/nest_theme/doctype/nest_theme_settings/nest_theme_settings.py` | 103 B | Empty Document subclass |
| `nest_theme/public/css/syn_theme.bundle.css` | 9.2 KB | Soft Pro palette + tightened form spacing |
| `nest_theme/public/js/syn_boot.bundle.js` | 3.5 KB | Body class apply + logo swap (no widgets) |
| `nest_theme/public/images/nest_logo.svg` | 630 B | Default Nest logo (slate-blue gradient + stylised N) |

CSS down from `8.1 KB → 9.2 KB` (gained spacing rules, lost density/font/widget CSS). JS down from `11.4 KB → 3.5 KB` (lost all widget code).

### Settings doctype (v0.2.0)

```json
{
  "issingle": 1,
  "field_order": ["branding_section", "customer_logo"],
  "fields": [
    { "fieldname": "branding_section", "fieldtype": "Section Break", "label": "Branding" },
    { "fieldname": "customer_logo",    "fieldtype": "Attach Image",
      "label": "Customer logo",
      "description": "Optional. Replaces the default Nest logo in the navbar. Recommended: square 32×32 SVG or PNG." }
  ]
}
```

That's it. One field. Customer uploads a square logo, JS swaps the navbar img `src`, realtime fires for instant cross-tab repaint.

---

## v0.3.0 — 2026-05-07 (evening) — palette switcher restored, admin-only

**Scope:** re-introduce the palette dropdown on `Nest Theme Settings`. Five palettes, each with light + dark variants. Admin-only (System Manager perm). **No font size changes, no spacing changes** — the v0.2 tightened spacing stays exactly as it is, just generalised to apply across all 5 palettes.

**Why this works architecturally:** the click-interception problem from v0.1 was about toolbar widgets in the navbar, not about palette switching. Palette switching never failed — it's just a body-class swap with CSS scoped under that class. v0.3 restores it cleanly.

### Five palettes (locked)

Each palette ships **both light and dark variants**. Frappe's existing dark/light toggle on `<html data-theme="dark|light">` selects the variant; no extra setting needed.

| Slug | Label | Mood | Primary | Accent |
|---|---|---|---|---|
| `soft-pro`   | Soft Professional | Muted, calm, professional         | `#6b85a3` slate blue        | `#82a085` sage |
| `crisp`      | Accounting Crisp  | Sharp accountant feel, white surfaces | `#0891b2` cyan-600         | `#059669` emerald |
| `warm-earth` | Warm Earth        | Cream, terracotta, forest          | `#a05a2c` terracotta       | `#4a6741` forest green |
| `corp-navy`  | Corporate Navy    | Traditional corporate, gold accent  | `#1e3a5f` deep navy        | `#b8945a` gold |
| `minimal`    | Minimal Mono      | Pure mono + single colour pop       | `#404040` near-black       | `#16a34a` emerald |

Light variant tokens are defined under `body.syn-palette-<slug>`. Dark variant tokens under `html[data-theme="dark"] body.syn-palette-<slug>`. Same selector pattern for all five.

### What v0.3.0 changes

| File | Change |
|---|---|
| `nest_theme/__init__.py` | `__version__ = "0.3.0"` |
| `nest_theme/boot.py` | Restored `PALETTE_SLUG` dict (5 entries) and `_palette_slug()` resolver. New combined publisher `publish_settings_change` fires both `syn_palette_changed` and `syn_logo_changed` realtime events on save. |
| `nest_theme/hooks.py` | `doc_events` `on_update` now points at `publish_settings_change` (was `publish_logo_change`). |
| `nest_theme/nest_theme/doctype/nest_theme_settings/nest_theme_settings.json` | Added `palette` Select field (5 options, default Soft Professional, reqd, with description). |
| `nest_theme/nest_theme/doctype/nest_theme_settings/nest_theme_settings.py` | Restored validate() to guard against unknown palette labels. |
| `nest_theme/public/css/syn_theme.bundle.css` | 5 palette token blocks (light + dark each = 10 blocks). All layout/spacing rules refactored from `body.syn-palette-soft-pro` to `body[class*="syn-palette-"]` so they apply across every palette. Bundle 9.2 KB → 16.3 KB. |
| `nest_theme/public/js/syn_boot.bundle.js` | Re-added `syn_palette_changed` realtime listener alongside the existing `syn_logo_changed` listener. |

### Refactor: body-class-prefix selector

The v0.2 spacing tightening was scoped under `body.syn-palette-soft-pro` because that was the only palette. v0.3 generalises to `body[class*="syn-palette-"]` (CSS attribute selector matching any class name containing `syn-palette-`). This matches every palette without duplicating the rules. Each rule still resolves tokens (`var(--card-bg)`, `var(--text-color)`, etc.) from the active palette block — that part requires no change.

### Admin-only permission fence

`Nest Theme Settings` keeps the v0.2 perm setup: System Manager only (`create / write / read / print / share`, no `delete`). Client desk users don't see the doctype. Russell switches palette during onboarding from his Frappe Cloud admin login. Same architecture, different visibility.

### Realtime swap

Admin saves Settings → `publish_settings_change` runs `after_commit=True` → both events fire. The JS listener for `syn_palette_changed`:

```js
frappe.realtime.on('syn_palette_changed', (data) => {
  Array.from(document.body.classList)
    .filter((c) => c.startsWith('syn-palette-'))
    .forEach((c) => document.body.classList.remove(c));
  document.body.classList.add('syn-palette-' + data.palette);
});
```

Browser engine matches the new class, picks tokens from the new block, repaints. No reload, no asset refetch (the bundle's already cached with all five palettes).

### What v0.3.0 does NOT change

- No font size axis. No font-size CSS, no toolbar.
- No density / spacing per-user controls. The v0.2 tightening (section headers, form controls, list rows) is the single locked spacing across all palettes.
- No new doctypes. Settings stays the only one. The v0.1 `Nest Theme User Preference` doctype is still dropped via the v0.2 patch (which is idempotent).
- No widget injection into the navbar. The v0.1 toolbar widgets stay retired; the v16 click-interception gotcha applies.

### v0.3.0 file inventory

| Path | Size | What |
|---|---|---|
| `nest_theme/__init__.py`              | 22 B   | `__version__ = "0.3.0"` |
| `nest_theme/hooks.py`                 | 566 B  | Bundles + boot_session + on_update publisher |
| `nest_theme/boot.py`                  | 2.4 KB | Palette resolver + combined publisher |
| `nest_theme/modules.txt`              | 11 B   | "Nest Theme" |
| `nest_theme/patches.txt`              | 84 B   | post_model_sync drop patch (from v0.2) |
| `nest_theme/patches/drop_user_preference_doctype.py` | 606 B | Idempotent — safe on fresh installs and upgrades |
| `nest_theme/nest_theme/doctype/nest_theme_settings/*.json` | 1.3 KB | 2 fields: palette + customer_logo |
| `nest_theme/nest_theme/doctype/nest_theme_settings/*.py`   | 290 B  | Palette label validation |
| `nest_theme/public/css/syn_theme.bundle.css` | 16.3 KB | 5 palettes × 2 modes + spacing rules |
| `nest_theme/public/js/syn_boot.bundle.js`   | 3.8 KB | Class apply + logo swap + 2 realtime listeners |
| `nest_theme/public/images/nest_logo.svg`    | 630 B  | Default Nest logo (slate-blue gradient) |

CSS grew 9.2 KB → 16.3 KB (added 4 palettes × 2 modes). JS unchanged in shape, +200 B for the second realtime listener.

---

## v0.3.1 — 2026-05-07 (late evening) — realtime registration timing fix

**Symptom:** v0.3.0 deployed, palette saves fired the realtime event server-side (confirmed via manual `frappe.realtime.on('syn_palette_changed', console.log)` in browser — events arrived), but the body class never swapped because our shipped listener wasn't actually registered. Diagnostic `Object.keys(frappe.realtime.socket._callbacks).filter(k => k.includes('syn'))` returned only the user's manual listener; `palette_listener_count: 1`, `logo_listener_count: 0`.

**Root cause:** v0.3.0's `attachRealtime()` polled until `frappe.realtime.on` existed and registered immediately. But `frappe.realtime` exists very early as a stub — the actual socket connects later, and Frappe v16 appears to throw out early registrations during that initialisation. By the time the socket was connected, our listener was gone. Manual `.on()` from console worked because by then Frappe was fully initialised.

**Fix (v0.3.1):** Wait for `frappe.realtime.socket.connected === true` before registering. Also re-register on `socket.on('reconnect', ...)` so listeners survive disconnect cycles.

```js
function attachRealtime() {
  if (!window.frappe || !frappe.realtime || !frappe.realtime.socket) {
    setTimeout(attachRealtime, 500);
    return;
  }
  const sock = frappe.realtime.socket;
  if (sock.connected) {
    registerRealtime();
  } else {
    sock.on('connect', registerRealtime);
  }
  sock.on('reconnect', registerRealtime);
}
```

Captured as `gotchas/2026-05-07-frappe-v16-realtime-registration-timing.md` for future sessions.

**Files touched:** `nest_theme/__init__.py` → 0.3.1, `nest_theme/public/js/syn_boot.bundle.js` → ~830 B added (handlers split out, socket-connected gate). JS now 4.6 KB.
