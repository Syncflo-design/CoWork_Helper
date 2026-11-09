# Till lines of the POS Profile's second-warehouse item group sell from that warehouse
# (Russell, 2 Nov 2026: Hyde Park sells fabric held at JHB Atrium Home). Runs before ERPNext
# validates, so stock, the ledger and returns all use it; set_pos_fields only fills empty rows.
if doc.get("is_pos") and doc.get("pos_profile"):
    cfg = frappe.db.get_value("POS Profile", doc.pos_profile,
        ["custom_second_warehouse", "custom_second_warehouse_item_group"], as_dict=True)
    if cfg and cfg.custom_second_warehouse and cfg.custom_second_warehouse_item_group:
        for row in doc.items:
            group = row.get("item_group") or frappe.db.get_value("Item", row.item_code, "item_group")
            if group == cfg.custom_second_warehouse_item_group:
                row.warehouse = cfg.custom_second_warehouse
