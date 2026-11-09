# ----------------------------
# Main Script (Batch Commits for Data Persistence)
# ----------------------------

company_integrations = frappe.get_all("Company Sage Integration", fields=["name", "company"])

for integration in company_integrations:
    try:
        sage = frappe.get_doc("Company Sage Integration", integration.name)
        apikey = sage.get_password("api_key")
        loginName = sage.username
        loginPwd = sage.get_password("password")
        last_date = frappe.utils.add_days(frappe.utils.today(), -30)  # Dynamic: last 7 days

        po_url = f"https://pharoh.co.za/api/PurchaseOrder/get-purchaseorders-for-erpnext?apikey={apikey}&lastDate={last_date}"
        payload = {"loginName": loginName, "loginPwd": loginPwd, "useOAuth": False, "sessionToken": None, "provider": None}

        # Enhanced API call with exception handling
        purchase_orders = None
        try:
            debug_start = f"API Start {sage.company}: {frappe.utils.now()} URL={po_url[:50]}..."[:140]
            frappe.log_error(debug_start, "Sage PO Sync Debug")
            purchase_orders = frappe.make_post_request(po_url, json=payload)
            debug_resp = f"API Resp {sage.company}: {len(purchase_orders) if purchase_orders else 'None'} items"[:140]
            frappe.log_error(debug_resp, "Sage PO Sync Debug")
        except Exception as api_e:
            api_err_title = f"API Fail {sage.company}: {str(api_e)}"[:140]
            frappe.log_error(api_err_title, "Sage PO Sync Error")
            continue  # Skip to next integration

        if not isinstance(purchase_orders, list):
            invalid_title = f"Invalid Resp {sage.company}: not list"[:140]
            frappe.log_error(invalid_title, "Sage PO Sync")
            continue

        # Limit to 50 POs per run to prevent timeout
        purchase_orders = purchase_orders[:50]

        updated_pos = []
        created_pos = []
        skipped_pos = []

        # Caches to reduce DB queries
        uom_cache = set()
        stock_uom_cache = set()
        item_cache = set()
        group_cache = set(["Sage Imported Items"])  # Pre-add common group

        batch_size = 20

        for i in range(0, len(purchase_orders), batch_size):
            batch = purchase_orders[i:i + batch_size]
            for po_data in batch:
                po_name = (po_data.get("name") or "").strip() if isinstance(po_data.get("name"), str) else po_data.get("name", "")
                supplier_name = (po_data.get("supplier_name") or "").strip() if isinstance(po_data.get("supplier_name"), str) else po_data.get("supplier_name", "")

                if not po_name or not supplier_name:
                    skipped_pos.append(po_name)
                    continue

                try:
                    po_filter = {"custom_sage_name": po_name, "company": sage.company}
                    is_update = False

                    if frappe.db.exists("Purchase Order", po_filter):
                        po_doc = frappe.get_doc("Purchase Order", po_filter)
                        is_update = True
                        po_doc.set("items", [])
                    else:
                        po_doc = frappe.new_doc("Purchase Order")
                        po_doc.naming_series = "PUR-ORD-.YYYY.-"
                        po_doc.custom_sage_name = po_name
                        po_doc.company = sage.company

                    # Direct field assignments
                    po_doc.supplier = supplier_name
                    po_doc.transaction_date = frappe.utils.getdate(po_data.get("transaction_date"))
                    po_doc.schedule_date = frappe.utils.getdate(po_data.get("delivery_date"))
                    po_doc.total = po_data.get("total", 0)
                    po_doc.total_taxes_and_charges = po_data.get("total_taxes_and_charges", 0)
                    po_doc.discount_amount = po_data.get("discount_amount", 0)

                    for item in po_data.get("items", []):
                        # Cached UOM check/create
                        uom_name = (item.get("uom") or "Nos").strip() if isinstance(item.get("uom"), str) else (item.get("uom") or "Nos")
                        if not uom_name:
                            uom_name = "Nos"
                        if uom_name not in uom_cache:
                            if not frappe.db.exists("UOM", uom_name):
                                uom_doc = frappe.new_doc("UOM")
                                uom_doc.uom_name = uom_name
                                uom_doc.insert(ignore_permissions=True)
                            uom_cache.add(uom_name)
                        uom_val = uom_name

                        # Cached stock_uom
                        stock_uom_name = (item.get("stock_uom") or uom_val).strip() if isinstance(item.get("stock_uom"), str) else (item.get("stock_uom") or uom_val)
                        if not stock_uom_name:
                            stock_uom_name = uom_val
                        if stock_uom_name not in stock_uom_cache:
                            if not frappe.db.exists("UOM", stock_uom_name):
                                stock_uom_doc = frappe.new_doc("UOM")
                                stock_uom_doc.uom_name = stock_uom_name
                                stock_uom_doc.insert(ignore_permissions=True)
                            stock_uom_cache.add(stock_uom_name)
                        stock_uom_val = stock_uom_name

                        # Cached Item Group
                        item_group_name = "Sage Imported Items"
                        if item_group_name not in group_cache:
                            if not frappe.db.exists("Item Group", item_group_name):
                                ig_doc = frappe.new_doc("Item Group")
                                ig_doc.item_group_name = item_group_name
                                ig_doc.parent_item_group = "All Item Groups"
                                ig_doc.insert(ignore_permissions=True)
                            group_cache.add(item_group_name)

                        # Cached Item check/create
                        item_code_param = (item.get("code") or "").strip() if isinstance(item.get("code"), str) else item.get("code", "")
                        item_name_param = (item.get("item_name") or "").strip() if isinstance(item.get("item_name"), str) else item.get("item_name", "")
                        description_param = (item.get("description") or "").strip() if isinstance(item.get("description"), str) else item.get("description", "")
                        if not item_code_param:
                            item_code_param = item_name_param or "ITEM-" + frappe.generate_hash("", 5)
                        if not item_name_param:
                            item_name_param = item_code_param
                        if not description_param:
                            description_param = item_name_param

                        if item_code_param not in item_cache:
                            if not frappe.db.exists("Item", item_code_param):
                                item_doc = frappe.new_doc("Item")
                                item_doc.item_code = item_code_param
                                item_doc.item_name = item_name_param
                                item_doc.description = description_param
                                item_doc.stock_uom = stock_uom_val
                                item_doc.is_stock_item = 1
                                item_doc.item_group = item_group_name
                                item_doc.insert(ignore_permissions=True)
                            item_cache.add(item_code_param)

                        item_code = item_code_param

                        po_doc.append("items", {
                            "item_code": item_code,
                            "item_name": item_name_param,
                            "description": description_param,
                            "qty": item.get("qty") or 0,
                            "uom": uom_val,
                            "stock_uom": stock_uom_val,
                            "conversion_factor": item.get("conversion_factor", 1),
                            "rate": item.get("rate", 0),
                            "amount": item.get("amount", 0),
                            "discount_percentage": item.get("discount_percentage", 0),
                            "discount_amount": item.get("discount_amount", 0),
                            "warehouse": item.get("warehouse") or "",
                            "cost_center": item.get("cost_center") or "",
                            "project": item.get("project") or ""
                        })

                    po_doc.save(ignore_permissions=True)

                    if is_update:
                        updated_pos.append(po_name)
                    else:
                        created_pos.append(po_name)

                except Exception as e:
                    proc_err_title = f"PO Proc Err {po_name}: {str(e)}"[:140]
                    frappe.log_error(proc_err_title)
                    skipped_pos.append(po_name)

            # Commit after each batch to persist changes
            frappe.db.commit()

        # Final commit for the integration
        frappe.db.commit()

        summary_title = f"Sage PO Summary {sage.company}"[:140]
        summary = f"Company: {sage.company} | Processed {len(purchase_orders)} POs | Updated: {len(updated_pos)}, Created: {len(created_pos)}, Skipped: {len(skipped_pos)}"
        frappe.log_error(summary, summary_title)

    except Exception as e:
        fatal_title = f"Sage Fatal Err {integration.company}: {str(e)}"[:140]
        frappe.log_error(fatal_title)