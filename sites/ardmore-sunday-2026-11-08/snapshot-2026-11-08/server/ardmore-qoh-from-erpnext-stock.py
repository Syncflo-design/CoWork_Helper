# Keeps Item.custom_quantity_on_hand truthful for items the Sage QOH sync skips.
#
# Why this exists: custom_quantity_on_hand was only ever written by
# get-inventory-qtyonhand-for-erpnext. Items carrying custom_qty_pending_sage are
# skipped by that sync (by design - their stock was added in ERPNext and Sage does
# not know about it), so the field froze at its last Sage value while real stock
# moved underneath it. On 2026-08-17 that was 6,444 items, most showing 0 while
# holding 20.
#
# Why a scheduled job and NOT a Stock Ledger Entry hook: erpnext's make_sl_entries
# writes every SLE first and only then calls update_bin_qty. Any doctype event on
# SLE therefore reads the PREVIOUS bin figure. Reading Bin on a timer avoids the
# ordering problem entirely.
#
# Scope is deliberately narrow - only flagged items. Untick custom_qty_pending_sage
# and this job stops touching the item, handing the field straight back to Sage.

actual = {}
for b in frappe.get_all("Bin", filters={"actual_qty": ["!=", 0]}, fields=["item_code", "actual_qty"], limit_page_length=0):
    c = b["item_code"]
    if c not in actual:
        actual[c] = 0.0
    actual[c] = actual[c] + float(b["actual_qty"] or 0)

changed = 0
n = 0
for it in frappe.get_all("Item", filters={"custom_qty_pending_sage": 1, "disabled": 0, "is_stock_item": 1}, fields=["name", "custom_quantity_on_hand"], limit_page_length=0):
    a = actual.get(it["name"]) or 0.0
    q = it["custom_quantity_on_hand"]
    if q is None:
        q = 0.0
    if float(q) != a:
        frappe.db.set_value("Item", it["name"], "custom_quantity_on_hand", a, update_modified=False)
        changed = changed + 1
        n = n + 1
        if n >= 200:
            frappe.db.commit()
            n = 0

frappe.db.commit()
