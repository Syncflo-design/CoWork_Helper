# Give every newly created Item an 8-digit POS barcode and register it in the
# standard Item Barcode table so the till can scan it. Internal use only - this
# number is never sent to Sage.
#
# No frappe.db.commit() here: DocType Event scripts run with commit/rollback
# stripped from the sandbox. The request commits on its own.

if not doc.get("custom_pos_barcode"):
    last = frappe.get_all(
        "Item",
        filters={"custom_pos_barcode": ["is", "set"]},
        fields=["custom_pos_barcode"],
        order_by="custom_pos_barcode desc",
        limit_page_length=1,
    )

    if last:
        nxt = int(last[0]["custom_pos_barcode"])
    else:
        nxt = 10000000

    nxt = nxt + 1
    while frappe.db.exists("Item Barcode", {"barcode": str(nxt)}):
        nxt = nxt + 1

    number = str(nxt)

    frappe.db.set_value("Item", doc.name, "custom_pos_barcode", number, update_modified=False)

    row = frappe.new_doc("Item Barcode")
    row.parent = doc.name
    row.parenttype = "Item"
    row.parentfield = "barcodes"
    row.barcode = number
    row.insert(ignore_permissions=True)
