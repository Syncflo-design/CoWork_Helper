# STOCK TRANSFERS WAITING TO BE RECEIVED (Russell, 27 Oct 2026): the badge on the Stock Transfer
# tile (Nest Home), like the Request Stock / Issue Stock badges. Counts transfers still "Issued"
# into one of the caller's stores. The caller's stores are found the same way as
# nest_stock_request: every enabled POS Profile they are on, plus any Stock Request Settings
# store that names them.
user = frappe.session.user
profiles = frappe.get_all("POS Profile User", filters={"user": user, "parenttype": "POS Profile"}, pluck="parent")
whs = frappe.get_all("POS Profile", filters={"name": ["in", profiles], "disabled": 0}, pluck="warehouse") if profiles else []
whs = whs + frappe.get_all("Stock Request Store", filters={"parent": "Stock Request Settings", "user": user}, pluck="warehouse")
whs = [w for w in whs if w]

count = 0
if whs:
    count = frappe.db.count("Stock Transfer", {"workflow_state": "Issued", "docstatus": 0, "target_warehouse": ["in", whs]})
frappe.response["message"] = count
