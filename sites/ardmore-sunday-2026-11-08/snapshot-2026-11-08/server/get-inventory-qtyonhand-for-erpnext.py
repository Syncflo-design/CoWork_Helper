def safe_float(val):
    # Comma-aware: Sage sends decimals as "208,696" (= 208.696). A plain
    # float() throws on that and silently yields 0.0, while Frappe's flt()
    # strips the comma and yields 208696. Both are wrong - parse explicitly.
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

now = frappe.utils.now_datetime()
whole_uoms = frappe.get_all("UOM", filters={"must_be_whole_number": 1}, pluck="name")

company_integrations = frappe.get_all("Company Sage Integration", fields=["name", "company"])

for integration in company_integrations:
    try:
        sage = frappe.get_doc("Company Sage Integration", integration.name)
        warehouse = sage.custom_default_warehouse
        if not warehouse:
            continue

        retry_after = sage.custom_sage_retry_after
        if retry_after and now < frappe.utils.get_datetime(retry_after):
            continue

        apikey = sage.get_password("api_key")
        loginName = sage.username
        loginPwd = sage.get_password("password")

        sync_start = frappe.utils.nowdate()
        lastDate = sage.custom_last_qtyonhand_sync or "1970-01-01"
        # Switch-on (Russell, 2026-10-16): the FIRST full pull skips items with zero on hand -
        # Main Distribution starts empty, so only items with stock matter and the pull is a
        # fraction of the size. Every later (incremental) pull MUST include zeros: when a
        # piece sells out in Sage, that zero is what takes Main Distribution down.
        incl_zero = "false" if lastDate == "1970-01-01" else "true"

        # PER COMPANY (Russell, 1 Nov 2026 - go-live day): each Sage company's on-hand lands in
        # ITS OWN ERPNext warehouse (Home -> JHB Atrium Home, Fashion -> JHB Atrium Fashion,
        # Ceramics -> Main Distribution), less that company's stock held in the other warehouses
        # it owns (Warehouse "Sage entity"): Home's stores and Online, Ceramics' transit
        # warehouse and Caversham. The ERPNext company comes from the warehouse.
        owner = frappe.db.get_value("Warehouse", warehouse, "custom_sage_entity")
        if owner != integration.name:
            frappe.log_error(message=f"Stock sync target {warehouse} belongs to {owner or 'no Sage company'}, not {integration.name}. Set the warehouse's Sage entity, or point {integration.name} at its own warehouse.", title=f"Sage QOH wrong warehouse {integration.company}"[:140])
            continue
        wh_company = frappe.db.get_value("Warehouse", warehouse, "company")
        other_whs = frappe.get_all("Warehouse", filters={"company": wh_company, "name": ["!=", warehouse], "is_group": 0, "disabled": 0, "custom_sage_entity": integration.name}, pluck="name")

        skipQty = 0
        has_more = True
        throttled = False
        rows = []

        while has_more:
            url = f"https://pharoh.co.za/api/InventorySync/get-inventory-qtyonhand-for-erpnext?apikey={apikey}&lastDate={lastDate}&skipQty={skipQty}&InclZeroOnHand={incl_zero}"
            payload = {"loginName": loginName, "loginPwd": loginPwd, "useOAuth": False, "sessionToken": None, "provider": None}

            try:
                response = frappe.make_post_request(url, json=payload)
            except Exception as http_err:
                status = None
                try:
                    status = http_err.response.status_code
                except Exception:
                    status = None
                if status == 503 or status == 429:
                    wait_secs = 5
                    try:
                        ra = http_err.response.headers.get("Retry-After")
                        if ra:
                            wait_secs = int(float(ra))
                    except Exception:
                        pass
                    try:
                        body = http_err.response.json()
                        if body and body.get("retryAfterSeconds"):
                            wait_secs = int(float(body.get("retryAfterSeconds")))
                    except Exception:
                        pass
                    block_until = frappe.utils.add_to_date(now, seconds=wait_secs)
                    frappe.db.set_value("Company Sage Integration", integration.name, "custom_sage_retry_after", block_until)
                    frappe.log_error(message=f"Pharoh asked us to wait {wait_secs}s (until {block_until})", title=f"Sage QOH backoff {integration.company}"[:140])
                    throttled = True
                    break
                else:
                    raise

            items = response.get("items") or []
            total = response.get("totalResults", 0)
            returned = response.get("returnedResults", 0)

            if not items:
                break

            for item_data in items:
                item_code = str(item_data.get("code") or "").strip()
                if not item_code:
                    continue
                if not frappe.db.exists("Item", item_code):
                    continue

                # Skip disabled items (e.g. SAMPLE / DISPLAY stock). ERPNext refuses
                # a Stock Reconciliation line for a disabled item ("Item X is
                # disabled"), and because rows are submitted in batches, ONE disabled
                # item used to fail the whole batch and block the good items with it.
                if frappe.db.get_value("Item", item_code, "disabled"):
                    continue

                # Skip items whose quantity was added straight into ERPNext by an
                # importer because Sage could not be updated (no update-item endpoint
                # yet - post-new-item-to-sage CREATES a duplicate, verified 2026-07-28).
                # Without this guard the line below would compute
                # target = sage_qty - other_warehouses and wipe the local figure on the
                # very next run. Untick the flag on the Item once Sage is correct.
                if frappe.db.get_value("Item", item_code, "custom_qty_pending_sage"):
                    continue

                sage_qty = safe_float(item_data.get("quantityOnHand"))
                # Only fabrics (Meter) take decimals; every other item counts in whole units
                # (Russell, 1 Nov 2026). Sage holds some half napkins and placemats (153.5): round
                # those down, or the line fails its whole Stock Reconciliation batch.
                if sage_qty != int(sage_qty) and frappe.db.get_value("Item", item_code, "stock_uom") in whole_uoms:
                    sage_qty = float(int(sage_qty))
                # Value the stock at OUR cost. The Sage averageCost is only a fallback
                # for items that have no Item_Cost of their own yet.
                val_rate = safe_float(frappe.db.get_value("Item", item_code, "custom_item_cost"))
                if val_rate <= 0:
                    val_rate = safe_float(item_data.get("averageCost"))
                # Sage can carry a negative average cost; ERPNext refuses a negative valuation
                # and the line would fail its whole batch, so it goes in at zero instead.
                if val_rate < 0:
                    val_rate = 0.0
                # Each company's figure is kept per item in custom_sage_qoh_by_company (JSON, read by
                # the count loader's checks) and their sum in custom_quantity_on_hand. The warehouse
                # itself is reconciled to THIS company's figure only (per-company warehouses, 1 Nov 2026).
                by_company = {}
                raw = frappe.db.get_value("Item", item_code, "custom_sage_qoh_by_company")
                if raw:
                    try:
                        by_company = json.loads(raw)
                    except Exception:
                        by_company = {}
                by_company[integration.name] = sage_qty
                total_qty = 0.0
                for k in by_company:
                    total_qty = total_qty + safe_float(by_company[k])
                frappe.db.set_value("Item", item_code, "custom_sage_qoh_by_company", json.dumps(by_company), update_modified=False)
                frappe.db.set_value("Item", item_code, "custom_quantity_on_hand", total_qty)

                other_qty = 0
                if other_whs:
                    bins = frappe.get_all("Bin", filters={"item_code": item_code, "warehouse": ["in", other_whs]}, fields=["actual_qty"])
                    for b in bins:
                        other_qty = other_qty + safe_float(b.actual_qty)

                target_qty = sage_qty - other_qty
                if target_qty < 0:
                    target_qty = 0

                current_qty = safe_float(frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty") or 0)
                if current_qty != target_qty:
                    rows.append({"item_code": item_code, "warehouse": warehouse, "qty": target_qty, "valuation_rate": val_rate})

            # Release row locks taken by the set_value calls above before fetching the
            # next page. Without this the whole paginated read ran inside ONE long
            # transaction, holding locks on thousands of Item rows while the (slow)
            # Sage calls completed — which collided with the inventory sync job and
            # made the Stock Reconciliation below die with
            # "(1205, 'Lock wait timeout exceeded')". That is why Sage quantities
            # were stamped on the Item but never became real stock.
            frappe.db.commit()

            skipQty = skipQty + returned
            has_more = skipQty < total

        if throttled:
            continue

        # Smaller batches = shorter locks on Bin / Stock Ledger, so a busy moment
        # no longer takes out the whole run. Each batch is retried once.
        batch_failed = False
        chunk = 25
        idx = 0
        while idx < len(rows):
            batch = rows[idx:idx + chunk]
            attempt = 0
            while attempt < 2:
                try:
                    sr = frappe.new_doc("Stock Reconciliation")
                    sr.company = wh_company
                    sr.purpose = "Stock Reconciliation"
                    for r in batch:
                        sr.append("items", {
                            "item_code": r["item_code"],
                            "warehouse": r["warehouse"],
                            "qty": r["qty"],
                            "valuation_rate": r["valuation_rate"],
                            # no cost anywhere: let the line through at zero instead of failing its whole batch
                            "allow_zero_valuation_rate": 1 if r["valuation_rate"] <= 0 else 0
                        })
                    sr.insert(ignore_permissions=True)
                    sr.submit()
                    frappe.db.commit()
                    break
                except Exception as e_sr:
                    frappe.db.rollback()
                    attempt = attempt + 1
                    if attempt >= 2:
                        frappe.log_error(message=str(e_sr) + f"\nItems: {len(batch)} starting {batch[0]['item_code']}", title=f"Sage QOH Recon failed {integration.company}"[:140])
                        batch_failed = True
            idx = idx + chunk

        if retry_after:
            frappe.db.set_value("Company Sage Integration", integration.name, "custom_sage_retry_after", None)
        # a failed batch keeps the old date, so the next run pulls those items again instead of
        # leaving them out until they next change in Sage (review 31 Oct 2026)
        if not batch_failed:
            frappe.db.set_value("Company Sage Integration", integration.name, "custom_last_qtyonhand_sync", sync_start)
        frappe.db.commit()

    except Exception as e:
        frappe.log_error(message=str(e), title=f"Sage QOH Sync Fatal Error for {integration.company}"[:140])
