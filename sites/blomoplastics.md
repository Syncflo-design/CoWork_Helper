# blomoplastics.jh.frappe.cloud

Plastics manufacturer. Frappe Cloud instance. ERPNext + Insights v3.

## MCP connector

`frappe-blomo` (configured globally for this user).

## Workbooks

| ID | Title | Notes |
|---|---|---|
| 1 | Manufacturing Operations | Live; built 2026-05-06 |
| 2 | MD Overview | Live; built 2026-05-06 |

## Dashboards

### MD Overview (`2uljes564g`)

**URL:** `https://blomoplastics.jh.frappe.cloud/insights/dashboards/2uljes564g`

13 items (10 charts + 2 date filters + 1 invisible spacer) — financial/executive layout, AR row above AP row:

```
[From Date][To Date  ][   <invisible spacer text>      ]  ← w=4, w=4, w=12, h=1, y=0
[Total Revenue][Receivables][Open Orders][Payables]       ← w=5 each, h=3, y=1
[Revenue Trend (line) ][Revenue by Customer (donut) ]     ← w=10 each, h=9, y=4   AR row
[AP by Supplier table ][Items Purchased by Value (bar)]   ← w=10 each, h=9, y=13  AP row
[Open Sales Orders    ][Outstanding POs              ]    ← w=10 each, h=8, y=22
```

**Important — items array order:** the two date filters and the spacer text item sit at the **end** of the `items` array. DOM order matters because of `:nth-child(N)` theme selectors; visual position is via `layout.y/x`. Chart order in array stays at indices 0-9 so the Soft Professional theme keeps working. See gotcha [`2026-05-06-insights-filter-order-vs-css-nth-child.md`](../gotchas/2026-05-06-insights-filter-order-vs-css-nth-child.md).

