payload = {}

# INTERCOMPANY STOCK MOVES -> SAGE (Russell + Jon, 22 Oct 2026).
#
# ERPNext holds all stock in one company; in Sage each entity (Home, Ceramics, Fashion) owns
# its own. A warehouse with "Sage entity" set belongs to that entity (a store, a holding
# warehouse); Main Distribution has none, so there each item belongs to the entity in its
# Category. When a submitted Material Transfer moves a line from one entity's stock into
# another's, the selling entity invoices the buying entity and the buying entity records the
# purchase - the intercompany invoices Ardmore used to raise by hand:
#   1) tax invoice in the FROM entity's Sage company, customer = the TO entity
#      (Sage Intercompany Account.customer_id)
#   2) supplier invoice in the TO entity's Sage company, supplier = the FROM entity
#      (Sage Intercompany Account.supplier_id)
# One pair of documents per (from -> to) pair on the entry; the transfer price comes from the
# pair's row (Cost = valuation on the entry, or a price list). Lines that stay inside one
# entity post nothing. This is what lets a till sale post wholly to the store's entity
# (see post-taxinvoice-to-sage): by the time it sells, the store's entity owns the stock.
#
# soft_fail: the stock has moved; Sage being down must not undo that. Failures are written
# on the Stock Entry (status / documents / error) and shown once. A rerun (same script on
# the same entry) carries on from what already posted - the tax invoice number is recorded
# before the supplier invoice is attempted, so nothing is sold twice.

# ---------------------------------------------------------------------------
# TEST-ONLY LOCK (same lock as the posting scripts): while set, BOTH documents go to the
# Sage TESTING company, using the customer/supplier ids on the Sage Intercompany Account
# row named "<TEST>-<TEST>"; the real pair's row still decides the price basis.
# GO-LIVE: set SAGE_FORCE_COMPANY = "" here as well as in the two posting scripts.
# ---------------------------------------------------------------------------
SAGE_FORCE_COMPANY = ""
FORCE_TAX_TYPE_ID = 0
if SAGE_FORCE_COMPANY:
    FORCE_TAX_TYPE_ID = int(frappe.db.get_value("Company Sage Integration", SAGE_FORCE_COMPANY, "tax_id") or 0)
TRAINING_COMPANIES = ["Ardmore Ceramics TEST"]
VAT_RATE = 15.0


def owner_of(warehouse, item_code):
    e = frappe.db.get_value("Warehouse", warehouse, "custom_sage_entity")
    if not e:
        e = frappe.db.get_value("Item", item_code, "custom_category")
    return e or ""


def sage_post(url, body, apikey):
    try:
        resp = frappe.make_post_request(url, json=body, headers={"Content-Type": "application/json"})
    except Exception as http_err:
        text = ""
        try:
            text = str(http_err.response.text)[:400]
        except Exception:
            text = ""
        # the URL carries the API key - keep it out of the document and the log
        raise Exception("Sage HTTP error: " + str(http_err)[:300].replace(str(apikey), "***") + " " + text)
    if resp and resp.get("success"):
        return resp
    raise Exception("Sage API error: " + str((resp or {}).get("errorMessage") or resp or "no response"))


if doc.company in TRAINING_COMPANIES:
    pass  # training company never talks to Sage
elif doc.purpose != "Material Transfer":
    pass  # receipts, issues, manufacture: not a move between entities
elif doc.get("custom_stock_already_owned"):
    # opening stock count loads at go-live, and any move of stock the receiving entity has
    # already bought in Sage (Jon, 26 Oct 2026): the location changes, the owner does not,
    # so there is nothing to post. The box is ticked on the Stock Entry before submit.
    doc.db_set("custom_sage_intercompany_status", "Not needed (already owned)")
elif doc.get("custom_sage_intercompany_status") == "Synced":
    pass  # already done
