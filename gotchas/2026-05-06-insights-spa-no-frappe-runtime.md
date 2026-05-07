# Insights v3 is a Standalone SPA — Frappe Client Scripts & head_html Don't Reach It

**Date:** 2026-05-06  
**Site:** blomoplastics (confirmed; likely applies to all Insights v3 installs)  
**Status:** Confirmed via live DOM inspection

> **Update 2026-05-06 (later same day):** Per-device Tampermonkey was the *initial* workaround. We've since proven the **server-side fork-overlay** approach works on Frappe Cloud — see `playbooks/insights-fork-themeing.md`. That's the right answer when you need theming for every user on the site. The mechanisms in this gotcha (Client Script / head_html / Server Script) still don't work; the fork-overlay just bypasses them entirely by baking the CSS into the SPA bundle.

## The Gotcha

Frappe Insights v3 serves its dashboard UI as a **completely standalone Vue 3 / Vite SPA**. The page HTML is a bare custom template — `frappe` is never defined on the page, there is no `frappe.boot`, and the template does not go through Frappe's website renderer.

This means the following Frappe mechanisms **do NOT work** for injecting CSS/JS into Insights dashboards:

| Mechanism | Why it fails |
|---|---|
| `Client Script` (dt: "Insights Dashboard v3") | No `frappe.boot.user_scripts` on the page |
| `Website Settings.head_html` | Insights HTML is served outside Frappe's template system |
| `Website Settings.custom_css` | Same — not included in the Insights HTML |
| `Server Script` (Before Website Render) | Insights doesn't go through Frappe's web render pipeline |

## What the DOM Actually Looks Like

```html
<html lang="en" class="h-full bg-gray-100">
<head>
  <meta charset="UTF-8">
  <link rel="icon" href="/assets/insights/frontend/favicon.png">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Manufacturing Operations | Insights</title>
  <script type="module" src="/assets/insights/frontend/assets/main-2ffaabdc.js"></script>
  <!-- Only Insights CSS files follow — no Frappe CSS, no boot, no head_html -->
</head>
```

Grid structure (not `vue-grid-layout` as docs suggest — it's `vgl-layout`):

```
.vgl-layout                                ← dashboard background
  └─ section.vgl-item.vgl-item--transform  ← each chart tile
       └─ div.group.relative...p-2
            └─ div > div
                 └─ [KPI card]  div.flex...rounded.bg-white.shadow
                    [Table]     div.flex...divide-y.bg-white.shadow
```

## Working CSS Selectors (verified in browser)

```css
/* Grid */
.vgl-layout { ... }                     /* dashboard bg */
.vgl-item:nth-child(N) { ... }          /* nth tile */

/* KPI card inner */
.vgl-item:nth-child(1) [class*="rounded"][class*="bg-white"][class*="shadow"] { ... }

/* Table card inner */
.vgl-item:nth-child(6) [class*="divide-y"][class*="bg-white"][class*="shadow"] { ... }

/* Table headers */
thead.sticky { ... }
thead.sticky td { ... }
```

## The Fix: Tampermonkey Userscript

The only persistent injection mechanism that works is a **browser userscript** (Tampermonkey or Violentmonkey).

The working userscript is saved at:
`templates/blomoplastics-insights-theme.user.js`

Install once per browser, runs automatically on every `/insights/*` page load.

### Install steps
1. Install [Tampermonkey](https://www.tampermonkey.net/) from the Chrome Web Store
2. Open `C:\ClaudeCode\CoWork_Helper\templates\blomoplastics-insights-theme.user.js`
3. Drag the file onto the Chrome window → Tampermonkey prompts to install → click Install
4. Hard-refresh the Insights dashboard — styling applied permanently

## Layout Convention for Future Dashboards

The userscript uses **positional selectors** (nth-child), not chart-name selectors. As long as each new dashboard follows the same layout:

```
positions 1–4: KPI cards  (indigo / teal / amber / red)
position 5:    hero chart  (white + indigo top border)
positions 6–7: tables      (teal + indigo top borders)
```

…the same userscript works for all dashboards on the site with no changes.

If a dashboard has a different layout (e.g. 3 KPIs + 1 hero + 3 tables), add dashboard-specific CSS blocks to the userscript gated by `window.location.pathname`.
