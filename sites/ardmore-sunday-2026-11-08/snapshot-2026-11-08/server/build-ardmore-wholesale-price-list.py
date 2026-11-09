# Ardmore - Wholesale = the stockist price list for the Account Sale screen (Jon, 26 Oct 2026:
# stockists pay the Wholesale list, same as Sage holds). Sage keeps one wholesale list per
# entity and the nightly price sync lands them in three ERPNext lists - VAT-INCLUSIVE, like
# every ERPNext price list here (the sync multiplies Sage's exclusive figure by 1.15 so the
# tills ring the list price as it stands). The screen can only use one list, so this job
# merges them: each item takes the price from ITS OWN entity's list (Item.custom_category),
# so a ceramic resold by Home never overrides Ceramics' own price; an item with no Category
# keeps whichever list set it first. Runs hourly; inserts what is missing, updates what changed.
SOURCES = {"Ceramics": "Ceramics - Wholesale", "Home": "Home - Wholesale Price", "Fashion": "Fashion - Wholesale - Local"}
TARGET = "Ardmore - Wholesale"

existing = {}
for r in frappe.get_all("Item Price", filters={"price_list": TARGET}, fields=["name", "item_code", "price_list_rate"], limit_page_length=100000):
    existing[r.item_code] = r

created = 0
updated = 0
for ent in SOURCES:
    src = SOURCES[ent]
    rows = frappe.get_all("Item Price", filters={"price_list": src, "selling": 1}, fields=["item_code", "price_list_rate"], limit_page_length=100000)
    for r in rows:
        rate = float(r.price_list_rate or 0)
        if rate <= 0:
            continue
        cat = frappe.db.get_value("Item", r.item_code, "custom_category")
        if cat and cat != ent:
            continue  # another entity's item on this list - its own list wins
        ex = existing.get(r.item_code)
        if ex:
            if not cat:
                continue  # no Category: the first list that set it keeps it
            if abs(float(ex.price_list_rate or 0) - rate) > 0.005:
                frappe.db.set_value("Item Price", ex.name, "price_list_rate", rate)
                ex.price_list_rate = rate
                updated = updated + 1
        else:
            p = frappe.new_doc("Item Price")
            p.item_code = r.item_code
            p.price_list = TARGET
            p.price_list_rate = rate
            p.selling = 1
            p.currency = "ZAR"
            p.insert(ignore_permissions=True)
            existing[r.item_code] = p
            created = created + 1
        if (created + updated) % 200 == 0 and (created + updated) > 0:
            frappe.db.commit()
frappe.db.commit()
if created or updated:
    frappe.log_error(message="Ardmore - Wholesale: " + str(created) + " prices added, " + str(updated) + " changed, from the three entity wholesale lists.", title="Wholesale price list built")
