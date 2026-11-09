# ONE-OFF (2 Nov 2026): send the till price to Sage with no line discount on top.
# Replaces exactly one block in each posting script; refuses if the block is not found exactly once.
if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "System Manager"}):
    frappe.throw("Not permitted")

NOTE = ("                # The till price IS the selling price (ceramic pieces can be repriced on the till,\n"
        "                # 2 Nov 2026): rate already carries any line discount, so none is sent on top.\n")

patches = [
    ["post-taxinvoice-to-sage",
     "                \"discount\": float(item.discount_amount or 0),\n"
     "                \"discountPercentage\": round(float(item.discount_percentage or 0) / 100, 4),\n",
     NOTE + "                \"discount\": 0,\n                \"discountPercentage\": 0,\n"],
    ["post-customerreturn-to-sage",
     "                \"discount\": abs(float(item.discount_amount or 0)),\n"
     "                \"discountPercentage\": round(abs(float(item.discount_percentage or 0)) / 100, 4),\n",
     NOTE + "                \"discount\": 0,\n                \"discountPercentage\": 0,\n"],
]

result = {}
for p in patches:
    d = frappe.get_doc("Server Script", p[0])
    n = d.script.count(p[1])
    if n != 1:
        result[p[0]] = "skipped - block found " + str(n) + " times"
        continue
    d.script = d.script.replace(p[1], p[2])
    d.save()
    result[p[0]] = "patched"

frappe.response["message"] = result
