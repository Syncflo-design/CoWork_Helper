payload = {}
# VAT basis (27 Oct 2026): Ardmore's prices are VAT-inclusive and ERPNext backs the VAT out of the
# inclusive price. The Sage document is therefore sent INCLUSIVE too (unitPriceInclusive = the till
# price), so Sage derives the same cents as ERPNext: R150 incl stays R150, not R149.99 as it did
# when Sage rebuilt the total from the rounded exclusive line.

# Ardmore runs POS Settings > Invoice Type = "Sales Invoice": every till sale IS a
# tax invoice (is_pos = 1, is_consolidated = 0) and must reach Sage, otherwise Sage
# keeps its old quantity and the QOH sync writes the sold units back into the main
# warehouse (found 2026-09-21: 2 units sold, Main Distribution went 100 -> 102).
#
# soft_fail: a till sale must NEVER be blocked or rolled back because Sage is down
# or an item is not mapped. For till sales we log + flag "Failed" and let the sale
# stand. Back-office invoices keep the old behaviour (hard stop, visible error).
# Inside the try we `raise Exception` rather than frappe.throw: frappe.throw queues a
# popup even when the exception is caught, and the cashier must not see Sage errors.
#
# RETRY (2026-09-29): a failed post is recorded on the invoice - status, the
# reason, and an attempt count - and the scheduled job "retry-failed-sage-sync"
# runs this same script again until it gets through.
#   Failed      Sage refused it, or we never got as far as sending. Safe to resend.
#   Check Sage  the connection dropped AFTER we sent. Sage may or may not have the
#               invoice, so it is NOT resent automatically (a resend could create
#               a duplicate). Someone checks Sage, then uses "Send to Sage".
soft_fail = 1 if doc.get("is_pos") else 0

# ---------------------------------------------------------------------------
# TEST-ONLY LOCK (Russell, 2026-09-21): until he says otherwise, EVERY tax
# invoice posts to the Sage TESTING company and nowhere else. Item category is
# ignored. Two locks: (1) the company is forced here, (2) a hard check right
# before the HTTP call refuses any other integration.
# GO-LIVE: set SAGE_FORCE_COMPANY = "" and routing returns to the Sage entity that
# owns the till (POS Profile / warehouse) or, for an Account Sale, the customer's Sage
# account - see ROUTING below (22 Oct 2026). Also lift the lock in the sibling script.
# ---------------------------------------------------------------------------
SAGE_FORCE_COMPANY = ""
# While locked, every line carries the TEST company's own tax type. Items store
# the LIVE companies' tax type ids (4849096 / 2704020 / 5698238) which do not
# exist in the TEST company. GO-LIVE: this becomes 0 automatically when the
# constant above is blanked, and the item's own id is used again.
FORCE_TAX_TYPE_ID = 0
if SAGE_FORCE_COMPANY:
    FORCE_TAX_TYPE_ID = int(frappe.db.get_value("Company Sage Integration", SAGE_FORCE_COMPANY, "tax_id") or 0)

# TRAINING (Russell, 2026-10-16): the training company never talks to Sage - not on
# submit, not on retry, not from the Send to Sage button. Rule 1 of the training setup.
TRAINING_COMPANIES = ["Ardmore Ceramics TEST"]

if doc.company in TRAINING_COMPANIES:
    pass  # training till - never sent to Sage
elif doc.get("is_return"):
    pass  # credit notes are handled by post-customerreturn-to-sage
elif doc.get("is_pos") and doc.get("is_consolidated"):
    pass  # legacy day-end consolidation of old POS Invoices - never sent, leave as is
elif doc.get("custom_sage_order_id") and doc.get("custom_sage_sync_status") == "Synced":
    pass  # already in Sage - nothing to do (keeps a re-run from flagging it Failed)
