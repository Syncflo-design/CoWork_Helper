# A Warehouse User Permission makes Stock Transfer look broken ("no items, no warehouses")

**Date:** 2026-07-20 · **Site:** ardmoreceramics.c.frappe.cloud · **Area:** Frappe user permissions

## Symptom

Store users report, in the custom Stock Transfer doctype: "there are no items to
transfer and no target warehouses to move the stock to", and the POS shows
"Items not found". Reads like missing data / a broken form. Nothing is broken.

## Cause

The shared till login (`testpos@mail.com`) had a **User Permission: Warehouse =
Finished Goods - ACT, apply_to_all_doctypes = 1**. That restricts EVERY
Warehouse link field for that user to one value, so on Stock Transfer:

- **Source** could only ever be Finished Goods - ACT — which held no stock, so
  the item picker (`in_stock_items`, filtered by source warehouse) was empty;
- **Target** excludes the source (`name != source`) — leaving zero options.

The user is boxed into a single warehouse and literally cannot transfer. The POS
symptom was the same root state: all stock sat in Main Distribution - ACT while
POS_Test2 sells from Finished Goods - ACT with `hide_unavailable_items` on.

## Fix

Deleted the Warehouse User Permission (kept the Company/POS Profile/Price List
ones — those scope the user to the TEST company without blocking the workflow).
Rule of thumb: **never give a warehouse-scoped User Permission to a user who
must perform transfers** — a transfer needs at least two visible warehouses.

## Diagnosis shortcut

`frappe_list("User Permission", filters=[["user","=","<user>"]])` before
believing any "dropdown is empty" report; then check `Bin` for where the stock
actually is (`group_by warehouse, actual_qty > 0`).
