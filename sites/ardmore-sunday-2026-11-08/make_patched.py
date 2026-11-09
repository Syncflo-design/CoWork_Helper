"""Offline only. Applies the anchored changes to copies of the Live scripts, one anchor must match exactly once,
and writes the results to patched/ so they can be syntax-checked and reviewed. Nothing here talks to the site.
Usage: python make_patched.py <folder holding the Live copies, with server/ and client/ inside>"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = sys.argv[1]
OUT = os.path.join(HERE, "patched")
os.makedirs(OUT, exist_ok=True)

# ---- Sales Other ------------------------------------------------------------------------------------------------
ITEM_OLD = '''            item_doc = frappe.get_doc("Item", item.item_code)
            if not SAGE_FORCE_COMPANY and not item_doc.get("custom_category"):
                raise Exception(f"Set ERPNext Category on {item.item_code} before syncing.")
            company = SAGE_FORCE_COMPANY or route_company

            selection_raw = frappe.db.get_value(
                "Sage Item Selection",
                {"item_code": item.item_code, "company": company},
                "selection_id")
            if not selection_raw:
                raise Exception(f"No Sage SelectionID for {item.item_code} in {company}. Sync this item for {company} first.")
'''
ITEM_NEW = '''            # SALES OTHER (Russell, 6 Nov 2026, ticket 0129): a till line with no item code is typed by the
            # cashier (till script "POS Sales Other"). It goes to Sage as an ACCOUNT line (lineType 1) on the
            # one account chosen for this company on Company Sage Integration, in the cashier's words.
            is_other = doc.get("is_pos") and not item.item_code
            item_doc = {} if is_other else frappe.get_doc("Item", item.item_code)
            if not SAGE_FORCE_COMPANY and not is_other and not item_doc.get("custom_category"):
                raise Exception(f"Set ERPNext Category on {item.item_code} before syncing.")
            company = SAGE_FORCE_COMPANY or route_company

            if is_other:
                selection_raw = frappe.db.get_value("Company Sage Integration", company, "custom_sage_sales_other_account_id")
                if not selection_raw:
                    raise Exception(f"No Sales Other account is chosen for {company}. Choose it on Company Sage Integration.")
            else:
                selection_raw = frappe.db.get_value(
                    "Sage Item Selection",
                    {"item_code": item.item_code, "company": company},
                    "selection_id")
                if not selection_raw:
                    raise Exception(f"No Sage SelectionID for {item.item_code} in {company}. Sync this item for {company} first.")
'''
LINE_OLD = '''                "lineType": 0,
                "description": item.description or item.item_name or "",
                "unit": item.uom or "",
'''
LINE_NEW = '''                "lineType": 1 if is_other else 0,
                # the till's cart shortens a line's description, so the cashier's full words come from item_name
                "description": (item.item_name if is_other else (item.description or item.item_name)) or "",
                "unit": "" if is_other else (item.uom or ""),
'''

# ---- Importers: Item Category, wholesale always per the workbook ------------------------------------------------
RETAIL_CHECK = '''        else:
            # Sage owns the retail price of an existing item; the tills read Sage Home's.
            till_rate = frappe.db.get_value('Item Price', {'item_code': code, 'price_list': 'Home - Retail Price'}, 'price_list_rate')
            if retail_incl and till_rate and round(float(till_rate), 2) != round(retail_incl, 2):
                issues.append({'row': row_num, 'code': code, 'reason': 'Retail price NOT changed - this item already exists, and Sage owns its retail price. Change it in Sage; it reaches the tills within minutes'})
            # Wholesale always follows the workbook, here and in Sage (Russell, 6 Nov 2026).
            if whole_incl:
                if round(float(item.get('custom_wholesale_price_incl_vat') or 0), 2) != round(whole_incl, 2):
                    sage_update = 1
                item.custom_wholesale_price_incl_vat = whole_incl
                item.custom_wholesesale_price_ex_vat = whole_excl
'''
PRICE_OLD = "        elif (retail_incl and round(float(item.get('custom_retail_price_incl_vat') or 0), 2) != round(retail_incl, 2)) or (whole_incl and round(float(item.get('custom_wholesale_price_incl_vat') or 0), 2) != round(whole_incl, 2)):\n            issues.append({'row': row_num, 'code': code, 'reason': 'Price NOT changed - this item already exists, and Sage owns its price. Change the price in Sage; it reaches the tills within minutes'})\n"
UPSERT_OLD = "        if is_new:\n            upsert_price(code, retail_list, retail_incl)\n            upsert_price(code, whole_list, whole_incl)\n"
QUEUE_LINES = "        elif whole_incl:\n            upsert_price(code, whole_list, whole_incl)\n%s        # Existing item changed: queue it for Sage, unless it is still waiting to be created there.\n        if sage_update and (not is_new) and frappe.db.get_value('Item', code, 'custom_sage_post_status') != 'Create':\n            frappe.db.set_value('Item', code, 'custom_sage_post_status', 'Update', update_modified=False)\n"
# Home and Fashion: the hourly Ardmore - Wholesale build reads the entity's own list, so keep it in step.
HOME_LIST = "            ent_list = {'Home': 'Home - Wholesale Price', 'Fashion': 'Fashion - Wholesale - Local'}.get(doc.category)\n            ent_row = frappe.db.get_value('Item Price', {'item_code': code, 'price_list': ent_list}, 'name')\n            if ent_row:\n                frappe.db.set_value('Item Price', ent_row, 'price_list_rate', whole_incl)\n"
MSG_OLD = "if issues:\n    msg = msg + '<br><br><b>' + str(len(issues)) + ' row(s) had a problem.</b> Use <b>Download Issues</b> for the list.'\n"
MSG_NEW = "if created:\n    msg = msg + '<br><br>The new items go to Sage automatically, 25 at a time. A big sheet takes a while; there is nothing more to do.'\n" + MSG_OLD

PATCHES = {
    ("server", "post-taxinvoice-to-sage"): [
        (ITEM_OLD, ITEM_NEW), (LINE_OLD, LINE_NEW),
        ('"unitCost": float(item.valuation_rate or item.net_rate or item.rate or 0),', '"unitCost": 0 if is_other else float(item.valuation_rate or item.net_rate or item.rate or 0),'),
    ],
    ("server", "post-customerreturn-to-sage"): [
        (ITEM_OLD, ITEM_NEW), (LINE_OLD, LINE_NEW),
        ('"unitCost": abs(float(item.valuation_rate or item.net_rate or item.rate or 0)),', '"unitCost": 0 if is_other else abs(float(item.valuation_rate or item.net_rate or item.rate or 0)),'),
    ],
    ("server", "post-intercompany-sale-to-sage"): [
        ("        for row in doc.items:\n            owner = owner_of(row.warehouse, row.item_code)\n",
         "        for row in doc.items:\n            # a Sales Other line is not stock, so nobody else owned it (ticket 0129)\n            if doc.get(\"is_pos\") and not row.item_code:\n                continue\n            owner = owner_of(row.warehouse, row.item_code)\n"),
    ],
    ("client", "POS Cart Quantity"): [
        ("if (!row) continue;", "if (!row || !row.item_code) continue; // a Sales Other line has no quantity box (ticket 0129)"),
    ],
    ("client", "POS Return Item Picker"): [
        ("\t\t\t\t\tfinish(out);\n",
         "\t\t\t\t\t// A Sales Other line goes back on its own credit note (ticket 0129): ERPNext cannot return it with stock.\n\t\t\t\t\tconst ticked = items.filter((r) => out[r.name]);\n\t\t\t\t\tif (ticked.some((r) => !r.item_code) && ticked.some((r) => r.item_code)) {\n\t\t\t\t\t\tfrappe.msgprint(__('Return the Sales Other line on its own: tick only that line now, then do a second return for the stock items.'));\n\t\t\t\t\t\treturn;\n\t\t\t\t\t}\n\t\t\t\t\tfinish(out);\n"),
    ],
    ("server", "Kiln Sheet Importer - Import"): [
        ("        raw_size = cell(row, C_SIZE)\n",
         "        # ITEM CATEGORY (Russell, 6 Nov 2026): the workbook's Category column is Type and Item Category both.\n        sage_update = 0\n        if tval:\n            if not frappe.db.exists('Item Group', tval):\n                ig_doc = frappe.new_doc('Item Group')\n                ig_doc.item_group_name = tval\n                ig_doc.parent_item_group = 'All Item Groups'\n                ig_doc.is_group = 0\n                ig_doc.insert(ignore_permissions=True)\n            if (not is_new) and item.get('item_group') != tval:\n                sage_update = 1\n            item.item_group = tval\n\n        raw_size = cell(row, C_SIZE)\n"),
        (PRICE_OLD, RETAIL_CHECK),
        (UPSERT_OLD, UPSERT_OLD + QUEUE_LINES % ""),
        (MSG_OLD, MSG_NEW),
    ],
    ("server", "Home Fashion Importer - Import"): [
        ("        else:\n            item = frappe.get_doc('Item', code)\n\n        # Every value must be on its allowed list.",
         "        else:\n            item = frappe.get_doc('Item', code)\n\n        # ITEM CATEGORY (Russell, 6 Nov 2026): the sheet's item_group also applies to an item that already exists.\n        sage_update = 0\n        ig_sheet = str(hval(headers, row, 'item_group') or '').strip()\n        if ig_sheet and (not is_new) and item.get('item_group') != ig_sheet and frappe.db.exists('Item Group', ig_sheet):\n            item.item_group = ig_sheet\n            sage_update = 1\n\n        # Every value must be on its allowed list."),
        (PRICE_OLD, RETAIL_CHECK),
        (UPSERT_OLD, UPSERT_OLD + QUEUE_LINES % HOME_LIST),
        (MSG_OLD, MSG_NEW),
    ],
    # ---- Item sync: a blank Sage category no longer wipes Item Category; Sage Home's item price reaches both tills
    ("server", "get-inventory-for-erpnext"): [
        ("                    if own:\n                        item_doc.item_group = item_group\n",
         "                    # A blank category in Sage never wipes the one ERPNext holds (Russell, 6 Nov 2026).\n                    if own and (item_data.get(\"item_group\") or not item_doc.get(\"item_group\")):\n                        item_doc.item_group = item_group\n"),
        ("                    if sage_item_id:\n                        sel_name = item_code + \"-\" + integration.company\n",
         "                    # Sage Home's item price -> the list both tills read (Russell, 6 Nov 2026).\n                    if integration.company == \"Home\" and not is_inactive and sage_price_incl > 0:\n                        home_rows = frappe.get_all(\"Item Price\", filters={\"item_code\": item_code, \"price_list\": \"Home - Retail Price\", \"selling\": 1}, fields=[\"name\", \"price_list_rate\"])\n                        for hr in home_rows:\n                            if float(hr.price_list_rate or 0) != sage_price_incl:\n                                frappe.db.set_value(\"Item Price\", hr.name, \"price_list_rate\", sage_price_incl)\n                        if not home_rows:\n                            hp = frappe.new_doc(\"Item Price\")\n                            hp.item_code = item_code\n                            hp.price_list = \"Home - Retail Price\"\n                            hp.price_list_rate = sage_price_incl\n                            hp.selling = 1\n                            hp.currency = \"ZAR\"\n                            hp.insert(ignore_permissions=True)\n\n                    if sage_item_id:\n                        sel_name = item_code + \"-\" + integration.company\n"),
    ],
    # ---- Till price: no Home item price -> Home's Wholesale list ----------------------------------------------------
    ("server", "sync-home-retail-prices"): [
        ("if errors:\n    frappe.log_error(message=(\"Created \"",
         "# No Sage Home item price: use Home's Wholesale list (Russell, 6 Nov 2026). The refresh above replaces it as\n# soon as Sage Home has a price.\nhave = {}\nfor c in frappe.get_all(\"Item Price\", filters={\"price_list\": PRICE_LIST, \"selling\": 1}, pluck=\"item_code\", limit_page_length=0):\n    have[c] = 1\nfor w in frappe.get_all(\"Item Price\", filters={\"price_list\": \"Home - Wholesale Price\", \"selling\": 1, \"price_list_rate\": [\">\", 0]}, fields=[\"item_code\", \"price_list_rate\"], limit_page_length=0):\n    if w.item_code not in have:\n        fb = frappe.new_doc(\"Item Price\")\n        fb.item_code = w.item_code\n        fb.price_list = PRICE_LIST\n        fb.price_list_rate = w.price_list_rate\n        fb.selling = 1\n        fb.currency = \"ZAR\"\n        fb.insert(ignore_permissions=True)\n        created = created + 1\nfrappe.db.commit()\n\nif errors:\n    frappe.log_error(message=(\"Created \""),
    ],
}


def safe(name):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)


bad = 0
for (kind, name), pairs in PATCHES.items():
    ext = ".py" if kind == "server" else ".js"
    text = open(os.path.join(SNAP, kind, safe(name) + ext), encoding="utf-8", newline="").read()
    for old, new in pairs:
        n = text.count(old)
        if n != 1:
            print("ANCHOR", name, "matched", n, "times:", old[:70].replace("\n", " "))
            bad += 1
            continue
        text = text.replace(old, new)
    path = os.path.join(OUT, safe(name) + ext)
    open(path, "w", encoding="utf-8", newline="").write(text)
    print("patched", name, len(pairs), "change(s)")

print("anchor problems:", bad)

# ---- Checks ------------------------------------------------------------------------------------------------------
files = [os.path.join(OUT, f) for f in os.listdir(OUT)]
for folder in ("server", "client"):
    files += [os.path.join(HERE, folder, f) for f in os.listdir(os.path.join(HERE, folder))]
fails = 0
for f in sorted(files):
    if f.endswith(".py"):
        src = open(f, encoding="utf-8").read()
        try:
            compile(src, f, "exec")
        except SyntaxError as e:
            print("SYNTAX", f, e)
            fails += 1
        # the sandbox refuses these at run time, so catch them here (only in lines this work adds is enough,
        # but the whole file is reported so anything new stands out against the Live copy)
        for pat, why in [(r"^\s*(import|from)\s+\w+", "import"), (r"\b_[a-zA-Z]\w*\s*=", "name starts with _"), (r"\.format\(", ".format"), (r"\+=", "+=")]:
            hits = re.findall(pat, src, re.M)
            if hits:
                print("SANDBOX?", os.path.basename(f), why, len(hits))
    elif f.endswith(".js"):
        r = subprocess.run(["node", "--check", f], capture_output=True, text=True)
        if r.returncode:
            print("SYNTAX", f, r.stderr[:300])
            fails += 1
print("syntax failures:", fails)
