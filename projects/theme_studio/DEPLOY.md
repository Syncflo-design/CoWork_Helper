# nest_theme — Deploy

Recipe to push to Frappe Cloud and install on `Syncflo_internal_V16` (`syncflo-internal.c.frappe.cloud` / `www.nesterp.co.za`).

**Current version:** v0.2.0 — single locked Soft Professional palette + tightened section header padding + customer logo branding. **No toolbar widgets, no density/font scaling.** The v0.1 widget layer was retired due to v16 navbar click interception (see `gotchas/2026-05-07-frappe-v16-modern-desk-click-interception.md`).

## 1. Push to GitHub (run from Git Bash on Windows)

> **Paste gotcha**: Git Bash on Windows can mangle pasted multi-line commands. If your first line picks up a `^[[200~` prefix, type the first command (`cd ...`) by hand, then paste the rest. Permanent fix: `echo 'set enable-bracketed-paste off' >> ~/.inputrc`.

```bash
cd /c/ClaudeCode/nest_theme
git add -A
git commit -m "v0.2.0 — scope cut: single locked palette + logo branding

- Drop toolbar widgets entirely (v16 navbar swallows mouse clicks
  even at document-level capture phase, see new gotcha).
- Drop density + font scale axes. No per-user prefs.
- Lock Soft Professional as the only palette.
- Tighten section header + form spacing aggressively (.section-head
  ~22px, form controls 30px, list rows 32px).
- Add default Nest logo at /assets/nest_theme/images/nest_logo.svg
  (slate-blue gradient rounded square with stylised N).
- Add Settings.customer_logo (Attach Image) for per-instance brand
  override. JS swaps navbar logo src at boot + realtime.
- Patch: drop orphan Nest Theme User Preference doctype + table.
- Delete api.py (no whitelisted methods needed)."
git push
```

## 2. Frappe Cloud — full Deploy

Bench → **Deploys** tab → **New Deploy**. ~5 min. Required because `public/` files changed (CSS, JS, new image).

> Why Deploy not Update: Update skips `bench build` so static assets stay stale. See `gotchas/2026-05-06-frappe-cloud-update-vs-deploy-assets.md`.

## 3. Update site — bench migrate runs the patch

Sites → `Syncflo_internal_V16` → Apps → **Update** on `nest_theme`. This:
- Pulls the new commit
- Runs `bench migrate` which executes `nest_theme.patches.drop_user_preference_doctype` from `patches.txt`
- The patch deletes the orphan `Nest Theme User Preference` doctype + drops `tabNest Theme User Preference`

