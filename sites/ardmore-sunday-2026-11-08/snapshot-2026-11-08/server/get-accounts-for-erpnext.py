
# -------------------- Helpers --------------------
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_parent_account(root_type, company_name):
    """Return parent account name based on root_type and company suffix"""
    # Inline strip logic
    def strip_if_str(value):
        return value.strip() if isinstance(value, str) else value
    
    initial = company_name[0].upper() if company_name else "C"
    root_type_lower = strip_if_str(root_type or "").lower()

    if "asset" in root_type_lower:
        return f"Application of Funds (Assets) - {initial}"
    elif "liabilit" in root_type_lower:
        return f"Source of Funds (Liabilities) - {initial}"
    elif "equity" in root_type_lower:
        return f"Equity - {initial}"
    elif "income" in root_type_lower:
        return f"Income - {initial}"
    elif "expense" in root_type_lower:
        return f"Expenses - {initial}"
    else:
        return f"Application of Funds (Assets) - {initial}"

# -------------------- Main Sync --------------------
# Inline strip helper for main loop
def strip_if_str(value):
    return value.strip() if isinstance(value, str) else value

company_integrations = frappe.get_all("Company Sage Integration", fields=["name", "company"])

for integration in company_integrations:
    company_name = integration.company
    try:
        sage = frappe.get_doc("Company Sage Integration", integration.name)
        accounts_url = f"https://pharoh.co.za/api/AccountsSync/get-accounts-for-erpnext?apikey={sage.get_password('api_key')}&lastDate=1970-01-01"
        payload = {"loginName": sage.username, "loginPwd": sage.get_password("password"), "useOAuth": False, "sessionToken": None, "provider": None}
        accounts = frappe.make_post_request(accounts_url, json=payload)

        if not isinstance(accounts, list):
            frappe.log_error(message=f"Unexpected API response format for {company_name}: {accounts}", title=f"Sage Sync API Error for {company_name}")
            continue

        for batch in chunks(accounts, 50):
            for acc_data in batch:
                acc_name = None  # Initialize to avoid scope issues
                try:
                    # Inline strip logic
                    acc_name_raw = acc_data.get("account_name")
                    acc_name = strip_if_str(acc_name_raw) if acc_name_raw is not None else None
                    
                    root_type_raw = acc_data.get("root_type")
                    root_type = strip_if_str(root_type_raw) if root_type_raw is not None else "Asset"

                    if not acc_name:
                        continue

                    parent_account_name = get_parent_account(root_type, company_name)
                    # Get the full parent account name (doc.name) for the Link field
                    full_parent_account = frappe.db.get_value(
                        "Account",
                        {"account_name": parent_account_name, "company": company_name},
                        "name"
                    )

                    # Skip if parent does not exist
                    if not full_parent_account:
                        frappe.log_error(
                            message=f"Parent account {parent_account_name} missing for {company_name}",
                            title=f"Sage Sync Parent Missing for {company_name}"
                        )
                        continue

                    # Check if child account already exists
                    if not frappe.db.exists("Account", {"account_name": acc_name, "company": company_name}):
                        acc_doc = frappe.get_doc({
                            "doctype": "Account",
                            "account_name": acc_name,
                            "company": company_name,
                            "parent_account": full_parent_account,  # Use full doc.name
                            "is_group": 0  # Default to ledger (0); set to 1 if group from data
                        })
                        acc_doc.insert(ignore_permissions=True)

                except Exception as inner_e:
                    frappe.log_error(message=str(inner_e), title=f"Error processing {acc_name or 'unknown'} [{company_name}]")

    except Exception as e:
        frappe.log_error(message=str(e), title=f"Sage Account Sync Fatal Error for {company_name}")