else:
    try:
        if doc.get("custom_sage_order_id"):
            raise Exception("Invoice already has a Sage Order ID (" + str(doc.get("custom_sage_order_id")) + ") but is not marked Synced. Check Sage before resending.")
        if not doc.items:
            raise Exception("No items found in Sales Invoice.")

        # Tax rate from the invoice
        tax_rate = 0.0
        if doc.taxes:
            for tax_row in doc.taxes:
                if tax_row.charge_type == "On Net Total":
                    tax_rate = float(tax_row.rate or 0)
                    break

        # ROUTING (Russell + Jon, 22 Oct 2026): a till sale posts to the Sage entity that OWNS
        # the till - "Sage entity" on the POS Profile, else on the till's warehouse (Hyde Park ->
        # Home, Caversham -> Ceramics). The takings land in that entity's bank, so the sale sits
        # there too; stock made by another entity was already invoiced between the companies
        # when it moved into the store. An Account Sale (no till) posts to the Sage company where
        # the customer holds an account (Sage Customer Selection). Item category no longer
        # decides where a sale posts - it still says who owns the stock.
        route_company = None
        pos_profile_name = str(doc.get("pos_profile") or "")
        till_warehouse = str(doc.get("set_warehouse") or "")
        if doc.get("is_pos"):
            if pos_profile_name:
                route_company = frappe.db.get_value("POS Profile", pos_profile_name, "custom_sage_entity")
            if not route_company and till_warehouse:
                route_company = frappe.db.get_value("Warehouse", till_warehouse, "custom_sage_entity")
            if not route_company and not SAGE_FORCE_COMPANY:
                raise Exception("No Sage entity is set on POS Profile " + pos_profile_name + " or warehouse " + till_warehouse + ". Set it before this till can post to Sage.")
        else:
            mapped = frappe.get_all("Sage Customer Selection", filters={"customer": doc.customer}, pluck="company")
            if len(mapped) == 1:
                route_company = mapped[0]
            elif len(mapped) > 1:
                # an account in more than one entity: the entity of the goods when they are all
                # one entity's and it has an account there, otherwise the first account found
                cats = []
                for item in doc.items:
                    c = frappe.db.get_value("Item", item.item_code, "custom_category")
                    if c and c not in cats:
                        cats.append(c)
                route_company = cats[0] if (len(cats) == 1 and cats[0] in mapped) else sorted(mapped)[0]
            elif not SAGE_FORCE_COMPANY:
                raise Exception("Account Sale: " + str(doc.customer) + " has no Sage customer account (Sage Customer Selection). Add one before invoicing.")

        groups = {}
        for item in doc.items:
            # SALES OTHER (Russell, 6 Nov 2026, ticket 0129): a till line with no item code is typed by the
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
            try:
                selection_id = int(float(str(selection_raw).strip()))
            except:
                raise Exception(f"Sage SelectionID must be numeric for {item.item_code}")

            # ZERO-RATED (Russell, 28 Oct 2026): a sale rung up at VAT 0% (the till's VAT selector) carries
            # the Sage company's zero-rated tax type - also while locked to TEST (company is TEST then).
            if doc.get("tax_category") == "Zero Rated":
                tax_type_id = int(frappe.db.get_value("Company Sage Integration", company, "custom_sage_zero_tax_id") or 0)
                if not tax_type_id:
                    raise Exception(f"Sage Zero-rated Tax Type ID is not set on Company Sage Integration {company}.")
            else:
                tax_type_id = FORCE_TAX_TYPE_ID or int(frappe.db.get_value("Company Sage Integration", company, "tax_id") or 0) or int(item_doc.get("tax_typeid_sales") or item_doc.get("custom_sage_tax_type_id") or 0)
            item_exclusive = float(item.net_amount or item.amount or 0)
            item_tax = round(item_exclusive * (tax_rate / 100), 2)

            if company not in groups:
                groups[company] = []
            groups[company].append({
                "selectionId": selection_id,
                "lineType": 1 if is_other else 0,
                # the till's cart shortens a line's description, so the cashier's full words come from item_name
                "description": (item.item_name if is_other else (item.description or item.item_name)) or "",
                "unit": "" if is_other else (item.uom or ""),
                "comments": "",
                "quantity": float(item.qty or 0),
                "unitPriceExclusive": float(item.net_rate or item.rate or 0),
                "unitPriceInclusive": float(item.rate or 0),
                "unitCost": 0 if is_other else float(item.valuation_rate or item.net_rate or item.rate or 0),
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

        # One Sage invoice per company
        for company in groups.keys():
            lines = groups[company]
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

            # SALES REP (Jon, 27 Oct 2026): the person who rang it up - the Sage rep on their
            # User, else the till's rep, else the entity's default. Sales carry it so Sage can
            # report by salesperson; returns cannot post without one. Not while locked to TEST:
            # the User/till ids belong to the live companies, only the TEST default applies.
            sales_rep_id = 0
            if not SAGE_FORCE_COMPANY:
                # the sales person picked in the till's Select POS User (Russell, 27 Oct 2026: report who sold what)
                if doc.get("custom_sales_representative"):
                    sales_rep_id = int(frappe.db.get_value("Sales Person", doc.custom_sales_representative, "custom_sage_rep_id") or 0)
                sales_rep_id = sales_rep_id or int(frappe.db.get_value("User", doc.owner, "custom_sage_sales_rep_id") or 0)
                if not sales_rep_id and pos_profile_name:
                    sales_rep_id = int(frappe.db.get_value("POS Profile", pos_profile_name, "custom_sage_sales_rep_id") or 0)
            sales_rep_id = sales_rep_id or int(sage.get("custom_sage_pos_sales_rep_id") or 0)

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
            # still within 43 characters; the order number itself is never cut.
            order_no = str(doc.get("po_no") or "").strip() if doc.get("is_pos") else ""
            if order_no:
                who = buyer or str(doc.get("customer_name") or "").strip()
                room = 43 - len(order_no) - 2
                sage_reference = (who[:room].strip() + ": " + order_no) if (who and room > 0) else order_no[:43]
            url = f"https://pharoh.co.za/api/TaxInvoice/post-taxinvoice-to-sage?apikey={apikey}"
            payload = {
                "credentials": {"loginName": loginName, "loginPwd": loginPwd,
                                "useOAuth": False, "sessionToken": None, "provider": None},
                "invoice": {
                    "date": frappe.utils.formatdate(doc.posting_date, "yyyy-MM-dd"),
                    "inclusive": True,
                    # Sage wants percentages as fractions (0.10 = 10%), like taxPercentage. Sent as 10 it became
                    # 1000% and Sage booked a NEGATIVE invoice (found 31 Oct 2026, ACC-SINV-2026-00099).
                    "discountPercentage": round(float(doc.additional_discount_percentage or 0) / 100, 4),
                    "taxReference": "",
                    "customerName": customer_name,
                    "customerId": customer_id,
                    "dueDate": frappe.utils.formatdate(doc.due_date, "yyyy-MM-dd") if doc.due_date else frappe.utils.formatdate(doc.posting_date, "yyyy-MM-dd"),
                    "reference": sage_reference,
                    "message": doc.remarks or "",
                    "discount": round(sum(l.get("discount", 0) for l in lines), 2),
                    "exclusive": round(sum(l.get("exclusive", 0) for l in lines), 2),
                    "tax": round(sum(l.get("tax", 0) for l in lines), 2),
                    "rounding": 0,
                    "total": round(sum(l.get("total", 0) for l in lines), 2),
                    "amountDue": round(sum(l.get("total", 0) for l in lines), 2),
                    "lines": lines
                }
            }

            if sales_rep_id:
                payload["invoice"]["salesRepresentative"] = {"id": sales_rep_id}

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
            frappe.msgprint("Sage sync complete. Orders: " + ", ".join(order_ids))

    except Exception as e:
        err = str(e)
        low = err.lower()
        # Did the request possibly reach Sage before the line dropped?
        uncertain = ("timed out" in low) or ("timeout" in low) or ("connection aborted" in low) or ("remote end closed" in low)
        # never write the Sage login into the Error Log
        frappe.log_error(
            message=f"Sales Invoice: {doc.name}\nError: {err}\nInvoice sent: {str(payload.get('invoice') or '')}",
            title="Sage Sales Invoice Sync Error")
        try:
            doc.db_set("custom_sage_sync_status", "Check Sage" if uncertain else "Failed")
            doc.db_set("custom_sage_sync_error", err[:900])
            doc.db_set("custom_sage_sync_attempts", int(doc.get("custom_sage_sync_attempts") or 0) + 1)
        except Exception:
            pass
        if not soft_fail:
            frappe.throw(f"Sage Sync Failed: {err}")
