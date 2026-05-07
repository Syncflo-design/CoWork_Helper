# Theming Insights v3 via a Minimal Fork (Server-Side, All Users)

**Last updated:** 2026-05-06
**Status:** ✅ VERIFIED LIVE on `blomoplastics.jh.frappe.cloud` (commit `9a121de` deployed 2026-05-06)
**Fork repo:** `https://github.com/Syncflo-design/insights` (branch `syncflo-custom-theme`)

## Outcome (what actually happened)

The plan held up exactly as predicted. Confirmed working in production:

- Total upstream change: **2 lines** (imports added to `frontend/src2/main.ts`)
- New files added: **2** (`syncflo-custom-overrides.css`, `syncflo-custom-chart-palette.ts`)
- Frappe Cloud build: succeeded first try, no Vite/TS errors
- Site after deploy: KPI tiles gradient-themed, donut chart's hot-pink slice replaced with dusty rose, tables with coloured top borders, soft canvas background
- Every user on the site sees the theme; no per-device install required
- Tampermonkey userscript can now be disabled (kept as fallback)

The `Object.assign(COLOR_MAP, ...)` mutation pattern works in production — Insights' `getColors()` returns the muted palette to every chart consumer.

## Why a fork (and not a userscript or Client Script)

We've already tried and ruled out everything else for site-wide theming:

- Client Script on `Insights Dashboard v3` → SPA bypasses Frappe's runtime (see `gotchas/2026-05-06-insights-spa-no-frappe-runtime.md`)
- Website Settings `head_html` / `custom_css` → never injected into Insights HTML
- Server Script "Before Website Render" → bypassed
- Tampermonkey userscript → works, but per-device only

A minimal fork is the only path that delivers themeing to **every user, every device, automatically** with no per-user setup.

## Recon findings — `frappe/insights` v3 source

**Chart palette is centralised in ONE file:**
- `frontend/src2/charts/colors.ts`
- Exports `COLOR_MAP` (an object of named hex values) and `getColors()` (returns `Object.values(COLOR_MAP)`).
- All chart series colours flow through this — verified in `helpers.ts` (5 call sites) and `Sparkline.vue`.
- **Git history: 3 commits ever, last touched 2025-01-01** (~16 months ago). Effectively static.

**KPI tile / dashboard styling is inline Tailwind utilities** in:
- `frontend/src2/charts/components/NumberChart.vue` — KPI cards use `class="... rounded bg-white shadow ..."`
- `frontend/src2/dashboard/VueGridLayout.vue` — `.vgl-layout` CSS lives here
- We don't edit these. We override them with high-specificity CSS using the same `[class*="rounded"][class*="bg-white"][class*="shadow"]` selector pattern proven in our userscript.

**Entry point** for adding overrides:
- `frontend/src2/main.ts`
- Already has `import './index.css'`. We add two more import lines below it.
- Git history: ~6 commits/year. Low churn. Adding lines at the bottom of the imports block has near-zero conflict risk.

## The override plan (pure additive — only `main.ts` is upstream-modified)

### File 1 (new) — `frontend/src2/syncflo-custom-overrides.css`

Visual overrides for the dashboard canvas, KPI tiles, hero chart, tables, headers, row hover. Approximately the same content as `templates/dashboard-theme-soft-professional.css` in the knowledge base.

Uses high-specificity selectors with `!important` to win over Insights' Tailwind utilities. Examples:

```css
.vgl-layout { background: #f5f6f8 !important; padding: 8px !important; }

.vgl-item:nth-child(1) [class*="rounded"][class*="bg-white"][class*="shadow"] {
  background: linear-gradient(140deg, #6b85a3 0%, #4a6580 100%) !important;
  box-shadow: 0 4px 18px rgba(107,133,163,0.30) !important;
  border-radius: 14px !important;
}
/* ... etc for KPIs 2-4, hero, tables, headers, hover ... */
```

### File 2 (new) — `frontend/src2/syncflo-custom-chart-palette.ts`

