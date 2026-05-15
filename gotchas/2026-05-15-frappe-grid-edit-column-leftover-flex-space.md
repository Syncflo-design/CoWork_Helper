# Frappe grid's "wide edit/pencil column" is usually leftover flex space, not the column

**Date:** 2026-05-15
**Domain:** Frappe / ERPNext — client-side, `frappe.ui.Dialog` Table grids
**Severity:** annoying

## Symptom

In a `frappe.ui.Dialog` Table-field grid, the row-edit (pencil) column on the
right looks far too wide — a dead band sits between the last data column and the
right edge of every row. Shrinking the pencil button (`.btn-open-row`) and its
`.col` with CSS makes the pencil itself tiny, but the empty band stays put.

## Cause

The dead band is **unallocated flexbox space**, not the edit column.

`.data-row` is `display:flex`. Field columns use Bootstrap-ish `col-xs-N`
classes — width `N/12`, so 1 unit ~= 60px in a 720px grid. Frappe's
`setup_visible_columns` caps the running total of field `columns` at ~10 units
(counter starts at 1 for the index col, stops once it would exceed 11). So
`row-check` (~31px) + the pencil col + 10 units of fields never fills the
12-unit row — the ~50px shortfall pools at the end of the row, right after the
pencil, and reads as a fat pencil column.

Second trap: `col-xs-N` sets **both** `flex-basis: N/12` **and**
`max-width: N/12`. `flex-grow:1` alone will not widen a column — the
`max-width` cap blocks it.

## Fix

Let one field column absorb the slack — override **both** `flex-grow` and
`max-width`, scoped to the dialog with a wrapper class
(`d.$wrapper.addClass('qi-dialog')` after building the dialog):

```css
.qi-dialog .grid-body .data-row .col[data-fieldname="description"],
.qi-dialog .grid-heading-row .col[data-fieldname="description"]{
  flex-grow: 1 !important;
  max-width: none !important;
}
```

To genuinely shrink the pencil column itself (a separate concern from the band):

```css
.qi-dialog .grid-body .col:has(.btn-open-row),
.qi-dialog .grid-heading-row .col:last-child{
  flex: 0 0 36px; max-width: 36px; min-width: 36px;
  padding-left: 2px; padding-right: 2px;
}
.qi-dialog .btn-open-row{ padding: 0; min-width: 0; }
```

## Why this is non-obvious

The dead band looks exactly like a too-wide edit column, so you target
`.btn-open-row` — and that *does* shrink the pencil, which feels like progress
while the band stubbornly stays. The truth only shows up when you measure
`getBoundingClientRect()` on every column: the pencil `.col` is already 36px and
there is a separate ~50px gap between its right edge and the row's. Likewise
`flex-grow:1` silently no-ops until you also kill `max-width`, which tempts you
to conclude "the row isn't flex" and chase the wrong layout model — it *is*
flex; the blocker is `max-width`. And bumping a field's `columns` to fill the
gap backfires: push the sum past 10 and `setup_visible_columns` drops your last
column(s) outright.

## See also

- Related: `gotchas/2026-05-06-frappe-dynamic-link-in-grid.md`,
  `gotchas/2026-05-11-frappe-v16-modern-desk-listview-hooks-untrustworthy.md`
- Site: `sites/nesterp.md` — found while editing the `Customer-Quick-Invoice`
  Client Script (the quick Sales Invoice dialog on the Customer form)
