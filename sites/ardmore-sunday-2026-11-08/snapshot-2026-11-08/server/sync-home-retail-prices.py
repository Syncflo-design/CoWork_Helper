# Daily refresh of "Home - Retail Price" from Sage Home's standard selling price (2 Nov 2026).
# Sage keeps its DEFAULT price list (Home "Retail Price", id 130577) on the item itself, so
# get-additional-prices-for-erpnext returns nothing for it. This pages Pharoh's inventory feed
# for the Home company and writes each item's incl-VAT selling price into that list.
# Hyde Park sells from this list. Run on demand: Scheduled Job Type -> Execute.
PRICE_LIST = "Home - Retail Price"
COMPANY = "Home"
MAX_PAGES = 200            # 100 items a page; Home has ~7,000 items


def sage_number(val):
    # Sage sends decimals with a comma ("208,696" = 208.696); flt() would read it as thousands.
    if val is None:
        return 0.0
    s = str(val).strip().replace(' ', '').replace(u'\xa0', '')
    if not s:
        return 0.0
    if (',' in s) and ('.' in s):
        if s.rfind(',') > s.rfind('.'):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif ',' in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except Exception:
        return 0.0


sage = frappe.get_doc("Company Sage Integration", COMPANY)
apikey = sage.get_password("api_key")
payload = {"loginName": sage.username, "loginPwd": sage.get_password("password"),
           "useOAuth": False, "sessionToken": None, "provider": None}

skip = 0
pages = 0
created = 0
updated = 0
errors = []

while pages < MAX_PAGES:
    url = ("https://pharoh.co.za/api/InventorySync/get-inventory-for-erpnext?apikey=" + apikey +
           "&lastDate=1970-01-01&InclZeroOnHand=true&skipQty=" + str(skip))
    try:
        r = frappe.make_post_request(url, json=payload) or {}
    except Exception as e:
        errors.append("Fetch @" + str(skip) + ": " + str(e))
        break
    pages = pages + 1
    items = r.get("items") or []
    total = r.get("totalResults", 0) or 0
    returned = r.get("returnedResults", 0) or len(items)
    if not items:
        break

    for d in items:
        code = d.get("item_code")
        if not code or d.get("disabled", 0) or not frappe.db.exists("Item", code):
            continue
        rate = sage_number(d.get("standard_rate_incl"))
        if rate <= 0:
            continue
        try:
            rows = frappe.get_all("Item Price",
                filters={"item_code": code, "price_list": PRICE_LIST, "selling": 1},
                fields=["name", "price_list_rate"])
            if rows:
                # Every row is set, so a duplicate row can never ring a stale price.
                for row in rows:
                    if float(row.price_list_rate or 0) != rate:
                        frappe.db.set_value("Item Price", row.name, "price_list_rate", rate)
                        updated = updated + 1
            else:
                ip = frappe.new_doc("Item Price")
                ip.item_code = code
                ip.price_list = PRICE_LIST
                ip.price_list_rate = rate
                ip.selling = 1
                ip.currency = "ZAR"
                ip.insert(ignore_permissions=True)
                created = created + 1
        except Exception as e:
            errors.append(str(code) + ": " + str(e))

    frappe.db.commit()
    skip = skip + returned
    if total and skip >= total:
        break

if errors:
    frappe.log_error(message=("Created " + str(created) + ", updated " + str(updated) + ", stopped at " +
                              str(skip) + "\n" + "\n".join(errors[0:50])),
                     title="Home retail price sync errors")