Mutates `COLOR_MAP` at module-load time so every subsequent `getColors()` call returns the soft palette. Works because `COLOR_MAP` is a mutable object exported as a named const, and JS modules are singletons.

```ts
import { COLOR_MAP } from './charts/colors'

// Soft Professional palette — replace the named-colour values
// (and the raw-hex aliases below them) with muted variants.
Object.assign(COLOR_MAP, {
  blue:   '#5e85a8',  // was #318AD8
  pink:   '#b07e7e',  // was #F683AE  ← the offending hot pink
  green:  '#7a9c7d',  // was #48BB74
  red:    '#a06868',  // was #F56B6B
  yellow: '#c4a373',  // was #FACF7A
  purple: '#8b7991',  // was #44427B
  teal:   '#85a0a8',  // was #5FD8C4
  orange: '#b08c75',  // was #F8814F
  cyan:   '#7a9eb0',  // was #15CCEF
  grey:   '#9aa1a6',  // was #A6B1B9
})
```

(The raw-hex aliases like `'#449CF0': '#449CF0'` we leave alone — those are user-pickable colours, intentionally varied.)

### File 3 (modified, +2 lines) — `frontend/src2/main.ts`

Right after the existing `import './index.css'` line, add:

```ts
import './blomo-chart-palette'
import './syncflo-custom-overrides.css'
```

That's the entire upstream change.

## Merge cost estimate

| File | Touched? | Last upstream change | Conflict probability |
|---|---|---|---|
| `colors.ts` | No (we mutate at runtime) | 2025-01-01 (16 months ago) | None — we don't edit it |
| `syncflo-custom-overrides.css` | New file | n/a | None ever |
| `syncflo-custom-chart-palette.ts` | New file | n/a | None ever |
| `main.ts` | +2 lines | ~6 commits/year | Low — only conflicts if upstream rewrites the imports block |

**Realistic ongoing cost: 0–5 minutes per Insights upgrade.** If `main.ts` ever conflicts on the import block, re-add the two lines. The override files themselves never conflict because upstream never touches them.

## Deploy sequence (Frappe Cloud)

1. **Push the unmodified clone to `Syncflo-design/insights` first** to establish a clean baseline (already in plan):
   ```
   cd /c/ClaudeCode/insights
   git remote rename origin upstream
   git remote add origin https://github.com/Syncflo-design/insights.git
   git push -u origin --all
   git push -u origin --tags
   ```

2. **Branch and apply the overrides**:
   ```
   git checkout -b syncflo-custom-theme
   # Add the two new files and edit main.ts (Claude can do this)
   git add .
   git commit -m "Add Syncflo custom theme overrides"
   git push -u origin syncflo-custom-theme
   ```

3. **On Frappe Cloud**: Bench → Apps → remove stock `insights` → Add App from GitHub → point at `Syncflo-design/insights`, branch `syncflo-custom-theme` → Deploy.

4. **Hard-refresh** any open Insights tab. Theme is now live for every user on the bench.

## Updating to a new Insights release

```
cd /c/ClaudeCode/insights
git checkout develop
git fetch upstream
git merge upstream/develop      # almost always clean
git push origin develop
git checkout syncflo-custom-theme
git merge develop                # almost always clean — re-add 2 import lines if conflicted
git push
```

Then bump the version on Frappe Cloud → Deploy.

## Tuning colours later

All colours live in **two files**:

- `frontend/src2/syncflo-custom-chart-palette.ts` → chart series colours (donut slices, bar fills, line strokes)
- `frontend/src2/syncflo-custom-overrides.css` → KPI tiles, dashboard canvas, table accents, headers

Edit, push to `syncflo-custom-theme` branch, redeploy. Done.

## Once this is deployed, the userscript becomes obsolete

The Tampermonkey userscript at `templates/insights-theme-all-sites.user.js` was the per-device workaround. After the fork is live, every visitor sees the theme without any browser extension.

You can either:
- Disable the userscript in Tampermonkey (cleanest), or
- Leave it running — it's idempotent against the fork's CSS so it does no harm.

Recommend disabling it so the next person who looks at the system has one fewer mechanism to understand.
