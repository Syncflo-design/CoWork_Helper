# Insights v3 Dashboard Styling via Client Script

**Date:** 2026-05-06  
**Site:** blomoplastics  
**Status:** Working

## The Pattern

Insights v3 dashboards don't ship with a `custom_css` field. To style the dashboard (rounded corners, background colors, shadows, hover effects), inject CSS via a **Client Script** scoped to `Insights Dashboard v3`.

## Example: Manufacturing Operations Dashboard

Created `Client Script` with name `Manufacturing Operations Dashboard Styling`:
- `dt: "Insights Dashboard v3"`
- `enabled: 1`
- Script injects a `<style>` tag targeting `.vue-grid-layout .vue-grid-item:nth-child(N)` selectors

## Selector Strategy

The dashboard uses vue-grid-layout, which assigns grid items in order. Target by position:
- Positions 1–4: KPI cards → `.vue-grid-item:nth-child(1)` through `:nth-child(4)`
- Position 5: Bar chart → `.vue-grid-item:nth-child(5)`
- Positions 6–7: Tables → `:nth-child(6)` and `:nth-child(7)`

## What Works

- `border-radius` on `.chart-container`
- `box-shadow` (graduated for depth)
- `background: linear-gradient(...)` for KPI card backgrounds
- `transition` + `:hover` for interactive effects
- `padding` on `.vue-grid-item` for grid spacing

## Gotchas

1. **Must use `!important`** — Insights inlines styles; `!important` is necessary to override.
2. **Script fires before DOM fully renders** — Wrap in `setTimeout(fn, 100)` or DOMContentLoaded listener.
3. **No reload = stale cache** — Hard-refresh the dashboard in the browser after enabling the script.
4. **Grid position changes break selectors** — If you reorder cards on the dashboard, update the `:nth-child()` numbers.

## Next Steps for Improvements

- Add custom icons next to KPI labels (requires per-chart config edits)
- Number formatting (thousands separators, decimals)
- Conditional row coloring in tables (via data_query or chart config)
