# Frappe dialog-grid per-cell `onchange` always fires with the FIRST row's `this`

**Date:** 2026-05-15
**Domain:** Frappe / ERPNext — client-side, `frappe.ui.Dialog` Table grids
**Severity:** day-killer

## Symptom

In a `frappe.ui.Dialog` with a `Table` field, a child field's `onchange` handler
works perfectly on the first row, but on every row added afterwards it appears to
do nothing — dependent fields never populate. (E.g. picking an Item on row 2+
doesn't fill in description / rate, while row 1 fills in fine.)

## Cause

All rows of a dialog grid share ONE child field-definition object (`df`). When a
cell value changes, Frappe invokes `df.onchange` — but `this` is **not** the
control of the row you edited. It is always the **first row's** control. So
`this.grid_row`, `this.doc` and `this.value` all refer to row 0, no matter which
row actually changed.

Row 0 works only because `this` happens to be row 0's control. Edits on any
added row get applied to row 0 (or look like they do nothing on the row you
touched).

Verified: wrapping the shared `df.onchange` showed every invocation reporting the
same `grid_row`; and `df.onchange.call(rowN_control)` worked correctly — proving
the handler logic was fine and only the trigger's `this` was wrong.

## Fix

Don't use the per-cell `onchange` for anything that needs to know its own row.
Use a **delegated listener on the grid wrapper** and resolve the row from the
actual event target:

```js
let $gw = $(grid.wrapper);
$gw.on('change awesomplete-selectcomplete', '.col[data-fieldname="item_code"] input', function () {
    let row_el = this.closest('.grid-row');
    let gr = (grid.grid_rows || []).find(g => g.wrapper && g.wrapper[0] === row_el);
    if (!gr) return;
    let value = (this.value || '').trim();
    // ...do the per-row work against `gr` (gr.doc, gr.refresh_field(...)) ...
});
```

Delegation on the stable grid wrapper also means rows added later are covered
automatically — no re-wiring per row. `awesomplete-selectcomplete` bubbles, so
Link-field dropdown picks are caught too (listen for `change` as well to cover
typed-and-blurred values).

## Why this is non-obvious

The first row always works, so it reads like a timing / race condition with
added rows rather than a `this`-binding bug. You will waste time inspecting the
added-row controls — and they look fine: `control.grid_row` and `control.doc`
correctly point at their own row. The lie is only in what `this` is *at onchange
invocation time*. Confirm fast by logging `this.grid_row.doc.name` inside the
handler — it is the first row's name for every row.

Handlers that don't use `this` at all (e.g. `onchange: () => recalc_total()`
that just iterates `grid.grid_rows`) are unaffected — which can make the failure
look field-specific and send you down the wrong path.

## See also

- `gotchas/2026-05-15-frappe-grid-edit-column-leftover-flex-space.md` — same
  screen (`Customer-Quick-Invoice`, the quick Sales Invoice dialog on the
  Customer form).
- `sites/nesterp.md`
