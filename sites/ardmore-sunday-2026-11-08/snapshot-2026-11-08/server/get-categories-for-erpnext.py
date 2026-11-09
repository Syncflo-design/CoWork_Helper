sage = frappe.get_doc("Sage Integration")

apikey = sage.get_password("api_key")
loginName = sage.username
loginPwd = sage.get_password("password")
sync_start = frappe.utils.nowdate()
lastDate = sage.custom_last_category_sync or "1970-01-01"
url = f"https://pharoh.co.za/api/ItemCategorySync/get-categories-for-erpnext?apikey={apikey}&lastDate={lastDate}"

payload = {
    "loginName": loginName,
    "loginPwd": loginPwd , "useOAuth": False, "sessionToken": None, "provider": None
}

# Send POST request to Pharoh API
items = frappe.make_post_request(url, json=payload)

for item_group_data in items:
    # Get item group name
    item_group_name = item_group_data.get("item_group_mame")
    if not item_group_name:
        continue

    # Check if item group exists, create if it doesn't
    if frappe.db.exists("Item Group", item_group_name):
        group_doc = frappe.get_doc("Item Group", item_group_name)
    else:
        group_doc = frappe.new_doc("Item Group")
        group_doc.item_group_name = item_group_name

    # Update item group fields
    group_doc.parent_item_group = item_group_data.get("parent_item_group")
    group_doc.is_group = item_group_data.get("is_group", 0)

    group_doc.save(ignore_permissions=True)

# Final commit only once after all item groups are processed
frappe.db.commit()

frappe.db.set_single_value("Sage Integration", "custom_last_category_sync", sync_start)