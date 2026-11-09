# A default filter added in a list `onload` also narrows a Customer drill-down, but only on a fresh page

**Date:** 2026-11-06
**Domain:** Frappe v16 / ERPNext — Client Script (List view)
**Severity:** annoying (silent, and it makes the numbers look wrong)

## Symptom

Adding `status != Paid` (and others) to `Sales Invoice - Hide Cancelled` on nesterp worked on a plain
open. A drill-down with `route_options = {customer: 'Com-Struct'}` then gave two different answers:

```
list already open in this page load:  [customer = Com-Struct]                              5 rows
first open after a page load:         [status != Paid, ..., customer = Com-Struct]         2 rows
```

The second one hides the customer's Paid invoices with nothing to say so except the filter count.

## Cause

`onload` only runs when the list view is first built. On that first build it runs while
`frappe.route_options` is still pending, so `filter_area.add()` overlaps the `clear` and `set` that
the list then does for the route options, and some of the added conditions survive. Once the view
exists, the route options simply replace the filters, which is why a second drill-down looks fine.

The old `status != Cancelled` filter had the same overlap, but nobody would notice it.

## Fix

Skip the default filter when arriving with route options:

```diff
- listview.filter_area.add([...]);
+ if (!Object.keys(frappe.route_options || {}).length) {
+     listview.filter_area.add([...]);
+ }
```

Check for an empty object, not just falsy.

Verified on nesterp: plain open gives the 4 conditions, fresh drill-down gives the customer filter
only with all 5 rows, statuses and the hidden Add button unchanged.

## Why this is non-obvious

- It passes a plain-open test, and a drill-down test too if the list was opened first in that page
  load. You only see it by reloading the page and making the drill-down the first open.
- Do not "fix" the remaining stickiness by re-applying the filter every time the list is shown:
  that also fires on Back from an invoice and wipes the view the user was working in.
- Remaining behaviour: `onload` does not fire again until a reload, so returning to the list after a
  drill-down without reloading keeps that customer's filter. Normal Frappe list behaviour.
- Testing on a real login overwrites that user's saved list filters. Clear them when you finish.

## See also

- `gotchas/2026-08-06-client-script-listview-settings-assignment-wipes-indicators.md`
- `gotchas/2026-05-11-frappe-v16-modern-desk-listview-hooks-untrustworthy.md`
- The script is DB-only on nesterp (no fixture). It keeps its old name but now applies all 4 conditions
  of the saved `Hide All N N` list filter as its own copy, so edits to the saved filter do not carry over.
