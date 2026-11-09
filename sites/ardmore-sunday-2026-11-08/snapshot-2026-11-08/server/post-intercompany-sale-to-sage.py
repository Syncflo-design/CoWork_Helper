payload = {}

# INTERCOMPANY ON A SALE (Russell + Jon, 27 Oct 2026) - "point 2".
#
# Rule: whoever sells it to the customer must own it first. Point 1 (post-intercompany-
# transfer-to-sage) handles stock that moved INTO a store owned by another entity. This
# script handles stock sold STRAIGHT OUT of a warehouse where another entity still owns
# it - the Online till selling a Ceramics bowl from Main Distribution, or an Account Sale
# for a Home stockist that picks a Fashion scarf. For every such line the owning entity
# invoices the selling entity and the selling entity records the purchase, exactly as
# point 1 does, so the entity that posted the sale (post-taxinvoice-to-sage) owned the
# stock a moment earlier.
#
# Who sold it = the same routing as the sale: the till's Sage entity (POS Profile, else
# its warehouse), or for an Account Sale the Sage company where the customer has an
# account. Who owned it = the line warehouse's Sage entity, else the item's Category.
# Same entity -> nothing. Stock moved into a store earlier already belongs to the store's
# entity (the warehouse carries it), so a till sale in a store never fires this.
#
# soft_fail always: the sale is through and the customer has paid; a Sage problem here is
# written on the invoice (status / documents / error) and shown once, never thrown. The
# tax invoice number is recorded before the purchase is attempted, so a rerun only
# finishes the pair.

# ---------------------------------------------------------------------------
# TEST-ONLY LOCK (same lock as the other scripts): while set, BOTH documents go to the
# Sage TESTING company using the ids on the Sage Intercompany Account row named
# "<TEST>-<TEST>". The REAL routing still decides whether a line is intercompany at all,
# so Online selling a Ceramics bowl fires here under the lock too (to TEST).
# GO-LIVE: set SAGE_FORCE_COMPANY = "" here as well.
# ---------------------------------------------------------------------------
SAGE_FORCE_COMPANY = ""
FORCE_TAX_TYPE_ID = 0
if SAGE_FORCE_COMPANY:
    FORCE_TAX_TYPE_ID = int(frappe.db.get_value("Company Sage Integration", SAGE_FORCE_COMPANY, "tax_id") or 0)
TRAINING_COMPANIES = ["Ardmore Ceramics TEST"]
VAT_RATE = 15.0


def owner_of(warehouse, item_code):
    e = frappe.db.get_value("Warehouse", warehouse, "custom_sage_entity") if warehouse else None
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
        raise Exception("Sage HTTP error: " + str(http_err)[:300].replace(str(apikey), "***") + " " + text)
    if resp and resp.get("success"):
        return resp
    raise Exception("Sage API error: " + str((resp or {}).get("errorMessage") or resp or "no response"))


if doc.company in TRAINING_COMPANIES:
    pass  # training company never talks to Sage
elif doc.get("is_return"):
    pass  # returns: stock comes back to the seller; the reverse pair is a later job
elif doc.get("is_pos") and doc.get("is_consolidated"):
    pass  # legacy day-end consolidation
elif doc.get("custom_sage_intercompany_status") == "Synced":
    pass
