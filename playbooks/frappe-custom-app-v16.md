# Frappe v16 — scaffolding a custom app from scratch

Reference build: `projects/quick_purchase_invoice/`. This playbook captures the file layout, the pyproject.toml shape, and the small set of conventions that bite if you guess them.

## When to use this

Any time you need a new Frappe v16 app (DocTypes, server logic, UI hooks) that you'll deploy to Frappe Cloud via the Bench → "Add App from GitHub" flow.

## File layout (minimum viable)

```
<app_name>/                              ← repo root, what GitHub sees
├── pyproject.toml                       ← v16 uses PEP 621, no setup.py
├── README.md
├── license.txt
├── .gitignore
└── <app_name>/                          ← Python package, same name as repo
    ├── __init__.py                      ← __version__ = "0.0.1"
    ├── hooks.py                         ← app metadata + extension points
    ├── modules.txt                      ← one module name per line
    ├── patches.txt                      ← `[pre_model_sync]` / `[post_model_sync]` headers
    ├── public/
    │   ├── css/<file>.css
    │   └── js/<file>.js
    ├── templates/                       ← optional Jinja
    ├── www/                             ← optional public web pages
    └── <module_name>/                   ← snake_case of the module name
        ├── __init__.py
        └── doctype/
            ├── __init__.py
            └── <doctype_snake_case>/
                ├── __init__.py
                ├── <doctype_snake_case>.json
                ├── <doctype_snake_case>.py
                └── <doctype_snake_case>.js   ← form script (parent doctypes only)
```

## `patches.txt` — REQUIRES both section headers

```ini
[pre_model_sync]
# patches that run BEFORE DocType sync (e.g. doctype renames). Example:
# <app_name>.patches.v1_2.rename_some_doctype

[post_model_sync]
# patches that run AFTER DocType sync (data migrations, defaults, etc.)
```

**Both headers must be present**, even if one section is empty. An empty file is also fine (no patches at all). A file with only ONE of the two sections crashes `bench migrate` with `ValidationError: Patch type PatchType.post_model_sync not found in patches.txt` — and Frappe Cloud's auto-Recovery hides this so the site looks stuck in an Update Available loop. See `gotchas/2026-05-08-frappe-patches-txt-needs-both-section-headers.md`.

## `pyproject.toml` (Frappe v16, flit_core)

```toml
[project]
name = "<app_name>"
authors = [{ name = "Syncflo", email = "ops@syncflo.co.za" }]
description = "..."
requires-python = ">=3.10"
readme = "README.md"
dynamic = ["version"]
dependencies = []

[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"

[tool.flit.module]
name = "<app_name>"
```

`dynamic = ["version"]` makes flit read `__version__` from `<app_name>/__init__.py`. **Do not** add a `setup.py` — v16 errors on it.

## `hooks.py` minimum

```python
app_name        = "<app_name>"
app_title       = "<App Title>"
app_publisher   = "Syncflo"
app_description = "..."
app_email       = "ops@syncflo.co.za"
app_license     = "MIT"

# Optional: bundle CSS/JS for desk
# app_include_css = "/assets/<app_name>/css/foo.css"
# app_include_js  = "/assets/<app_name>/js/foo.js"
```

## `modules.txt`

One module name per line, in the human form (e.g. `Quick Purchase Invoice`). The folder under `<app_name>/<module_snake>/` must match the snake_case form. Frappe v16 figures this out automatically; just keep the case + spelling consistent.

## DocType JSON shape (essentials)

```json
{
 "doctype": "DocType",
 "name": "<DocType Name>",
 "module": "<Module Name>",
 "engine": "InnoDB",
 "autoname": "naming_series:",      // or "field:fieldname", or "hash"
 "is_submittable": 1,                // submittable doc with docstatus 0/1/2
 "track_changes": 1,
 "field_order": [ "...", "..." ],    // explicit ordering, must match `fields[].fieldname`
 "fields": [
   { "fieldname": "...", "fieldtype": "...", "label": "...", "reqd": 1, ... }
 ],
 "permissions": [
   { "role": "Accounts User", "read": 1, "write": 1, "create": 1, "submit": 1, ... }
 ],
 "sort_field": "modified",
 "sort_order": "DESC"
}
```

Key fields per `fields[]` entry:
- `fieldname` (snake_case, unique within the DocType)
- `fieldtype` (Data, Date, Float, Currency, Link, Dynamic Link, Select, Table, Section Break, Column Break, Small Text, ...)
- `options` — depends on `fieldtype`. For Link, the target DocType. For Dynamic Link, the **fieldname** of a Link-to-DocType column on the same row. For Select, newline-separated values. For Currency, optionally a fieldname holding the currency code.
- `reqd`, `read_only`, `hidden`, `in_list_view`, `in_standard_filter`
- `default` — string value; for `Date` use `"Today"`.
- `depends_on` — JS-eval expression like `"eval:doc.entry_type=='Account'"`.
- `fetch_from` — like `"supplier.supplier_name"`, auto-fills from a linked doc.

## Child DocType (table) particulars

```json
{
  "doctype": "DocType",
  "istable": 1,
  "editable_grid": 1,
  "module": "<Module Name>",
  ...
}
```

`istable: 1` is the only flag that distinguishes a child table from a regular DocType. Reference it from the parent via a `Table` field with `options: "<Child DocType Name>"`.

## Form script wiring

Parent: `<doctype>.js` next to the JSON, top-level events:

```js
frappe.ui.form.on("<DocType>", {
    refresh(frm) { ... },
    onload(frm)  { ... },
    <fieldname>(frm) { ... },     // value change
});
```

Child rows: separate `frappe.ui.form.on("<Child DocType>", { ... })` block in the same file, with handlers like `<fieldname>(frm, cdt, cdn)` and `items_add(frm, cdt, cdn)`.

## Whitelisted methods

Put `@frappe.whitelist()` functions in `<app_name>/api.py` (or any module). Call from JS via:

```js
frappe.call({
    method: "<app_name>.api.<func_name>",
    args: { ... },
});
```

## Permissions on a DocType

In the JSON `permissions[]` array, each entry is a role + a set of capability flags. Use ERPNext's standard role names where possible (`Accounts User`, `Accounts Manager`, `Stock User`, ...). If you need a brand-new role, ship it as a Fixture (out of scope for this playbook).

## Deploy to Frappe Cloud

1. Push the repo to GitHub.
2. Bench → Apps → Add App → from GitHub → branch `main`.
3. Wait for green build.
4. Bench → Deploy.
5. Sites → `<site>` → Apps → Install → pick the new app.

Updating: `git push` → Bench → Apps → Update on that app's row → Deploy.

## Known patterns / pitfalls

- **Dynamic Link in a grid**: see `gotchas/2026-05-06-frappe-dynamic-link-in-grid.md`.
- **Blank-item Purchase Invoice rows**: see `gotchas/2026-05-06-erpnext-purchase-invoice-blank-item-row.md`.
- **MCP user perms on Frappe Cloud**: see `gotchas/2026-05-06-mcp-user-restricted-doctypes.md`.
