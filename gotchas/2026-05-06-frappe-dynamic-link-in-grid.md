# Dynamic Link inside a grid — needs a hidden Link-to-DocType helper field per row

**Date:** 2026-05-06
**Bit me on:** `quick_purchase_invoice` — wanted a single grid column ("Item / Account") whose link target switches per row depending on a "Type" Select.

## Symptom

Frappe `Dynamic Link` requires `options` to be the **fieldname** of a Link-to-DocType field. If you try to point its `options` at a `Select` field directly, the link picker breaks (it tries to use the literal Select value as a DocType name and fails).

## Fix

Add a hidden Link-to-DocType helper field on the same row, and sync it from a form script when the visible Select changes.

JSON (child table fields, condensed):

```json
{ "fieldname": "entry_type",   "fieldtype": "Select", "options": "Item\nAccount", "default": "Item" },
{ "fieldname": "link_doctype", "fieldtype": "Link",   "options": "DocType", "hidden": 1, "default": "Item" },
{ "fieldname": "entry_ref",    "fieldtype": "Dynamic Link", "options": "link_doctype" }
```

Form script (parent doctype's `.js`):

```js
frappe.ui.form.on("<Child DocType>", {
    items_add(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.entry_type) row.entry_type = "Item";
        row.link_doctype = row.entry_type;     // keep helper synced
    },
    entry_type(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        row.link_doctype = row.entry_type;     // re-sync on change
        row.entry_ref = null;                  // clear stale value
        frm.refresh_field("items");
    },
});
```

## Why the helper is needed

Dynamic Link reads its target DocType from another field on the **same row** at render time. The Select doesn't qualify because Frappe expects a Link → DocType column there. The helper bridges them. Hide it so the user never sees it.

## Bonus — server-side hardening

Bypass-the-form inserts (REST, scripts) can leave `link_doctype` mismatched. In your Python controller's `validate()`:

```python
self.link_doctype = self.entry_type or "<DefaultDocType>"
```

…so the row is consistent regardless of how it was created.