(If you're doing a fresh install rather than upgrading: Sites → Apps → Install → pick `nest_theme`. The patch runs but no-ops because the doctype was never created.)

## 4. Smoke test (v0.2.0 — much narrower than v0.1)

Hard-refresh the desk (`Ctrl+Shift+R`). Open DevTools → Console and paste:

```js
JSON.stringify({
  body_classes:    document.body.className,
  syn_classes:     frappe.boot.syn_classes,
  syn_logo_url:    frappe.boot.syn_logo_url,
  navbar_img_src:  document.querySelector('header.desktop-navbar .navbar-home img')?.src,
  // Tightened spacing — sample one section header height
  first_section_head_height: (() => {
    const sh = document.querySelector('.form-section .section-head');
    return sh ? Math.round(sh.getBoundingClientRect().height) : null;
  })(),
}, null, 2)
```

Pass criteria:
- `body_classes` contains `syn-palette-soft-pro`
- `syn_classes` is `"syn-palette-soft-pro"`
- `syn_logo_url` is `"/assets/nest_theme/images/nest_logo.svg"` (assuming no customer logo uploaded yet)
- `navbar_img_src` ends with `/assets/nest_theme/images/nest_logo.svg`
- `first_section_head_height` is roughly 22-30 px (was ~50-60 px in v16 default; if it's still that high on a Sales Invoice form, the selectors didn't catch — paste me the section-head outerHTML so I can refine)

Visual checks (open a Sales Invoice or Purchase Invoice form):
- [ ] Navbar logo: slate-blue rounded square with white "N" (the default Nest logo)
- [ ] Section headers ("Accounting Dimensions", "Currency and Price List", etc.) are visibly thinner — small uppercase muted-grey label, no longer the bulky button-like header
- [ ] Form fields are tighter — labels above inputs with minimal gap, inputs ~30px tall
- [ ] List rows in any list view (Sales Invoice list, etc.) ~32px tall
- [ ] Tabs (Details / Address & Contact / Terms / etc.) compact, slate-blue underline on active
- [ ] Soft Pro palette still applied — `#f5f6f8` page background, white card surfaces, slate-blue primary buttons

If section headers still look chunky on certain doctypes, paste this in console on that doctype's form and I'll add the missing selector:

```js
JSON.stringify(Array.from(document.querySelectorAll('.form-section')).slice(0,3).map(s => ({
  classes: s.className,
  head_classes: s.querySelector('.section-head')?.className,
  head_height: Math.round(s.querySelector('.section-head')?.getBoundingClientRect().height || 0),
  head_outerHTML: s.querySelector('.section-head')?.outerHTML.substring(0, 250),
})), null, 2)
```

## 5. Test the customer logo override

1. Open `https://www.nesterp.co.za/app/nest-theme-settings`.
2. **Customer logo** field → Attach → upload a square 32×32 PNG/SVG (e.g. a customer's brand mark).
3. Save.
4. Watch the navbar logo: it should swap from the Nest "N" to the uploaded image **without a reload** (realtime).
5. Reload the page → logo persists.
6. Clear the field → save → navbar reverts to the default Nest logo.

If the realtime swap doesn't happen but reloading shows the new logo, the realtime listener didn't attach. Check Console for `frappe.realtime.on('syn_logo_changed', ...)` — it should be wired up by `syn_boot.bundle.js`.

## 6. Updating later

For Python / DocType / hooks changes:

```bash
cd /c/ClaudeCode/nest_theme
git add -A && git commit -m "..."
git push
```

Frappe Cloud → Bench → Apps → row for `nest_theme` → **Update** (~30 s, runs migrations).

For ANY change under `public/` (CSS, JS, logo): same git steps, BUT in Frappe Cloud do **Deploys → New Deploy** (~5 min, full rebuild). Update will leave assets stale.

## 7. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Body has no `syn-*` class | `boot_session` errored | Frappe Cloud → Bench → Logs (worker / web). Check tracebacks. Browser console: `frappe.boot.syn_classes` should be a string. Re-run migrate. |
| Navbar logo unchanged (still Frappe icon) | Logo selector mismatch | Direct-hit `https://www.nesterp.co.za/assets/nest_theme/images/nest_logo.svg` — should return the SVG. If 200 but navbar still shows Frappe icon, paste me `document.querySelector('header.desktop-navbar .navbar-home img')?.outerHTML` so I can update the JS selector. |
| Section headers still look chunky | Selectors didn't catch v16's actual class names | Paste the diagnostic in step 4 so I can target the exact element. |
| Customer logo upload doesn't propagate | Realtime listener didn't attach | Console: `frappe.realtime` should be defined. Check that `frappe.realtime.on('syn_logo_changed', ...)` was registered (look for it in syn_boot.bundle.js console errors). |
| Direct asset URL 404s | Update vs Deploy | You ran Update instead of Deploy after a `public/` change. New Deploy → wait green → hard refresh. |

## v0.3.0 addendum — palette switching test

After deploy + update, hard-refresh the desk and:

1. Confirm default still works: `frappe.boot.syn_classes` returns `"syn-palette-soft-pro"` (or whatever palette was set in Settings).
2. Open `https://www.nesterp.co.za/app/nest-theme-settings`.
3. Change **Palette** to `Accounting Crisp` → Save. The desk should repaint to cyan-accent / white surfaces **without a reload**. (Realtime fires `syn_palette_changed` → JS swaps body class → CSS targets new palette block → repaint.)
4. Walk through all five palettes saving each in turn:
   - Soft Professional (slate-blue / sage)
   - Accounting Crisp (cyan / emerald)
   - Warm Earth (terracotta / forest)
   - Corporate Navy (deep navy / gold)
   - Minimal Mono (mono + emerald accent)
5. Toggle the user-menu dark/light theme on each — confirm the dark variant lands. Each palette has its own dark token block.
6. Network tab: there should be NO new asset request when switching palettes (the CSS bundle has all five palettes pre-baked; the swap is just a body-class change).

If a swap doesn't fire live but does land on reload, the realtime listener didn't attach. Console:
```js
typeof frappe.realtime?.on === 'function'
```
Should be `true`. If `false`, Frappe's realtime layer didn't initialise — check bench logs.
