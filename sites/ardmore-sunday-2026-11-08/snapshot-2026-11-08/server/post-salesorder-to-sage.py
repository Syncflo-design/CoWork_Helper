payload = {}

try:

    # 1. Prevent duplicate sync
    if doc.get("custom_sage_order_id"):
        frappe.throw("Sales Order already synced to Sage.")

    # 2. Get Sage credentials
    sage = frappe.get_doc("Sage Integration", {"company": doc.company})
    apikey = sage.get_password("api_key")
    loginName = sage.username
    loginPwd = sage.get_password("password")

    if not apikey or not loginName or not loginPwd:
        frappe.throw("Sage credentials missing in Sage Integration.")

    url = f"https://pharoh.co.za/api/SalesOrder/post-salesorder-to-sage?apikey={apikey}"

    # 3. Validate Customer
    customer_doc = frappe.get_doc("Customer", doc.customer)
    sage_customer_id = customer_doc.get("custom_sage_customer_id")

    if not sage_customer_id:
        frappe.throw(f"Sage Customer ID missing on Customer: {doc.customer}")

    try:
        customer_id = int(sage_customer_id)
    except:
        frappe.throw("Sage Customer ID must be numeric.")

    # 3b. Validate Sales Rep
    sage_sales_rep_id = doc.get("custom_sage_sales_rep_id")
    if not sage_sales_rep_id:
        frappe.throw("Sage Sales Rep ID missing on Sales Order. Please fill in the 'Sage Sales Rep ID' field.")

    try:
        sales_rep_id = int(sage_sales_rep_id)
    except:
        frappe.throw("Sage Sales Rep ID must be numeric.")

    # 4. Get Tax Rate
    tax_rate = 0.0
    if doc.taxes:
        for tax_row in doc.taxes:
            if tax_row.charge_type == "On Net Total":
                tax_rate = float(tax_row.rate or 0)
                break

    # 5. Build Lines
    lines = []

    if not doc.items:
        frappe.throw("No items found in Sales Order.")

    for item in doc.items:

        item_doc = frappe.get_doc("Item", item.item_code)
        selection_raw = item_doc.get("custom_sage_selection_id")

        if not selection_raw:
            frappe.throw(
                f"Sage Selection ID missing for item: {item.item_code}. "
                f"Please sync this item to Sage first."
            )

        try:
            selection_id = int(float(str(selection_raw).strip()))
        except:
            frappe.throw(f"Sage Selection ID must be numeric for item: {item.item_code}")

        tax_type_id = int(item_doc.get("tax_typeid_sales") or item_doc.get("custom_sage_tax_type_id") or 0)

        item_exclusive = float(item.net_amount or item.amount or 0)
        item_rate_excl = float(item.net_rate or item.rate or 0)
        item_rate_incl = float(item.rate or 0)
        item_tax = round(item_exclusive * (tax_rate / 100), 2)
        item_total = round(item_exclusive + item_tax, 2)

        lines.append({
            "selectionId": selection_id,
            "id": 0,
            "lineType": 0,
            "description": item.description or item.item_name or "",
            "unit": item.uom or "",
            "comments": "",
            "quantity": float(item.qty or 0),
            "unitPriceExclusive": item_rate_excl,
            "unitPriceInclusive": item_rate_incl,
            "unitCost": float(item.valuation_rate or item.net_rate or item.rate or 0),
            "exclusive": item_exclusive,
            "discount": float(item.discount_amount or 0),
            "discountPercentage": float(item.discount_percentage or 0),
            "tax": item_tax,
            "total": item_total,
            "taxPercentage": round(tax_rate / 100, 4),
            "taxTypeId": tax_type_id
        })

    # 6. Build Payload
    payload = {
        "credentials": {
            "loginName": loginName,
            "loginPwd": loginPwd,
            "useOAuth": False,
            "sessionToken": None,
            "provider": None
        },
        "order": {
            "id": 0,
            "date": frappe.utils.formatdate(doc.transaction_date, "yyyy-MM-dd") + "T00:00:00",
            "deliveryDate": frappe.utils.formatdate(doc.delivery_date, "yyyy-MM-dd") + "T00:00:00" if doc.delivery_date else frappe.utils.formatdate(doc.transaction_date, "yyyy-MM-dd") + "T00:00:00",
            "customer": {
                "id": customer_id
            },
            "salesRepresentative": {
                "id": sales_rep_id
            },
            "reference": doc.name or "",
            "message": doc.remarks or "",
            "tax": float(doc.total_taxes_and_charges or 0),
            "discount": float(doc.discount_amount or 0),
            "total": float(doc.grand_total or 0),
            "lines": lines
        }
    }

    # 7. Send Request
    sage_response_text = "No response captured"

    try:
        response = frappe.make_post_request(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response and response.get("success"):
            doc.db_set("custom_sage_order_id", str(response.get("sageOrderId") or ""))
            doc.db_set("custom_sage_document_number", str(response.get("documentNumber") or ""))
            try:
                doc.db_set("custom_sage_sync_status", "Synced")
            except Exception:
                pass
            frappe.msgprint(
                f"Sage Sync Successful!\n"
                f"Sage Order ID: {response.get('sageOrderId')}\n"
                f"Document Number: {response.get('documentNumber')}"
            )
        else:
            error_msg = response.get("errorMessage") or str(response) if response else "Unknown"
            frappe.throw(f"Sage API Error: {error_msg}")

    except Exception as http_err:
        err_str = str(http_err)
        sage_body = ""
        try:
            sage_body = http_err.response.text
        except Exception:
            sage_body = err_str

        frappe.log_error(
            message=f"HTTP Error: {err_str}\nSage Response Body: {sage_body}\nPayload: {str(payload)}",
            title=f"Sage API HTTP Error - {doc.name}"
        )
        frappe.throw(f"Sage API Error: {sage_body}")

except Exception as e:
    frappe.log_error(
        message=f"Sales Order: {doc.name}\nCustomer: {doc.customer}\nError: {str(e)}\nPayload: {str(payload)}",
        title="Sage Sales Order Sync Error"
    )
    try:
        doc.db_set("custom_sage_sync_status", "Failed")
    except Exception:
        pass
    frappe.throw(f"Sage Sync Failed: {str(e)}")