**Why the spacer:** vue-grid-layout vertically compacts by default (per-browser localStorage flag, not the dashboard's `vertical_compact_layout` field). With only filters in row y=0, the empty x=8–19 span lets KPIs 3 & 4 hoist up — and the AR-row donut follows them. The spacer text occupies x=8–19 at y=0 to lock the layout. See [`2026-05-06-insights-vue-grid-vertical-compact.md`](../gotchas/2026-05-06-insights-vue-grid-vertical-compact.md).

**Theme:** Soft Professional via the Insights fork (server-side, all users). The line chart slot now occupies what was the donut's hero-rule index (`:nth-child(5)`) so it gets the slate-blue top border — appropriate. Donut moves to `:nth-child(6)` (sage top border) and AP table to `:nth-child(7)` (slate-blue top border). Bottom 2 tables (`:nth-child(8)` and (9)) are unstyled.

**Date filters (split into From + To):**
- `From Date` — type `Date`, operator `>=`, default `2024-01-01`
- `To Date` — type `Date`, operator `<=`, default `2030-12-31`
- Both linked to the same chart-column pairs:
  - Total Revenue KPI → `\`etmsud9nfl\`.\`posting_date\``
  - Open Orders KPI → `\`5tnndactf5\`.\`transaction_date\``
  - AP by Supplier table → `\`0tpba89nnn\`.\`posting_date\``
  - Open Sales Orders table → `\`etp1vds1qb\`.\`transaction_date\``
  - Outstanding POs table → `\`ebtv93o772\`.\`transaction_date\``
  - Revenue Trend → `\`etmsud9nfl\`.\`posting_date\``
  - Items Purchased by Value → `\`8eee109eqd\`.\`posting_date\``
- The two filters' adhoc filters are pushed into the same per-query filter group with `logical_operator: "And"`, so effectively `WHERE col >= from AND col <= to`.
- **NOT** linked to: Receivables KPI, Payables KPI, Donut (point-in-time / all-time metrics).

Source queries (all `type: "sql"`, data source `"Site DB"`):

| Chart | Query | What it shows |
|---|---|---|
| KPI: Total Revenue | `etmsud9nfl` | **REFACTORED 2026-05-06**: row-level Sales Invoice w/ `posting_date`, `posting_month`, `revenue`. Aggregation lives in data_query `4u1nq2dqen` (sum). |
| KPI: Receivables | `7tn902euo5` | `SUM(outstanding_amount) tabSales Invoice docstatus=1 outstanding>0` (untouched — not date-filtered) |
| KPI: Open Orders | `5tnndactf5` | **REFACTORED 2026-05-06**: row-level Sales Order w/ `transaction_date`, `open_orders`. Aggregation in data_query `5u2bpkiq3k`. |
| KPI: Payables | `4to4inm6o5` | `SUM(outstanding_amount) tabPurchase Invoice docstatus=1 outstanding>0` (untouched — not date-filtered) |
| Line: Revenue Trend (Monthly) | uses `etmsud9nfl` source; data_query `fkj152m5q1` summarizes by `posting_month`, sum(`revenue`); chart `bkq2dlva5b` | Monthly revenue trend — order_by lives in chart config, NOT data_query (see gotcha) |
| Donut: Revenue by Customer | `btoivinpgm` | `tabSales Invoice GROUP BY customer` (untouched) |
| Table: AP by Supplier | `0tpba89nnn` | **REFACTORED 2026-05-06**: row-level Purchase Invoice w/ `posting_date`, `supplier`, `outstanding`. data_query `2u3g8u96m9` summarizes by supplier. |
| Bar: Items Purchased by Value | source `8eee109eqd` (rows: item_code, item_name, amount, posting_date, supplier — comma-join `tabPurchase Invoice Item, tabPurchase Invoice WHERE pii.parent = pi.name AND pi.docstatus = 1`); data_query `2g8qrd0vtc` summarizes by `item_name`, sum(`amount`); chart `aghga3odgd` | **NEW 2026-05-06** — top items by total purchase spend. Uses comma-join because explicit JOIN routes child to wrong schema (see gotcha) |
| Table: Open Sales Orders | `etp1vds1qb` | `tabSales Order docstatus=1, status NOT IN (Completed,Cancelled)` — already row-level, has `transaction_date` |
| Table: Outstanding POs | `ebtv93o772` | `tabPurchase Order docstatus=1, status NOT IN (Completed,Cancelled)` — already row-level, has `transaction_date` |

### Manufacturing Operations (`0qj8e3nb4t`)

**URL:** `https://blomoplastics.jh.frappe.cloud/insights/dashboards/0qj8e3nb4t`

7 tiles, modern layout (polished 2026-05-06):

```
[KPI 1  ][KPI 2  ][KPI 3  ][KPI 4  ]      ← w=5 each, h=3, gradient backgrounds
[Raw Material Levels - Hero Chart   ]     ← w=20, h=8, full-width bar
[FG Snapshot   ][Work Order Pipeline]    ← w=10 each, h=7, side-by-side tables
```

**Styling:** Modern card design, gradient KPI backgrounds, shadow depth, conditional row coloring on tables. See `DASHBOARD-POLISH-GUIDE.md`.

Source queries (all use `type: "sql"` with `raw_sql`, data source `"Site DB"`):

| Chart | Query name | Measure Name | What it shows |
|---|---|---|---|
| KPI: Active Orders | `dodbej7124` | "Active Orders" | `COUNT(*) tabWork Order WHERE status IN ('In Process','Not Started')` |
| KPI: Units Remaining | `apm77goiea` | "Units Remaining" | `SUM(qty - produced_qty)` over same WHERE |
| KPI: Items Short | `3pmpcanala` | "Items Short" | `COUNT(*) tabBin WHERE projected_qty < 0` |
| KPI: Critical RM | `4pubtksmbm` | "Critical RM" | `COUNT(*) tabBin WHERE actual_qty < 50 AND warehouse LIKE '%Raw Materials%'` |
| Bar: Raw Material Levels | `epnnjear5u` | "Stock Level" | `tabBin × tabItem JOIN, RM warehouses, ORDER BY actual_qty DESC` |
| Table: Finished Goods Snapshot | `1poe3obcfm` | n/a | `tabBin item_code, actual_qty, reserved_qty, projected_qty WHERE warehouse LIKE '%Finished Goods%'` |
| Table: Work Order Pipeline | `cpo7bll6sf` | n/a | `tabWork Order full row, docstatus<2, ORDER BY planned_start_date` |

Removed during build (data was empty):
- WIP Materials (`1popttvb7h`) — `tabBin warehouse LIKE '%Work-In-Progress%' AND actual_qty > 0` returns 0 rows; query is correct, just no stock in WIP warehouses currently.

## Quirks

- Workbook ID stored on parent docs as `"1"` (string) but inside `source` operations as `1` (integer). Don't mix.
- `Site DB` is the data_source name — not "Local DB" or "MariaDB" etc.

## Polish Pass — Completed 2026-05-06

✓ **Layout rebalanced** — KPI cards widened to 5-col, Raw Material Levels promoted to full-width hero chart, tables moved to side-by-side layout  
✓ **KPI labels improved** — "Active Orders", "Units Remaining", "Items Short", "Critical RM" (friendlier names)  
✓ **Modern styling** — Gradient backgrounds on KPI cards, larger typography, rounded corners, shadow depth, hover effects  
✓ **Conditional formatting** — Negative values in tables highlighted in red (#ffe5e5)  

**Styling applied via:** Client Script `Manufacturing Operations Dashboard Styling` (injected CSS via JavaScript)

### Latest Polish Pass — 2026-05-06 (afternoon)

✓ **KPI background color** — Light blue gradient (#f0f7ff to #e8f1ff) with rounded corners (12px)  
✓ **Bar chart rounded corners** — 16px radius with enhanced shadow (0 4px 12px)  
✓ **Table rounded corners** — 12px radius, consistent with other cards  
✓ **Hover effects** — Smooth lift (2px translateY) + shadow enhancement on all cards  
✓ **Shadow depth** — Graduated: KPI/table 0 2px 8px, bar chart 0 4px 12px, hover 0 6px 16px  
✓ **Grid spacing** — Improved padding between cards (8px)

### Theme Enhancement — 2026-05-06 (session 2) — FINAL WORKING APPROACH

✓ **Industrial Pro v2 theme applied** via Client Script `Manufacturing Operations Dashboard Styling`  
✓ **Distinct KPI colors** — Active Orders: Indigo, Units Remaining: Teal, Items Short: Amber→Orange, Critical RM: Deep Red  
✓ **Colored glow shadows** on KPI cards (match gradient color at 40% opacity)  
✓ **Top-border accents** on hero chart (Indigo) and tables (Teal + Indigo)  
✓ **Dashboard background** — cool gray #eef1f7  
✓ **Table improvements** — uppercase headers, striped rows, blue hover, negative value red highlighting  
✓ **CSS template saved** to `templates/dashboard-theme-industrial-pro.css` + `.js` for reuse on next 2 dashboards

**KEY FINDING:** Insights v3 is a standalone Vue SPA — `frappe` is not defined. Client Scripts, Website Settings head_html, and Server Scripts do NOT work for styling. The only persistent mechanism is a **Tampermonkey userscript**.

**Working selectors (verified in live browser):**
- Grid: `.vgl-layout` (not `.vue-grid-layout`)
- Tiles: `.vgl-item:nth-child(N)` (not `.vue-grid-item`)
- KPI card: `[class*="rounded"][class*="bg-white"][class*="shadow"]`
- Table card: `[class*="divide-y"][class*="bg-white"][class*="shadow"]`
- Table head: `thead.sticky td`

**Userscript:** `templates/blomoplastics-insights-theme.user.js`  
Install: Tampermonkey → drag `.user.js` file onto Chrome → Install → hard refresh dashboard  

### Remaining (future):
- Highlight overdue Work Orders (needs `planned_start_date` logic)
- Add icons to KPI cards (custom extension)
- Number formatting (thousands separators, decimals)

### Palette switch — 2026-05-06 (session 3)

Russell preferred a softer, more professional palette than Industrial Pro — particularly objected to anything pink-leaning. **Industrial Pro retired**, replaced by **Soft Professional**:

| Position | Mfg Ops (default) | MD Overview override |
|---|---|---|
| KPI 1 | Slate blue `#6b85a3 → #4a6580` | Steel blue `#5e85a8 → #3f6182` |
| KPI 2 | Sage green `#82a085 → #5d7a60` | Soft sage `#7a9c7d → #557556` |
| KPI 3 | Soft amber `#c4a373 → #99794d` | Muted plum `#8b7991 → #614f68` |
| KPI 4 | Dusty rose `#b07e7e → #855555` | Warm taupe `#b08c75 → #836552` |

Shadow opacity dropped from 0.45 → 0.30 across the board. Background lifted from `#eef1f7` → `#f5f6f8` (default) / `#f4f5f9` (MD Overview).

Changes applied to:
- `templates/insights-theme-all-sites.user.js` — version bumped to 3.0, style ID `insights-soft-professional`
- `templates/dashboard-theme-soft-professional.css` — replaces `dashboard-theme-industrial-pro.css` (deleted)

Tampermonkey will pick up the userscript change automatically; hard-refresh each dashboard (Ctrl+Shift+R) to see the new colours.

### Userscript v4.0 — Chart palette recolourer added

The donut/bar/line chart series colours come from the Insights chart library and were not affected by earlier theme versions (which only re-skinned tiles). v4.0 adds an SVG fill remapper that, on each chart inside a `.vgl-item`:

- Walks `path[fill]`, `rect[fill]`, `circle[fill]`, `polygon[fill]`, plus `path[stroke]` and `line[stroke]`
- Skips neutral fills (white, black, near-white, low-saturation greys)
- Remaps the unique series fills to the site palette (KPI gradient `from` colours + 6 muted extras), in order of first appearance
- Also remaps inline `style="background-color: ..."` on legend swatches so the legend stays synced
- Idempotent — fills already in the palette are skipped, so the MutationObserver re-render loop can't cycle colours

This kills the default hot-pink slice in the Revenue-by-Customer donut on MD Overview (it now becomes soft sage, since steel blue is the largest slice).

### KPI drill-through modal — pending deploy 2026-05-06

`syncflo-custom-drill-through.ts` added to the fork. On click, MD Overview's 4 KPI tiles open a modal showing the underlying records:

| Tile | DocType | Filters | Order |
|---|---|---|---|
| Total Revenue | Sales Invoice | `docstatus = 1` | `posting_date desc`, limit 200 |
| Outstanding Receivables | Sales Invoice | `docstatus = 1`, `outstanding_amount > 0` | `due_date asc`, limit 200 |
| Open Orders | Sales Order | `docstatus = 1`, `status not in (Completed, Cancelled)` | `transaction_date desc`, limit 200 |
| Accounts Payable | Purchase Invoice | `docstatus = 1`, `outstanding_amount > 0` | `due_date asc`, limit 200 |

Modal CSS lives in `syncflo-custom-overrides.css`. ERPNext list link in the footer takes the user to the full filtered list. Tiles are identified by `[dashboard_id, 1-indexed nth-of-type position]` — same pattern as the theme, no Vue-component edit required.

To extend to another tile: edit `DRILL_MAP` in the .ts file, push to `syncflo-custom-theme`, redeploy.

**Deploy required** before this is live — fork changes only take effect after a Frappe Cloud rebuild. Russell pushes from Windows host.

### Server-side theme via Insights fork — LIVE 2026-05-06

**Userscript is now superseded.** Theme is baked into the bench at the server level — every user, every device, no Tampermonkey required.

**Fork:** `https://github.com/Syncflo-design/insights` (branch `syncflo-custom-theme`, commit `9a121de`)

**What changed in the fork:** 2 new files + 2 import lines added to `frontend/src2/main.ts`. Pure additive overlay — no upstream files modified beyond those imports. See `playbooks/insights-fork-themeing.md` for the full design.

**Frappe Cloud workflow used:**
1. Bench Apps tab on `blomoplastics.jh.frappe.cloud` → "Change Source" on the Insights row
2. Pointed at `Syncflo-design/insights` branch `syncflo-custom-theme`
3. Frappe Cloud built and deployed (~5 min, first-try success)
4. Hard-refresh the dashboard — theme live

**To retune colours:** edit `frontend/src2/syncflo-custom-overrides.css` and `frontend/src2/syncflo-custom-chart-palette.ts` in the fork, push to the `syncflo-custom-theme` branch, redeploy via Frappe Cloud.

**To merge upstream Insights updates:** `git fetch upstream && git merge upstream/develop` on `develop`, then merge `develop` into `syncflo-custom-theme`. Conflicts on the 2 import lines in `main.ts` are the only realistic risk; ~5 min cost per release. See playbook for full procedure.

**Tampermonkey userscript status:** disabled. Kept on disk as fallback in case Frappe Cloud is mid-deploy or in case the fork ever needs to be reverted.
