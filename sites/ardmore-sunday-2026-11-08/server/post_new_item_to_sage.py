# A NEW IMPORTED ITEM GOES ON THE QUEUE (Russell, 6 Nov 2026). It used to be posted to all three Sage companies
# here, inside the import's own web request. A big sheet then timed out: ERPNext rolled back but Sage kept the
# items, which came back through the sync without their wholesale price or category (Nozy, KSI-00018).
# Server Script post-pending-items-to-sage now sends them, 25 at a time, so nobody has to split a sheet.
if doc.custom_from_import:
    frappe.db.set_value("Item", doc.name, "custom_sage_post_status", "Create", update_modified=False)
