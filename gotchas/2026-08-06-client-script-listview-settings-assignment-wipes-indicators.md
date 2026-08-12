# A List Client Script that *assigns* `frappe.listview_settings[dt]` wipes the app's own list settings — statuses go back to "Submitted"

**Date:** 2026-08-06
**Domain:** Frappe v16 / ERPNext — Client Script (List view)
**Severity:** annoying (silent, and it looks like a data bug)

## Symptom

On nesterp, Sales Invoices that were fully receipted and had `status = "Paid"` in the database
still showed **"Submitted"** in the Status column of `/app/sales-invoice`.

The Customer form's Recent Transactions panel showed the same invoices as **Paid** — so the data
was right and only the list view was wrong. No console errors.

## Cause

The `Sales Invoice - Hide Cancelled` Client Script did a straight **assignment**:

```js
frappe.listview_settings['Sales Invoice'] = {
    onload: function(listview) { ... }
};
```

List Client Scripts are evaluated **after** the app's own `<doctype>_list.js` bundle, so the
assignment replaced ERPNext's entire `sales_invoice_list.js` settings object — including
`get_indicator()`, `add_fields`, and `right_column`. With no `get_indicator`, Frappe's list falls
back to the generic docstatus label: Draft / **Submitted** / Cancelled.

Same defect existed on `Sales Order - Hide Cancelled` and on `nest-crm-todo-intercept`
(the ToDo one silently dropped Frappe's priority-colour indicators and `add_fields`).

## Fix

Merge into whatever is already there, and chain the original `onload` instead of clobbering it:

```diff
- frappe.listview_settings['Sales Invoice'] = {
-     onload: function(listview) {
-         listview.filter_area.add([['Sales Invoice', 'status', '!=', 'Cancelled']]);
-     }
- };
+ (function () {
+     let settings = frappe.listview_settings['Sales Invoice'] = frappe.listview_settings['Sales Invoice'] || {};
+     let original_onload = settings.onload;
+
+     settings.onload = function (listview) {
+         if (typeof original_onload === 'function') {
+             original_onload.call(this, listview);
+         }
+         listview.filter_area.add([['Sales Invoice', 'status', '!=', 'Cancelled']]);
+     };
+ })();
```

Same pattern for `formatters` / `add_fields`:

```js
settings.add_fields = (settings.add_fields || []).concat(['reference_type', 'reference_name']);
settings.formatters = Object.assign({}, settings.formatters, { description: fn });
```

`Lead List Status Colours` on the same site was already written this way — it's the reference
implementation.

## Why this is non-obvious

- It reads as a **data** problem ("the receipt didn't update the invoice"), not a UI one. The first
  instinct is to go check `status` / `outstanding_amount` in the database — which look fine.
- Nothing errors. Losing `get_indicator` just quietly downgrades to the docstatus indicator, and
  "Submitted" is a plausible-looking status for an invoice, so it doesn't scream *bug*.
- The Client Script that breaks it looks completely unrelated — its stated job is hiding cancelled
  rows and removing the "+ Add" button. Nobody greps a filter script when statuses look wrong.
- The blast radius is invisible: everything else `<doctype>_list.js` provides (extra fetched fields,
  right column, action items, settings) is gone too, so unrelated list features silently stop
  working at the same time.

## Where the fixed scripts live

- `Sales Invoice - Hide Cancelled`, `Sales Order - Hide Cancelled` — DB-only Client Scripts on
  nesterp (no repo copy).
- `nest-crm-todo-intercept` — shipped as a **fixture** in `nest_crm_tasks`, so the DB edit alone
  would be reverted by the next `bench migrate`. Fixed in
  `nest_crm_tasks/nest_crm_tasks/fixtures/client_script.json` as well.

## See also

- `gotchas/2026-05-11-frappe-v16-listview-formatters-stripped-to-text.md`
- `gotchas/2026-05-11-frappe-v16-modern-desk-listview-hooks-untrustworthy.md`
- `sites/nesterp.md`
