# Gotcha: a Customer/Supplier can only be assigned to a LEAF group, never a group node

**Date:** 2026-05-14
**Project:** erpnext_sbca (Sage customer/supplier category sync)
**Status:** Confirmed live

## The Gotcha

ERPNext's `Customer Group` and `Supplier Group` are nested-set trees. A
`Customer` / `Supplier` record can only point at a **leaf** group
(`is_group = 0`). Assigning one to a group *node* (`is_group = 1`) — including
the tree root, "All Customer Groups" / "All Supplier Groups" — fails validation
with `Cannot select a Group type ...`.

This bites when syncing an external system's categories into ERPNext groups:

1. The external system (here, Sage) sends a category NAME per record. When a
   record has no category, the wrapper may default it to the root group name
   ("All Supplier Groups") — which is a node, not a leaf. Assigning it throws,
   and (if the loop catches per-record) that record is silently SKIPPED.
2. If you create groups from the external category list, they must be created
   as leaves (`is_group = 0`) under the root — not as nodes.

The old erpnext_sbca code did `supplier_group = sageGroup or "All Supplier
Groups"` and assigned it raw — so unknown categories threw and the
"All Supplier Groups" fallback was itself invalid. Suppliers were quietly lost.

## The Fix

A create-if-missing resolver that always returns a valid LEAF, or `None` so the
caller can fall back to its own default leaf (see
`erpnext_sbca/API/helper_function.py :: ensure_party_group`):

```python
def ensure_party_group(group_doctype, group_name):  # "Customer Group" / "Supplier Group"
    name = group_name.strip() if isinstance(group_name, str) else group_name
    if not name:
        return None
    if frappe.db.exists(group_doctype, name):
        # leaf -> use it; group node -> return None so caller falls back
        is_group = frappe.db.get_value(group_doctype, name, "is_group")
        return None if is_group else name
    # create as a leaf under the doctype's root group
    snake = group_doctype.lower().replace(" ", "_")        # customer_group
    parent_field = "parent_" + snake                       # parent_customer_group
    name_field = snake + "_name"                            # customer_group_name
    root = frappe.db.get_value(group_doctype,
        {"is_group": 1, parent_field: ["in", ["", None]]},
        "name", order_by="creation asc")
    doc = frappe.get_doc({"doctype": group_doctype, name_field: name,
        parent_field: root, "is_group": 0})
    doc.insert(ignore_permissions=True)
    return doc.name
```

Caller pattern: `group = ensure_party_group("Customer Group", sage_cat) or _default_leaf_group()`.

The `parent_<snake>` / `<snake>_name` field-name derivation works for both
Customer Group and Supplier Group — and the same leaf-vs-node rule applies to
Territory and Item Group, any ERPNext nested-set group tree.

## See also

- `projects/erpnext_sbca/ASSESSMENT.md` — the customer/supplier category sync.
- `erpnext_sbca/API/helper_function.py` — `ensure_party_group` as shipped.