else:
    try:
        # which lines cross from one entity's stock into another's
        pairs = {}
        for row in doc.items:
            if not row.s_warehouse or not row.t_warehouse:
                continue
            frm = owner_of(row.s_warehouse, row.item_code)
            to = owner_of(row.t_warehouse, row.item_code)
            if not frm or not to:
                where = row.t_warehouse if frm else row.s_warehouse
                raise Exception("Cannot tell which Sage entity owns " + str(row.item_code) + " in " + str(where) + ": set Sage entity on the warehouse or Category on the item.")
            if frm == to:
                continue
            key = frm + " -> " + to
            if key not in pairs:
                pairs[key] = {"from": frm, "to": to, "rows": []}
            pairs[key]["rows"].append(row)

        if not pairs:
            doc.db_set("custom_sage_intercompany_status", "Not needed")
        else:
            prior = str(doc.get("custom_sage_intercompany_docs") or "")
            for key in pairs.keys():
                p = pairs[key]
                # what an earlier attempt already posted for this pair
                existing = ""
                for ln in prior.split("\n"):
                    if ln.startswith(key + ": "):
                        existing = ln
                if existing and "(purchase pending)" not in existing:
                    continue  # both documents already in Sage
                inv_no = ""
                if existing:
                    inv_no = existing[len(key) + 2:].split(" /")[0].strip()

                cfg_name = p["from"] + "-" + p["to"]
                if not frappe.db.exists("Sage Intercompany Account", cfg_name):
                    raise Exception("No Sage Intercompany Account row " + cfg_name + ". Add it: " + p["to"] + " as a customer in " + p["from"] + "'s Sage, and " + p["from"] + " as a supplier in " + p["to"] + "'s Sage.")
                cfg = frappe.get_doc("Sage Intercompany Account", cfg_name)
                ids = cfg
                from_company = p["from"]
                to_company = p["to"]
                if SAGE_FORCE_COMPANY:
                    from_company = SAGE_FORCE_COMPANY
                    to_company = SAGE_FORCE_COMPANY
                    ids_name = SAGE_FORCE_COMPANY + "-" + SAGE_FORCE_COMPANY
                    if not frappe.db.exists("Sage Intercompany Account", ids_name):
                        raise Exception("Locked to " + SAGE_FORCE_COMPANY + " but no Sage Intercompany Account row " + ids_name + " holds its test customer and supplier ids.")
                    ids = frappe.get_doc("Sage Intercompany Account", ids_name)
                try:
                    customer_id = int(str(ids.customer_id).strip())
                    supplier_id = int(str(ids.supplier_id).strip())
                except Exception:
                    raise Exception("Customer and supplier ids on " + ids.name + " must be numeric.")
                if customer_id <= 0 or supplier_id <= 0:
                    raise Exception("Sage Intercompany Account " + ids.name + " is not set up yet (customer or supplier id is 0). Ken to supply the accounts.")

                sage_from = frappe.get_doc("Company Sage Integration", from_company)
                sage_to = frappe.get_doc("Company Sage Integration", to_company)
                for s in [sage_from, sage_to]:
                    # lock 2: never talk to any Sage company other than the forced one
                    if SAGE_FORCE_COMPANY and (s.name != SAGE_FORCE_COMPANY or s.company != SAGE_FORCE_COMPANY):
                        raise Exception("Blocked: Sage posting is locked to " + SAGE_FORCE_COMPANY + " but resolved " + s.name + ".")
                    if not s.get_password("api_key") or not s.username or not s.get_password("password"):
                        raise Exception("Sage credentials missing for " + s.name + ".")
                tax_from = FORCE_TAX_TYPE_ID or int(sage_from.get("tax_id") or 0)
                tax_to = FORCE_TAX_TYPE_ID or int(sage_to.get("tax_id") or 0)

                inv_lines = []
                pi_lines = []
                for row in p["rows"]:
                    qty = abs(float(row.transfer_qty or row.qty or 0))
                    if qty <= 0:
                        continue
                    cost = float(row.basic_rate or row.valuation_rate or 0)
                    if cost <= 0:
                        cost = float(frappe.db.get_value("Item", row.item_code, "valuation_rate") or 0)
                    price = 0
                    if cfg.price_basis == "Price List":
                        price = float(frappe.db.get_value("Item Price", {"item_code": row.item_code, "price_list": cfg.price_list}, "price_list_rate") or 0)
                        # TICKET 0138 (Cheri + Russell, 3 Nov 2026): Sage's own figure on the pair's list IS the
                        # VAT-inclusive transfer price, so the two invoices must total it (less the pair's
                        # discount). Sage drives the price lists and ERPNext's copy carries the price sync's
                        # +15% - undo that first, then back the VAT out once: Sage wants the exclusive.
                        # Before this the VAT landed on top of an inclusive price (1105 posted as 1270.75).
                        price = price / (1 + VAT_RATE / 100)
                        price = price / (1 + VAT_RATE / 100)
                        # the pair's discount off the list (Jon, 26 Oct 2026: 15% on Ceramics and Home, 0% on Fashion)
                        price = round(price * (1 - float(cfg.get("discount_percent") or 0) / 100), 2)
                    if price <= 0:
                        # No price on the pair's list (Russell, 3 Nov 2026): the stock still moves - the transfer
                        # only warns (block-transfer-without-wholesale-price) - and Sage is invoiced at the
                        # sending entity's cost, the rate the stock left its warehouse at. The price is caught
                        # later, when the item is sold. A "Cost" pair always lands here.
                        price = cost
                        if price <= 0:
                            raise Exception(str(row.item_code) + " has no cost (valuation rate) to transfer at.")
                    sel_from = frappe.db.get_value("Sage Item Selection", {"item_code": row.item_code, "company": from_company}, "selection_id")
                    sel_to = frappe.db.get_value("Sage Item Selection", {"item_code": row.item_code, "company": to_company}, "selection_id")
                    if not sel_from:
                        raise Exception("No Sage SelectionID for " + str(row.item_code) + " in " + from_company + ".")
                    if not sel_to:
                        raise Exception("No Sage SelectionID for " + str(row.item_code) + " in " + to_company + ". The item must exist in the buying entity's Sage company.")
                    excl = round(price * qty, 2)
                    tax = round(excl * VAT_RATE / 100, 2)
                    base = {
                        "id": 0,
                        "lineType": 0,
                        "description": row.description or row.item_name or row.item_code,
                        "unit": row.stock_uom or row.uom or "",
                        "comments": "Intercompany " + key + " on " + doc.name,
                        "quantity": qty,
                        "unitPriceExclusive": round(price, 2),
                        "unitPriceInclusive": round(price * (1 + VAT_RATE / 100), 2),
                        "unitCost": round(cost, 2),
                        "exclusive": excl,
                        "discount": 0,
                        "discountPercentage": 0,
                        "tax": tax,
                        "total": round(excl + tax, 2),
                        "taxPercentage": round(VAT_RATE / 100, 4)
                    }
                    l1 = dict(base)
                    l1["selectionId"] = int(float(str(sel_from).strip()))
                    l1["taxTypeId"] = tax_from
                    l2 = dict(base)
                    l2["selectionId"] = int(float(str(sel_to).strip()))
                    l2["taxTypeId"] = tax_to
                    l2["currencyId"] = 0
                    l2["analysisCategoryId1"] = 0
                    l2["analysisCategoryId2"] = 0
                    l2["analysisCategoryId3"] = 0
                    inv_lines.append(l1)
                    pi_lines.append(l2)
                if not inv_lines:
                    continue

                total_excl = round(sum(l.get("exclusive", 0) for l in inv_lines), 2)
                total_tax = round(sum(l.get("tax", 0) for l in inv_lines), 2)
                total_all = round(sum(l.get("total", 0) for l in inv_lines), 2)
                date_s = frappe.utils.formatdate(doc.posting_date, "yyyy-MM-dd")
                due_s = frappe.utils.formatdate(frappe.utils.add_days(doc.posting_date, int(cfg.credit_days or 0)), "yyyy-MM-dd")
                note = "Intercompany stock transfer " + key + " (" + doc.name + ")"

                # 1) the sale: tax invoice in the FROM entity, customer = the TO entity
                if not inv_no:
                    apikey = sage_from.get_password("api_key")
                    invoice = {
                        "date": date_s,
                        "inclusive": False,
                        "discountPercentage": 0,
                        "taxReference": "",
                        "customerName": ids.customer_name or p["to"],
                        "customerId": customer_id,
                        "dueDate": due_s,
                        "reference": doc.name,
                        "message": note,
                        "discount": 0,
                        "exclusive": total_excl,
                        "tax": total_tax,
                        "rounding": 0,
                        "total": total_all,
                        "amountDue": total_all,
                        "lines": inv_lines
                    }
                    if int(cfg.sales_rep_id or 0):
                        invoice["salesRepresentative"] = {"id": int(cfg.sales_rep_id)}
                    payload = {
                        "credentials": {"loginName": sage_from.username, "loginPwd": sage_from.get_password("password"), "useOAuth": False, "sessionToken": None, "provider": None},
                        "invoice": invoice
                    }
                    r1 = sage_post("https://pharoh.co.za/api/TaxInvoice/post-taxinvoice-to-sage?apikey=" + apikey, payload, apikey)
                    inv_no = str(r1.get("documentNumber") or r1.get("sageOrderId") or "")
                    # recorded at once, so a rerun never sells the same stock twice
                    prior = (prior + "\n" if prior else "") + key + ": " + inv_no + " / (purchase pending)"
                    doc.db_set("custom_sage_intercompany_docs", prior)

                # 2) the purchase: supplier invoice in the TO entity, supplier = the FROM entity
                apikey2 = sage_to.get_password("api_key")
                purchase = {
                    "id": 0,
                    "documentNumber": "",
                    "date": date_s + "T00:00:00",
                    "dueDate": due_s + "T00:00:00",
                    "status": "",
                    "supplier": {"id": supplier_id, "name": ids.supplier_name or p["from"]},
                    "total": total_all,
                    "tax": total_tax,
                    "discount": 0,
                    "reference": inv_no or doc.name,
                    "message": note,
                    "lines": pi_lines,
                    "inclusive": False,
                    "discountPercentage": 0,
                    "taxReference": "",
                    "exclusive": total_excl,
                    "rounding": 0,
                    "amountDue": total_all,
                    "externalReference": doc.name,
                    "supplier_CurrencyId": 0,
                    "supplier_ExchangeRate": 0,
                    "useForeignCurrency": False,
                    "fromDocument": "",
                    "fromDocumentId": 0,
                    "fromDocumentTypeId": 0,
                    "paid": False,
                    "locked": False,
                    "hasAdditionalCost": False
                }
                payload = {
                    "credentials": {"loginName": sage_to.username, "loginPwd": sage_to.get_password("password"), "useOAuth": False, "sessionToken": None, "provider": None},
                    "invoice": purchase
                }
                r2 = sage_post("https://pharoh.co.za/api/SupplierInvoice/post-supplierinvoice-to-sage?apikey=" + apikey2, payload, apikey2)
                pi_no = str(r2.get("documentNumber") or r2.get("sageOrderId") or "")
                prior = prior.replace(key + ": " + inv_no + " / (purchase pending)", key + ": " + inv_no + " / " + pi_no)
                doc.db_set("custom_sage_intercompany_docs", prior)

            doc.db_set("custom_sage_intercompany_status", "Synced")
            doc.db_set("custom_sage_intercompany_error", "")

    except Exception as e:
        err = str(e)
        low = err.lower()
        uncertain = ("timed out" in low) or ("timeout" in low) or ("connection aborted" in low) or ("remote end closed" in low)
        # never write the Sage login into the Error Log
        frappe.log_error(
            message="Stock Entry: " + doc.name + "\nError: " + err + "\nSent: " + str(payload.get("invoice") or "")[:1500],
            title="Sage Intercompany Sync Error")
        try:
            doc.db_set("custom_sage_intercompany_status", "Check Sage" if uncertain else "Failed")
            doc.db_set("custom_sage_intercompany_error", err[:900])
        except Exception:
            pass
        frappe.msgprint("Sage intercompany posting did not go through: " + err[:300] + " The transfer stands; the reason is on the Stock Entry.", title="Sage", indicator="red")