else:
    try:
        # who sold it: the same routing as post-taxinvoice-to-sage (the REAL entity, lock or not)
        seller = None
        pos_profile_name = str(doc.get("pos_profile") or "")
        till_warehouse = str(doc.get("set_warehouse") or "")
        if doc.get("is_pos"):
            if pos_profile_name:
                seller = frappe.db.get_value("POS Profile", pos_profile_name, "custom_sage_entity")
            if not seller and till_warehouse:
                seller = frappe.db.get_value("Warehouse", till_warehouse, "custom_sage_entity")
        else:
            mapped = frappe.get_all("Sage Customer Selection", filters={"customer": doc.customer}, pluck="company")
            if len(mapped) == 1:
                seller = mapped[0]
            elif len(mapped) > 1:
                cats = []
                for item in doc.items:
                    c = frappe.db.get_value("Item", item.item_code, "custom_category")
                    if c and c not in cats:
                        cats.append(c)
                seller = cats[0] if (len(cats) == 1 and cats[0] in mapped) else sorted(mapped)[0]
        if not seller:
            raise Exception("Cannot tell which Sage entity sold this (no Sage entity on the till or warehouse, or no Sage customer account).")

        # which lines belonged to someone else at the moment of sale
        pairs = {}
        for row in doc.items:
            owner = owner_of(row.warehouse, row.item_code)
            if not owner:
                raise Exception("Cannot tell which Sage entity owns " + str(row.item_code) + ": set Category on the item or Sage entity on " + str(row.warehouse) + ".")
            if owner == seller:
                continue
            key = owner + " -> " + seller
            if key not in pairs:
                pairs[key] = {"from": owner, "to": seller, "rows": []}
            pairs[key]["rows"].append(row)

        if not pairs:
            doc.db_set("custom_sage_intercompany_status", "Not needed")
        else:
            prior = str(doc.get("custom_sage_intercompany_docs") or "")
            for key in pairs.keys():
                p = pairs[key]
                existing = ""
                for ln in prior.split("\n"):
                    if ln.startswith(key + ": "):
                        existing = ln
                if existing and "(purchase pending)" not in existing:
                    continue
                inv_no = ""
                if existing:
                    inv_no = existing[len(key) + 2:].split(" /")[0].strip()

                cfg_name = p["from"] + "-" + p["to"]
                if not frappe.db.exists("Sage Intercompany Account", cfg_name):
                    raise Exception("No Sage Intercompany Account row " + cfg_name + ".")
                cfg = frappe.get_doc("Sage Intercompany Account", cfg_name)
                ids = cfg
                from_company = p["from"]
                to_company = p["to"]
                if SAGE_FORCE_COMPANY:
                    from_company = SAGE_FORCE_COMPANY
                    to_company = SAGE_FORCE_COMPANY
                    ids_name = SAGE_FORCE_COMPANY + "-" + SAGE_FORCE_COMPANY
                    if not frappe.db.exists("Sage Intercompany Account", ids_name):
                        raise Exception("Locked to " + SAGE_FORCE_COMPANY + " but no Sage Intercompany Account row " + ids_name + ".")
                    ids = frappe.get_doc("Sage Intercompany Account", ids_name)
                try:
                    customer_id = int(str(ids.customer_id).strip())
                    supplier_id = int(str(ids.supplier_id).strip())
                except Exception:
                    raise Exception("Customer and supplier ids on " + ids.name + " must be numeric.")
                if customer_id <= 0 or supplier_id <= 0:
                    raise Exception("Sage Intercompany Account " + ids.name + " is not set up yet (customer or supplier id is 0).")

                sage_from = frappe.get_doc("Company Sage Integration", from_company)
                sage_to = frappe.get_doc("Company Sage Integration", to_company)
                for s in [sage_from, sage_to]:
                    if SAGE_FORCE_COMPANY and (s.name != SAGE_FORCE_COMPANY or s.company != SAGE_FORCE_COMPANY):
                        raise Exception("Blocked: Sage posting is locked to " + SAGE_FORCE_COMPANY + " but resolved " + s.name + ".")
                    if not s.get_password("api_key") or not s.username or not s.get_password("password"):
                        raise Exception("Sage credentials missing for " + s.name + ".")
                tax_from = FORCE_TAX_TYPE_ID or int(sage_from.get("tax_id") or 0)
                tax_to = FORCE_TAX_TYPE_ID or int(sage_to.get("tax_id") or 0)

                inv_lines = []
                pi_lines = []
                for row in p["rows"]:
                    qty = abs(float(row.stock_qty or row.qty or 0))
                    if qty <= 0:
                        continue
                    cost = float(row.incoming_rate or 0)
                    if cost <= 0:
                        cost = float(frappe.db.get_value("Item", row.item_code, "valuation_rate") or 0)
                    if cfg.price_basis == "Price List":
                        price = float(frappe.db.get_value("Item Price", {"item_code": row.item_code, "price_list": cfg.price_list}, "price_list_rate") or 0)
                        if price <= 0:
                            raise Exception(str(row.item_code) + " has no price on " + str(cfg.price_list) + ".")
                        # ERPNext's price lists are VAT-inclusive; Sage wants the exclusive
                        price = price / (1 + VAT_RATE / 100)
                        price = round(price * (1 - float(cfg.get("discount_percent") or 0) / 100), 2)
                    else:
                        price = cost
                        if price <= 0:
                            raise Exception(str(row.item_code) + " has no cost (valuation rate) to transfer at.")
                    sel_from = frappe.db.get_value("Sage Item Selection", {"item_code": row.item_code, "company": from_company}, "selection_id")
                    sel_to = frappe.db.get_value("Sage Item Selection", {"item_code": row.item_code, "company": to_company}, "selection_id")
                    if not sel_from:
                        raise Exception("No Sage SelectionID for " + str(row.item_code) + " in " + from_company + ".")
                    if not sel_to:
                        raise Exception("No Sage SelectionID for " + str(row.item_code) + " in " + to_company + ". The item must exist in the selling entity's Sage company.")
                    excl = round(price * qty, 2)
                    tax = round(excl * VAT_RATE / 100, 2)
                    base = {
                        "id": 0,
                        "lineType": 0,
                        "description": row.description or row.item_name or row.item_code,
                        "unit": row.stock_uom or row.uom or "",
                        "comments": "Intercompany " + key + " for sale " + doc.name,
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
                note = "Intercompany " + key + " for sale " + doc.name

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
                    prior = (prior + "\n" if prior else "") + key + ": " + inv_no + " / (purchase pending)"
                    doc.db_set("custom_sage_intercompany_docs", prior)

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
        frappe.log_error(
            message="Sales Invoice: " + doc.name + "\nError: " + err + "\nSent: " + str(payload.get("invoice") or "")[:1500],
            title="Sage Intercompany Sync Error")
        try:
            doc.db_set("custom_sage_intercompany_status", "Check Sage" if uncertain else "Failed")
            doc.db_set("custom_sage_intercompany_error", err[:900])
        except Exception:
            pass
        if not doc.get("is_pos"):
            frappe.msgprint("Sage intercompany posting did not go through: " + err[:300] + " The sale stands; the reason is on the invoice.", title="Sage", indicator="red")
