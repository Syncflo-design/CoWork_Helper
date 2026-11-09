if doc.custom_from_import:
    try:
        # Go-live structure (Russell, 2026-10-13): the item master is created in EVERY
        # Sage company, but the opening quantity goes ONLY to the Sage company that
        # holds the stock, and that is decided by the item's category (Home, Ceramics
        # or Fashion), not by the company on the import screen (now always Ardmore,
        # which is not a Sage company).
        item_company = (doc.custom_category or "").strip() or None
        if not item_company:
            for d in (doc.item_defaults or []):
                if d.company:
                    item_company = d.company
                    break

        opening_qty = float(doc.custom_opening_qty or 0)

        sync_results = []
        # -------------------------------------------------------------------
        # TEST-ONLY LOCK (Russell, 2026-09-22): during UAT a new item is created
        # in the Sage TESTING company only. The three live Sage companies must
        # not receive test items. GO-LIVE: set SAGE_FORCE_COMPANY = "" and the
        # item master is created in every Company Sage Integration again.
        # -------------------------------------------------------------------
        SAGE_FORCE_COMPANY = ""
        companies = frappe.get_all("Company Sage Integration", fields=["name", "company"])
        if SAGE_FORCE_COMPANY:
            companies = [c for c in companies if c.name == SAGE_FORCE_COMPANY and c.company == SAGE_FORCE_COMPANY]
            # While locked, the testing company is the only Sage company there is, so
            # it also takes the opening quantity (as it always did during UAT).
            item_company = SAGE_FORCE_COMPANY
        else:
            # live: never create items in the Sage TEST company (review 31 Oct 2026)
            companies = [c for c in companies if c.name != "Ardmore Ceramics TEST"]

        for company_doc in companies:
            try:
                sage = frappe.get_doc("Company Sage Integration", company_doc.name)
                apikey = sage.get_password("api_key")
                loginName = sage.username
                loginPwd = sage.get_password("password")
                tax_id = sage.tax_id

                # Opening qty ONLY to the item's own company; master created everywhere
                qty_here = opening_qty if (item_company and company_doc.company == item_company) else 0

                url = f"https://pharoh.co.za/api/InventorySync/post-new-item-to-sage?apikey={apikey}"

                payload = {
                    "credentials": {
                        "loginName": loginName,
                        "loginPwd": loginPwd,
                        "useOAuth": False,
                        "sessionToken": None,
                        "provider": None
                    },
                    "item": {
                        "ID": 0,
                        "Code": doc.item_code,
                        "Description": doc.item_name or doc.description,
                        "Active": True if doc.disabled == 0 else False,
                        "Physical": True if doc.is_stock_item else False,
                        "Unit": doc.stock_uom or "Each",
                        "PriceExclusive": round(float(doc.custom_retail_price_incl_vat or 0) / 1.15, 2),
                        "PriceInclusive": float(doc.custom_retail_price_incl_vat or 0),
                        "TaxTypeIdSales": tax_id,
                        "TaxTypeIdPurchases": tax_id,
                        "LastCost": float(doc.last_purchase_rate or 0),
                        "AverageCost": float(doc.valuation_rate or 0),
                        "QuantityOnHand": qty_here,
                        "Created": frappe.utils.format_datetime(doc.creation, "yyyy-MM-dd'T'HH:mm:ss"),
                        "Modified": frappe.utils.format_datetime(doc.modified, "yyyy-MM-dd'T'HH:mm:ss")
                    }
                }

                response = frappe.make_post_request(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                sage_item_id = None
                if response:
                    sage_item_id = (response.get("SelectionID") or response.get("selectionId") or response.get("id") or response.get("ID"))

                if sage_item_id:
                    sel_name = doc.item_code + "-" + company_doc.company
                    if frappe.db.exists("Sage Item Selection", sel_name):
                        frappe.db.set_value("Sage Item Selection", sel_name, "selection_id", str(sage_item_id))
                    else:
                        sel = frappe.new_doc("Sage Item Selection")
                        sel.item_code = doc.item_code
                        sel.company = company_doc.company
                        sel.selection_id = str(sage_item_id)
                        sel.insert(ignore_permissions=True)
                    # the item's own SelectionID is its category company's (Russell, 3 Nov 2026): the master is
                    # created in every Sage company, and the other companies' IDs live in Sage Item Selection only
                    if company_doc.company == item_company:
                        frappe.db.set_value("Item", doc.name, "custom_sage_selection_id", str(sage_item_id))

                sync_results.append(f"✅ {doc.item_code} → {company_doc.company} (qty {qty_here})")

            except Exception as e:
                short_title = f"Sage Sync Failed for Item {doc.item_code} ({company_doc.company})"[:140]
                error_message = str(e)
                try:
                    error_message += f"\nResponse Body: {e.response.text}"
                except Exception:
                    pass
                frappe.log_error(title=short_title, message=error_message)
                sync_results.append(f"❌ {doc.item_code} → {company_doc.company}")

        if sync_results:
            frappe.msgprint("<br>".join(sync_results))

    except Exception as e:
        frappe.log_error(title="Sage Item Create Fatal Error"[:140], message=str(e))
