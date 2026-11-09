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
        last_date = frappe.utils.add_days(frappe.utils.today(), -30)  # last 30 days

        so_url = f"https://pharoh.co.za/api/SalesOrder/get-salesorders-for-erpnext?apikey={apikey}&lastDate={last_date}"
        payload = {"loginName": loginName, "loginPwd": loginPwd, "useOAuth": False, "sessionToken": None, "provider": None}

        # API call with debug
        sales_orders = None
        try:
            debug_start = f"API Start {sage.company}: {frappe.utils.now()} URL={so_url[:50]}..."[:140]
            frappe.log_error(debug_start, "Sage SO Sync Debug")
            sales_orders = frappe.make_post_request(so_url, json=payload)
            debug_resp = f"API Resp {sage.company}: {len(sales_orders) if sales_orders else 'None'} items"[:140]
            frappe.log_error(debug_resp, "Sage SO Sync Debug")
        except Exception as api_e:
            api_err_title = f"API Fail {sage.company}: {str(api_e)}"[:140]
            frappe.log_error(api_err_title, "Sage SO Sync Error")
            continue

        if not isinstance(sales_orders, list):
            invalid_title = f"Invalid Resp {sage.company}: not list"[:140]
            frappe.log_error(invalid_title, "Sage SO Sync")
            continue

        # Limit to 50 SOs per run
        sales_orders = sales_orders[:50]

        updated_sos = []
        created_sos = []
        skipped_sos = []

        # Caches
        uom_cache = set()
        stock_uom_cache = set()
        item_cache = set()
        group_cache = set(["Sage Imported Items"])
        warehouse_cache = {}  # Cache for warehouses

        batch_size = 20

        for i in range(0, len(sales_orders), batch_size):
            batch = sales_orders[i:i + batch_size]
            for so_data in batch:
                so_name = (so_data.get("name") or "").strip() if isinstance(so_data.get("name"), str) else so_data.get("name", "")
                customer_name = (so_data.get("customer_name") or "").strip() if isinstance(so_data.get("customer_name"), str) else so_data.get("customer_name", "")

                if not so_name or not customer_name:
                    skipped_sos.append(so_name)
                    continue

                try:
                    so_filter = {"custom_sage_name": so_name, "company": sage.company}
                    is_update = False

                    if frappe.db.exists("Sales Order", so_filter):
                        so_doc = frappe.get_doc("Sales Order", so_filter)
                        is_update = True
                        so_doc.set("items", [])
                    else:
                        so_doc = frappe.new_doc("Sales Order")
                        so_doc.naming_series = "SAL-ORD-.YYYY.-"
                        so_doc.custom_sage_name = so_name
                        so_doc.company = sage.company

                    # Direct field assignments
                    so_doc.customer = customer_name
                    so_doc.transaction_date = frappe.utils.getdate(so_data.get("transaction_date"))
                    so_doc.delivery_date = frappe.utils.getdate(so_data.get("delivery_date"))
                    so_doc.total = so_data.get("total", 0)
                    so_doc.total_taxes_and_charges = so_data.get("total_taxes_and_charges", 0)
                    so_doc.discount_amount = so_data.get("discount_amount", 0)

                    for item in so_data.get("items", []):
                        # Cached UOM
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

                        # Cached Stock UOM
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

                        # Cached Item
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

                        # --- Warehouse Handling ---
                        raw_warehouse = item.get("warehouse") or ""
                        if not raw_warehouse:
                            base_warehouse_name = "All Warehouses"
                        else:
                            base_warehouse_name = raw_warehouse.strip() if isinstance(raw_warehouse, str) else str(raw_warehouse)

                        # ERPNext auto adds company suffix (first letter capitalized)
                        company_suffix = sage.company[0].upper()
                        final_warehouse_name = f"{base_warehouse_name} - {company_suffix}"

                        # Check cache first
                        if final_warehouse_name in warehouse_cache:
                            warehouse_to_use = warehouse_cache[final_warehouse_name]
                        else:
                            existing_wh = frappe.db.exists("Warehouse", final_warehouse_name)
                            if existing_wh:
                                warehouse_to_use = final_warehouse_name
                            else:
                                wh_doc = frappe.new_doc("Warehouse")
                                wh_doc.warehouse_name = base_warehouse_name  # ERPNext adds suffix automatically
                                wh_doc.company = sage.company
                                wh_doc.insert(ignore_permissions=True)
                                warehouse_to_use = final_warehouse_name

                            warehouse_cache[final_warehouse_name] = warehouse_to_use

                        # Append item
                        so_doc.append("items", {
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
                            "warehouse": warehouse_to_use,
                            "cost_center": item.get("cost_center") or "",
                            "project": item.get("project") or ""
                        })

                    so_doc.save(ignore_permissions=True)

                    if is_update:
                        updated_sos.append(so_name)
                    else:
                        created_sos.append(so_name)

                except Exception as e:
                    proc_err_title = f"SO Proc Err {so_name}: {str(e)}"[:140]
                    frappe.log_error(proc_err_title)
                    skipped_sos.append(so_name)

            # Commit after each batch
            frappe.db.commit()

        # Final commit for the integration
        frappe.db.commit()

        summary_title = f"Sage SO Summary {sage.company}"[:140]
        summary = f"Company: {sage.company} | Processed {len(sales_orders)} SOs | Updated: {len(updated_sos)}, Created: {len(created_sos)}, Skipped: {len(skipped_sos)}"
        frappe.log_error(summary, summary_title)

    except Exception as e:
        fatal_title = f"Sage SO Fatal Err {integration.company}: {str(e)}"[:140]
        frappe.log_error(fatal_title)
