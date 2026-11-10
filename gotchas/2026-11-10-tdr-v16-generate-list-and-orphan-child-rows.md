# TDR on v16: use "Generate To Delete List", then clean up orphan child rows it leaves behind

**Date:** 2026-11-10
**Domain:** ERPNext v16 (comstruct, ERPNext 16.36 / Frappe 16.35)
**Severity:** annoying

## Symptom

Wiping Com-struct South Africa for a training restart:

1. `erpnext.setup.demo.clear_demo_data` failed and rolled back:
   ```
   Cannot delete or cancel because Supplier Summit Traders Ltd. is linked with Purchase Order PUR-ORD-2026-00011
   Failed to erase demo data, please delete the demo company manually.
   ```
2. After the main-company TDR completed (it deleted Project too), deleting the old site
   users and site warehouses was blocked, and `delete_items` returned their names as failed.

## Cause

1. A real-company PO used a demo-company supplier. `clear_demo_data` deletes the demo
   masters, so it cannot run while any other company's transaction points at them.
2. The TDR deletes the parent rows of `Project` but **not** the rows of a custom child table on
   Project (`Project Site` from nest_project_sites). Its "Child DocTypes" column only listed
   `Project User`. The orphan rows still held Link fields (`site_store_warehouse`, `site_manager`),
   and `check_if_doc_is_linked` treats an orphan child row as a live link.

## Fix

Order that worked, all in one sitting:

1. Desk: new **Transaction Deletion Record**, pick the company, Save (draft).
2. Click **Generate To Delete List** (v16 button). It fills every company-linked doctype with a
   count, and the Excluded table already keeps Account, Cost Center, Warehouse, tax templates,
   POS Profile, BOM, Company, Mode of Payment, Item Default, Customer, Supplier and others.
3. Click **Remove Zero Counts**, review the rows that are left, Save, Submit, Yes.
4. Then `erpnext.setup.demo.clear_demo_data` (MCP) succeeds.
5. Orphan child rows: `frappe.desk.reportview.delete_items` with `doctype="Project Site"` and
   the row names (from `frappe.client.get_list`, `parent_doctype="Project"`). It works as
   Administrator even though the parent is gone. `frappe.client.delete` / `set_value` do NOT
   work on these rows, because both load the parent first.
6. Then masters delete normally via `delete_items` (more than 10 names = background job; re-count
   to confirm). Also delete the Contacts left behind by deleted users (`user` is null).

## Why this is non-obvious

The playbook (`playbooks/erpnext-wipe-company-transactions.md`) says to add rows by hand after a
batched count. On v16 the Generate button does that more completely: it also caught Bin, Project
and Process Deferred Accounting, which the curated count list missed. The orphan child rows give
no error of their own. They only surface later as "can't delete user/warehouse".

## See also

- Playbook: `playbooks/erpnext-wipe-company-transactions.md` (pre-v16 manual-row method)
