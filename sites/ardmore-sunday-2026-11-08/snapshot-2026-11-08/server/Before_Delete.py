# Item Before Delete: clear Sage Item Selection + Item Price links so the item deletes cleanly (UAT).
sel_rows = frappe.get_all("Sage Item Selection", filters={"item_code": doc.name}, fields=["name"])
for i in range(len(sel_rows)):
    frappe.delete_doc("Sage Item Selection", sel_rows[i]["name"], force=1, ignore_permissions=True)

ip_rows = frappe.get_all("Item Price", filters={"item_code": doc.name}, fields=["name"])
for i in range(len(ip_rows)):
    frappe.delete_doc("Item Price", ip_rows[i]["name"], force=1, ignore_permissions=True)