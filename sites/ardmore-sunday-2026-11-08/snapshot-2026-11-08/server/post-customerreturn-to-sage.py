payload = {}
# VAT basis (27 Oct 2026): Ardmore's prices are VAT-inclusive and ERPNext backs the VAT out of the
# inclusive price. The Sage document is therefore sent INCLUSIVE too (unitPriceInclusive = the till
# price), so Sage derives the same cents as ERPNext: R150 incl stays R150, not R149.99 as it did
# when Sage rebuilt the total from the rounded exclusive line.

# Credit notes (returns) -> Sage customer return.  Rewritten 2026-09-29.
#
# Before this, a return made on the TILL never reached Sage: the script skipped
# every "is_return and is_pos" document, waiting for a day-end consolidated credit
# note that no longer exists now that Ardmore runs POS Settings > Invoice Type =
# "Sales Invoice". Sage kept the sale, its stock stayed one short, and the return
# even SHOWED "Synced" because ERPNext copied the sale's Sage fields onto it.
#
# Now a till return posts to Sage the moment it is submitted, the same way a till
# sale does (see post-taxinvoice-to-sage, which this mirrors on purpose):
#   - credentials + Sage customer come from Company Sage Integration
#   - item ids come from Sage Item Selection for that company
#   - it refers back to the Sage invoice of the ORIGINAL sale
#
# soft_fail: a till return must NEVER be blocked because Sage is down. For till
# returns we log + flag the document and let the return stand. Back-office credit
# notes keep the hard stop. Inside the try we `raise Exception`, not frappe.throw:
# frappe.throw queues a popup even when caught, and the cashier must not see it.
#
# RETRY: status / reason / attempt count are written to the document and the
# scheduled job "retry-failed-sage-sync" runs this script again.
#   Failed      safe to resend (includes "the original sale is not in Sage yet")
#   Check Sage  the connection dropped after sending - not resent automatically
soft_fail = 1 if doc.get("is_pos") else 0

# ---------------------------------------------------------------------------
# TEST-ONLY LOCK (Russell, 2026-09-21): until he says otherwise, EVERYTHING
# posts to the Sage TESTING company and nowhere else. Same two locks as the
# tax invoice script.
# GO-LIVE: set SAGE_FORCE_COMPANY = "" and routing follows the ORIGINAL sale: the Sage
# entity that owns the till, or the customer's Sage account - see ROUTING below (22 Oct 2026).
# ---------------------------------------------------------------------------
SAGE_FORCE_COMPANY = ""
FORCE_TAX_TYPE_ID = 0
if SAGE_FORCE_COMPANY:
    FORCE_TAX_TYPE_ID = int(frappe.db.get_value("Company Sage Integration", SAGE_FORCE_COMPANY, "tax_id") or 0)

# TRAINING (Russell, 2026-10-16): the training company never talks to Sage - not on
# submit, not on retry, not from the Send to Sage button. Rule 1 of the training setup.
TRAINING_COMPANIES = ["Ardmore Ceramics TEST"]

if doc.company in TRAINING_COMPANIES:
    pass  # training till - never sent to Sage
elif not doc.get("is_return"):
    pass  # sales are handled by post-taxinvoice-to-sage
elif doc.get("is_pos") and doc.get("is_consolidated"):
    pass  # legacy day-end consolidated credit notes - never sent, leave as is
elif doc.get("custom_sage_order_id") and doc.get("custom_sage_sync_status") == "Synced":
    pass  # already in Sage
