# Frappe 16.56: saved filters became "layouts" that keep one condition per field, and page button labels are now plain text

**Date:** 2026-11-12
**Domain:** Frappe v16.56 / ERPNext v16.54 — list views, saved filters, page actions
**Severity:** annoying (two silent regressions straight after a platform update)

## Symptom

1. After the update, the Sales Invoice list on nesterp stopped opening on "Hide All N N". It showed
   `Filters 1` (status != Cancelled), with Paid and Return invoices back in the list. The top-right
   dropdown still said "Hide All N N".
2. Buttons set with HTML labels showed the raw markup, e.g. a ToDo form button reading
   `<i class="fa fa-arrow-left" style="margin-right:6px;"></i>My Activities`.

## Cause

1. Saved filters (List Filter) are now selectable **layouts**, with new stored fields:
   `route_signature`, `columns`, `sort_field`, `sort_order`. On list open,
   `restore_layout_from_route_signature` matches the current filters (or the user's saved
   `active_layout_name`) to a layout and runs `apply_layout_state`, which **clears the filter area
   and sets the layout's filters**. It runs after `listview_settings.onload`, so it overrides
   anything the onload added. It reads the layout's filters through `ListView.validate_filters`,
   which does `uniqBy(fieldname)`. A saved filter with four `status != X` rows comes back as one row.
2. `frappe.ui.Page.set_action` (used by `set_primary_action` / `set_secondary_action`) now sets the
   label with `.text()`, not `.html()`.

## Fix

1. Store one condition per field. Use `not in` instead of repeated `!=`, and update
   `route_signature` to match, in the format the client builds:

```diff
- filters: [["Sales Invoice","status","!=","Cancelled"], ... x4]
+ filters: [["Sales Invoice","status","not in",["Cancelled","Paid","Credit Note Issued","Return"]]]
+ route_signature: status=["not in",["Cancelled","Paid","Credit Note Issued","Return"]]
```

   Make any list Client Script that adds the same default use the identical single condition, so
   the signature matches and the layout shows as active. To open on exactly the default (and not
   stack on last time's saved filters), do `filter_area.clear(false).then(() => filter_area.add(...))`,
   skipped when `frappe.route_options` is non-empty (drill-downs).
   The layout's `columns` JSON is now what drives that view's columns: remove a column there.

2. Pass the icon as the third argument instead of HTML in the label:

```diff
- page.set_secondary_action('<i class="fa fa-arrow-left" ...></i>My Activities', fn);
+ page.set_secondary_action(__('My Activities'), fn, 'arrow-left');
```

   `arrow-left` and `user` exist in the v16.56 icon sprite (check with
   `document.querySelector('symbol[id="icon-<name>"]')`).

## Why this is non-obvious

- The client script and saved filter were untouched by the update and still looked right in the
  database. The layout dropdown even showed "Hide All N N" as active while only one of its four
  conditions was applied.
- Calling `filter_area.add()` by hand with the four conditions works fine. The collapse only happens
  on the layout-restore path, which you only see by tracing `filter_area.clear` on page load.
- Every other saved filter with several conditions on one field is broken the same way. Check them
  after the update.
- Testing on a real login overwrites that user's saved list filters and active layout.

## See also

- `gotchas/2026-11-06-list-onload-filter-narrows-fresh-drilldown.md`
- `gotchas/2026-08-06-client-script-listview-settings-assignment-wipes-indicators.md`
