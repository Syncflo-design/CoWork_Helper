# Child-table grid columns: a saved per-user layout silently beats your Property Setters

**Date:** 2026-08-24
**Domain:** Frappe v16 / ERPNext (nesterp)
**Severity:** annoying (looks like a caching bug, isn't)

## Symptom

Asked to add **Description** and remove **Warehouse** from the Items grid on the Sales
Invoice form. Did it properly via Property Setters on the child DocType:

```
Sales Invoice Item-description-in_list_view = 1
Sales Invoice Item-warehouse-in_list_view   = 0
+ columns widths totalling 10
```

Verified the Property Setters existed. Reloaded. Hard-reloaded. Cleared cache. The grid
still rendered the old columns:

```
No | Item | Quantity | Rate (ZAR) | Discount (%) | Amount (ZAR) | Warehouse
```

Note the giveaway that got missed at first: **`Discount (%)` was in the grid but its
`in_list_view` was 0 in the DocType meta.** The screen was not rendering the meta at all.

## Cause

The user had previously used the grid's ⚙ (gear) icon to pick columns. Frappe persists
that choice **per user, per parent doctype** in the `__UserSettings` table under a
`GridView` key, and a saved `GridView` **completely replaces** the `in_list_view` /
`columns` fields from the DocType meta. Property Setters never get a look-in.

```sql
select user, doctype, data from __UserSettings where data like '%GridView%';
```

```
Administrator            | Sales Invoice | Sales Invoice Item
    -> item_code, qty, rate, discount_percentage, amount, warehouse
presales@syncflo.co.za   | Sales Invoice | Sales Invoice Item
    -> item_code, qty, price_list_rate, discount_percentage, amount
```

Two different users, two different grids, neither matching the doctype. Whoever reports
"the change didn't work" may simply be the one user with a saved layout — and other users
on the same site will see the new columns just fine, which makes it look non-deterministic.

## Fix

**The user does it, in one click:** grid header ⚙ → **Reset to default**. That deletes the
saved `GridView` and the doctype meta (your Property Setters) takes over. To keep a
hand-picked column set instead, tick/untick in that same dialog rather than resetting.

**You (over MCP/console) cannot do it for them.** Two hard walls:

1. `__UserSettings` is a plain SQL table, not a DocType — no `frappe.db.set_value`,
   no `frappe.get_doc`.
2. `frappe.db.sql` inside System Console / Server Scripts is read-only:

```
frappe.exceptions.PermissionError: Read-Only queries are allowed
  File "apps/frappe/frappe/utils/safe_exec.py", line 759, in check_safe_sql_query
```

`frappe.model.utils.user_settings.update_user_settings()` only ever writes
`frappe.session.user`, so even calling it over MCP just edits the API user's own layout,
not the affected user's.

You *can* read the offending settings to diagnose (read-only SQL is allowed) — do that
first so you can tell the user exactly which of their logins is affected.

## Why this is non-obvious

- Every instinct says "stale cache". It survives Ctrl+F5, `bench clear-cache`, and a
  fresh Deploy, because it is data, not cache.
- Property Setters are the *correct* mechanism and they were correctly created —
  `frappe.get_meta()` on the server shows the new columns. The server is right; only the
  one browser session is wrong.
- Customize Form's own UI shows your change as applied, giving false confirmation.
- It is per user, so it reproduces for one person and not another. Easy to chase as a
  role/permission problem.
- **Tell:** if the grid shows a column whose `in_list_view` is 0, stop touching Property
  Setters and go straight to `__UserSettings`.

## See also

- Related: `gotchas/2026-05-15-frappe-grid-edit-column-leftover-flex-space.md`
- Related: `gotchas/2026-05-20-frappe-deploy-overwrites-doctype-permissions.md`
  (same family — the DB copy of a setting diverging from the app/meta copy)
- Frappe source: `frappe/public/js/frappe/form/grid.js` (`get_docfields` /
  `set_column_disp`), `frappe/model/utils/user_settings.py`
- Rule of thumb: **meta defines the default grid; `__UserSettings.GridView` defines what
  that user actually sees.**