else:
    try:
        if doc.get("custom_sage_order_id"):
            raise Exception("Credit Note already has a Sage ID (" + str(doc.get("custom_sage_order_id")) + ") but is not marked Synced. Check Sage before resending.")

        return_against = doc.get("return_against")
        if not return_against:
            raise Exception("Return Against (original invoice) is missing on this Credit Note.")
        if not doc.items:
            raise Exception("No items found in Credit Note.")

        original = frappe.get_doc("Sales Invoice", return_against)
        if not original.get("custom_sage_order_id") or original.get("custom_sage_sync_status") != "Synced":
            raise Exception(f"Original invoice {return_against} is not in Sage yet. This return will go through once that sale has.")

        # ROUTING (Russell + Jon, 22 Oct 2026): a return follows the ORIGINAL sale, and that
        # posted to the Sage entity that owns the till (POS Profile > warehouse), or, for an
        # Account Sale, to the Sage company where the customer holds an account. Mirrors
        # post-taxinvoice-to-sage.
        route_company = None
        pos_profile_name = str(original.get("pos_profile") or "")
        till_warehouse = str(original.get("set_warehouse") or "")
        if original.get("is_pos"):
            if pos_profile_name:
                route_company = frappe.db.get_value("POS Profile", pos_profile_name, "custom_sage_entity")
            if not route_company and till_warehouse:
                route_company = frappe.db.get_value("Warehouse", till_warehouse, "custom_sage_entity")
            if not route_company and not SAGE_FORCE_COMPANY:
                raise Exception("No Sage entity is set on POS Profile " + pos_profile_name + " or warehouse " + till_warehouse + ".")
        else:
            mapped = frappe.get_all("Sage Customer Selection", filters={"customer": original.customer}, pluck="company")
            if len(mapped) == 1:
                route_company = mapped[0]
            elif len(mapped) > 1:
                cats = []
                for oi in original.items:
                    c = frappe.db.get_value("Item", oi.item_code, "custom_category")
                    if c and c not in cats:
                        cats.append(c)
                route_company = cats[0] if (len(cats) == 1 and cats[0] in mapped) else sorted(mapped)[0]
            elif not SAGE_FORCE_COMPANY:
                raise Exception("Account Sale return: " + str(original.customer) + " has no Sage customer account (Sage Customer Selection).")
        orig_companies = [SAGE_FORCE_COMPANY or route_company]
        orig_ids = [x.strip() for x in str(original.get("custom_sage_order_id") or "").split(",")]
        orig_nums = [x.strip() for x in str(original.get("custom_sage_document_number") or "").split(",")]

        # Tax rate from the credit note
        tax_rate = 0.0
        if doc.taxes:
            for tax_row in doc.taxes:
                if tax_row.charge_type == "On Net Total":
                    tax_rate = float(tax_row.rate or 0)
                    break

        # Group lines by company. Credit notes carry negatives - Sage wants positives.
        groups = {}
        for item in doc.items:
            item_doc = frappe.get_doc("Item", item.item_code)
            if not SAGE_FORCE_COMPANY and not item_doc.get("custom_category"):
                raise Exception(f"Set ERPNext Category on {item.item_code} before syncing.")
            company = SAGE_FORCE_COMPANY or route_company

            selection_raw = frappe.db.get_value(
                "Sage Item Selection",
                {"item_code": item.item_code, "company": company},
                "selection_id")
            if not selection_raw:
                raise Exception(f"No Sage SelectionID for {item.item_code} in {company}. Sync this item for {company} first.")
            try:
                selection_id = int(float(str(selection_raw).strip()))
            except:
                raise Exception(f"Sage SelectionID must be numeric for {item.item_code}")

            # ZERO-RATED (Russell, 28 Oct 2026): the return of a sale rung up at VAT 0% carries the Sage
            # company's zero-rated tax type - also while locked to TEST (company is TEST then).
            if (doc.get("tax_category") or original.get("tax_category")) == "Zero Rated":
                tax_type_id = int(frappe.db.get_value("Company Sage Integration", company, "custom_sage_zero_tax_id") or 0)
                if not tax_type_id:
                    raise Exception(f"Sage Zero-rated Tax Type ID is not set on Company Sage Integration {company}.")
            else:
                tax_type_id = FORCE_TAX_TYPE_ID or int(frappe.db.get_value("Company Sage Integration", company, "tax_id") or 0) or int(item_doc.get("tax_typeid_sales") or item_doc.get("custom_sage_tax_type_id") or 0)
            item_exclusive = abs(float(item.net_amount or item.amount or 0))
            item_tax = round(item_exclusive * (tax_rate / 100), 2)

            if company not in groups:
                groups[company] = []
            groups[company].append({
                "selectionId": selection_id,
                "id": 0,
                "lineType": 0,
                "description": item.description or item.item_name or "",
                "unit": item.uom or "",
                "comments": "",
                "quantity": abs(float(item.qty or 0)),
                "unitPriceExclusive": abs(float(item.net_rate or item.rate or 0)),
                "unitPriceInclusive": abs(float(item.rate or 0)),
                "unitCost": abs(float(item.valuation_rate or item.net_rate or item.rate or 0)),
                "exclusive": item_exclusive,
                # The till price IS the selling price (ceramic pieces can be repriced on the till,
                # 2 Nov 2026): rate already carries any line discount, so none is sent on top.
                "discount": 0,
                "discountPercentage": 0,
                "tax": item_tax,
                "total": round(item_exclusive + item_tax, 2),
                "taxPercentage": round(tax_rate / 100, 4),
                "taxTypeId": tax_type_id
            })

        order_ids = []
        doc_numbers = []

        # One Sage customer return per company
        for company in groups.keys():
            lines = groups[company]

            if company not in orig_companies:
                raise Exception(f"{company} was not part of the original sale {return_against}.")
            pos_in_orig = orig_companies.index(company)
            if pos_in_orig >= len(orig_ids) or not orig_ids[pos_in_orig]:
                raise Exception(f"Original invoice {return_against} has no Sage Order ID for {company}.")
            try:
                from_document_id = int(float(orig_ids[pos_in_orig]))
            except:
                raise Exception(f"Sage Order ID on {return_against} is not numeric: {orig_ids[pos_in_orig]}")
            from_document_number = orig_nums[pos_in_orig] if pos_in_orig < len(orig_nums) else ""

            if not frappe.db.exists("Company Sage Integration", company):
                raise Exception(f"No Company Sage Integration for category '{company}'.")
            sage = frappe.get_doc("Company Sage Integration", company)
            # lock 2: never talk to any Sage company other than the forced one
            if SAGE_FORCE_COMPANY and (company != SAGE_FORCE_COMPANY or sage.name != SAGE_FORCE_COMPANY or sage.company != SAGE_FORCE_COMPANY):
                raise Exception(f"Blocked: Sage posting is locked to '{SAGE_FORCE_COMPANY}' but resolved '{sage.name}'.")
            apikey = sage.get_password("api_key")
            loginName = sage.username
            loginPwd = sage.get_password("password")
            if not apikey or not loginName or not loginPwd:
                raise Exception(f"Sage credentials missing for {company}.")

            # ACCOUNT SALE (Russell, 2026-10-21): a till sale (is_pos) posts against the
            # company's cash/POS customer as before. Any other document - a stockist or
            # account holder invoiced from the back office, no till close-out - posts
            # against the customer's OWN Sage account for this company, taken from Sage
            # Customer Selection (filled by the hourly customer sync, or by hand).
            if doc.get("is_pos"):
                # the store's own cash customer when the till names one (not while locked to TEST)
                till = frappe.db.get_value("POS Profile", pos_profile_name, ["custom_sage_cash_customer_id", "custom_sage_cash_customer_name"], as_dict=True) if (pos_profile_name and not SAGE_FORCE_COMPANY) else None
                customer_id = (till.custom_sage_cash_customer_id if till and till.custom_sage_cash_customer_id else None) or sage.get("sage_pos_customer_id")
                customer_name = (till.custom_sage_cash_customer_name if till and till.custom_sage_cash_customer_name else None) or sage.get("sage_pos_customer_name") or ""
                if not customer_id:
                    raise Exception(f"Sage customer not set on Company Sage Integration {company}.")
            else:
                customer_id = frappe.db.get_value("Sage Customer Selection", {"customer": doc.customer, "company": company}, "sage_customer_id")
                customer_name = doc.customer_name or doc.customer or ""
                if not customer_id:
                    raise Exception(f"Account Sale: {doc.customer} has no Sage Customer ID for {company}. Add a Sage Customer Selection row for it, or wait for the hourly customer sync.")
            try:
                customer_id = int(customer_id)
            except:
                raise Exception(f"Sage customer id must be numeric for {company}.")

            # Sage will not accept a customer return without a sales representative
            # ("Sales Representative is Required"). A rep id belongs to ONE Sage
            # company, so the till's rep is held per company on Company Sage
            # Integration, next to the POS customer.
            # SALES REP (Jon, 27 Oct 2026): the sales person of the original sale - the return copies
            # it (Russell, 27 Oct 2026: report who sold what) - else the Sage rep on the User who
            # processed it, else the till's rep, else the entity's default (the only one used while
            # locked to TEST).
            sales_rep_id = 0
            if not SAGE_FORCE_COMPANY:
                sales_person = doc.get("custom_sales_representative") or original.get("custom_sales_representative")
                if sales_person:
                    sales_rep_id = int(frappe.db.get_value("Sales Person", sales_person, "custom_sage_rep_id") or 0)
                sales_rep_id = sales_rep_id or int(frappe.db.get_value("User", doc.owner, "custom_sage_sales_rep_id") or 0)
                if not sales_rep_id and pos_profile_name:
                    sales_rep_id = int(frappe.db.get_value("POS Profile", pos_profile_name, "custom_sage_sales_rep_id") or 0)
            sales_rep_id = sales_rep_id or int(sage.get("custom_sage_pos_sales_rep_id") or 0)
            if not sales_rep_id:
                raise Exception(f"Sage POS Sales Rep ID is not set on Company Sage Integration {company}.")

            total_excl = round(sum(l.get("exclusive", 0) for l in lines), 2)
            total_tax = round(sum(l.get("tax", 0) for l in lines), 2)
            total_all = round(sum(l.get("total", 0) for l in lines), 2)

            # REFERENCE (Russell + Jon, 2 Nov 2026): a till sale sits in Sage under the till's cash
            # customer, so the reference names who bought it (Invoice To; nobody for a walk-in) before
            # our number, as Sage's Cust. Ref did before go-live. At most 43 characters: the longest
            # reference Sage Home already holds.
            sage_reference = doc.name or ""
            buyer = str(doc.get("custom_invoice_to_name") or "").strip() if doc.get("is_pos") else ""
            if buyer and len(sage_reference) < 40:
                sage_reference = buyer[:40 - len(sage_reference)].strip() + " - " + sage_reference
            # ONLINE ORDER NUMBER (Russell, 3 Nov 2026): the Online till's Order Number box (Customer's
            # Purchase Order, one per invoice) goes to Sage's Customer Ref as "Customer name: order number",
            # still within 43 characters; the order number itself is never cut. A return carries its sale's number.
            order_no = str(doc.get("po_no") or original.get("po_no") or "").strip() if doc.get("is_pos") else ""
            if order_no:
                who = buyer or str(doc.get("customer_name") or "").strip()
                room = 43 - len(order_no) - 2
                sage_reference = (who[:room].strip() + ": " + order_no) if (who and room > 0) else order_no[:43]
            customer_return = {
                "date": frappe.utils.formatdate(doc.posting_date, "yyyy-MM-dd") + "T00:00:00",
                "inclusive": True,
                # Sage wants percentages as fractions (0.10 = 10%), like taxPercentage. Sent as 10 it became
                # 1000% (found 31 Oct 2026 on a sale; returns carry the same discount).
                "discountPercentage": round(abs(float(doc.additional_discount_percentage or 0)) / 100, 4),
                "taxReference": "",
                "reference": sage_reference,
                "message": doc.remarks or "",
                "discount": round(sum(l.get("discount", 0) for l in lines), 2),
                "exclusive": total_excl,
                "tax": total_tax,
                "rounding": 0,
                "total": total_all,
                "amountDue": total_all,
                "customer": {"id": customer_id},
                "fromDocument": from_document_number,
                "fromDocumentId": from_document_id,
                "fromDocumentTypeId": 1,
                "lines": lines
            }
            customer_return["salesRepresentative"] = {"id": sales_rep_id}

            url = f"https://pharoh.co.za/api/CustomerReturn/post-customerreturn-to-sage?apikey={apikey}"
            payload = {
                "credentials": {"loginName": loginName, "loginPwd": loginPwd,
                                "useOAuth": False, "sessionToken": None, "provider": None},
                "customerReturn": customer_return
            }

            try:
                response = frappe.make_post_request(url, json=payload, headers={"Content-Type": "application/json"})
            except Exception as http_err:
                body = ""
                try:
                    body = str(http_err.response.text)[:400]
                except Exception:
                    body = ""
                # the request URL carries the API key - keep it out of the document and the log
                where = str(http_err)[:300].replace(str(apikey), "***")
                raise Exception(f"Sage HTTP error for {company}: {where} {body}")

            if response and response.get("success"):
                order_ids.append(str(response.get("sageOrderId") or ""))
                doc_numbers.append(str(response.get("documentNumber") or ""))
                # save progress immediately so a retry can't double-post this company
                doc.db_set("custom_sage_order_id", ", ".join(order_ids))
                doc.db_set("custom_sage_document_number", ", ".join(doc_numbers))
            else:
                error_msg = response.get("errorMessage") or str(response) if response else "Unknown"
                raise Exception(f"Sage API Error for {company}: {error_msg}")

        doc.db_set("custom_sage_sync_status", "Synced")
        doc.db_set("custom_sage_sync_error", "")
        if not soft_fail:
            frappe.msgprint("Sage sync complete. Customer returns: " + ", ".join(doc_numbers))

    except Exception as e:
        err = str(e)
        low = err.lower()
        # Did the request possibly reach Sage before the line dropped?
        uncertain = ("timed out" in low) or ("timeout" in low) or ("connection aborted" in low) or ("remote end closed" in low)
        # never write the Sage login into the Error Log
        frappe.log_error(
            message=f"Credit Note: {doc.name}\nError: {err}\nReturn sent: {str(payload.get('customerReturn') or '')}",
            title="Sage Customer Return Sync Error")
        try:
            doc.db_set("custom_sage_sync_status", "Check Sage" if uncertain else "Failed")
            doc.db_set("custom_sage_sync_error", err[:900])
            doc.db_set("custom_sage_sync_attempts", int(doc.get("custom_sage_sync_attempts") or 0) + 1)
        except Exception:
            pass
        if not soft_fail:
            frappe.throw(f"Sage Sync Failed: {err}")
