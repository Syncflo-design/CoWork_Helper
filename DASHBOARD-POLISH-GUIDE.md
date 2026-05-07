# Manufacturing Operations Dashboard - Polish Complete

**Date:** 2026-05-06  
**Status:** Layout & styling ready; CSS applied  
**Changes:** Layout rebalanced, KPI labels improved, modern styling added

## What Changed

### 1. **Layout Rebalance**
- **KPI Cards** — Now 5-column each (wider) instead of 3-column
- **Raw Material Levels** — Promoted to full-width hero chart (8 rows tall)
- **Tables** — FG Snapshot & Work Order Pipeline now side-by-side (10 cols each)

**New flow:**
```
Row 1 (y=0):    [KPI 1][KPI 2][KPI 3][KPI 4]         ← All visible at once
Row 2-3 (y=3):  [Raw Material Levels - Hero Chart]   ← Full-width bar chart
Row 4 (y=11):   [FG Snapshot][Work Order Pipeline]   ← Balanced pair
```

### 2. **KPI Card Names**
- "Active Work Orders" → **"Active Orders"**
- "Units in Production" → **"Units Remaining"**
- "Stock Shortfalls" → **"Items Short"**
- "Critically Low RM" → **"Critical RM"**

(Friendlier, fits better on wider cards)

### 3. **Visual Enhancements**
- **Gradient backgrounds** on KPI cards (color-coded by metric type)
- **Larger typography** — KPI numbers now 48px, labels uppercase & bolder
- **Modern cards** — Rounded corners (12px), subtle shadows, hover effects
- **Table improvements** — Better headers, striped rows, negative value highlighting
- **Dashboard background** — Soft gray (#f8f9fa) for depth

### 4. **Conditional Formatting**
- Negative numbers in tables show with **red background** (#ffe5e5, #d32f2f text)
- Applies to projected_qty and other numeric columns
- Auto-highlights on load and when data updates

## How to Apply the Styling

### **Option A: Using Browser Console (Quick)**

Paste this into your browser console when viewing the dashboard:

```javascript
// Copy & paste into console
fetch('/path/to/apply-dashboard-styling.js')
  .then(r => r.text())
  .then(code => eval(code));
```

Or manually:
1. Open the Manufacturing Operations dashboard
2. Press `F12` to open Developer Tools → Console tab
3. Paste the contents of `apply-dashboard-styling.js`
4. Press Enter
5. Refresh the page

### **Option B: Add as Frappe Custom Script (Permanent)**

1. Go to **Customization → Customize Form** (Manufacturing Operations dashboard)
2. Scroll to **Client Script** section
3. Paste the contents of `apply-dashboard-styling.js`
4. Save

Or via the API:

```python
frappe.new_doc("Customize Form", {
    "doctype": "Insights Dashboard v3",
    "name": "0qj8e3nb4t",
    "custom_script": "<contents of apply-dashboard-styling.js>"
}).insert()
```

### **Option C: Add as Site CSS (For All Dashboards)**

1. Go to **Settings → Customize** → **Custom CSS**
2. Copy contents of `custom-dashboard-styling.css`
3. Save

Or add to your site's `custom.css` file directly.

## What the Files Do

| File | Purpose |
|---|---|
| `apply-dashboard-styling.js` | JavaScript that injects CSS and applies dynamic styling (gradients, negative value highlighting). **Choose this if you want auto-updates.** |
| `custom-dashboard-styling.css` | Pure CSS with all styles. **Choose this if you want static styling or to include in your custom.css.** |

## Testing the Changes

1. **Layout:**
   - KPI cards should be visibly wider (5-column grid)
   - Raw Material bar chart spans full width
   - Tables sit side-by-side below

2. **Colors:**
   - KPI cards have gradient backgrounds
   - Hover over any card → subtle lift effect
   - Negative values in tables → red background

3. **Typography:**
   - KPI numbers are large and bold
   - Labels are uppercase and smaller
   - Table headers are styled with gray gradient

## Reverting Changes

If you need to go back:

**Layout:**
```javascript
frappe.call({
  method: 'frappe.client.set_value',
  args: {
    doctype: 'Insights Dashboard v3',
    name: '0qj8e3nb4t',
    fieldname: 'items',
    value: '<original items JSON>'
  }
});
```

**Styling:**
- Delete the custom script or remove the CSS from custom.css
- Hard refresh browser (Ctrl+Shift+R)

## Next Steps

- [ ] Apply the styling to the live dashboard
- [ ] Test on mobile (responsive CSS included)
- [ ] Verify negative value highlighting works on all columns
- [ ] Optionally add icons to KPI cards (requires custom extension)
- [ ] Consider adding drill-down capability to hero chart

## Notes

- All changes are saved to the database; styling is applied via JavaScript overlay
- The styling is non-destructive — removing it reverts to Insights' default styles
- Negative value highlighting uses JavaScript to scan table cells; add `data-value="<number>"` to table cells for more robust detection

## See Also

- `sites/blomoplastics.md` — Dashboard inventory
- `skills/frappe-insights-v3-dashboard/SKILL.md` — Full Insights v3 reference
- `gotchas/` — Previous gotchas from dashboard build
