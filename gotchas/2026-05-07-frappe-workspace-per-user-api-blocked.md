# Frappe API blocks admins from creating per-user workspace overrides for other users

**Date:** 2026-05-07
**Domain:** Frappe MCP / Workspace
**Severity:** annoying

## Symptom

Trying to hide a specific workspace for a specific user without affecting all users.
`frappe.client.insert` returns:

```
frappe.exceptions.ValidationError: Name is required
```

`frappe.desk.doctype.workspace.workspace.new_page` returns:

```
frappe.exceptions.PermissionError: Cannot create private workspace of other users
```

## Cause

Two separate blockers:

1. **`frappe.client.insert` ignores the `name` field** for the `Workspace` doctype because its `autoname` is `field:title`. When `title = "Financial Reports"` a workspace with that name already exists, so insert fails at the uniqueness check before the name we supplied is even evaluated.

2. **`new_page` has an explicit permission guard** — it checks `frappe.session.user == for_user` and raises `PermissionError` if an admin tries to create a private workspace owned by someone else, even with System Manager role.

## Fix

**No server-side API path exists for this.** The options in order of effort:

1. **Quickest — log in as the target user, use the desk UI:** Click ⋮ next to the workspace in the sidebar → Hide. Frappe creates the per-user override record itself. Takes 10 seconds.

2. **Role-based restriction on the public workspace** — add a role (e.g. "Accounts Manager") to the `Workspace.roles` child table via `frappe_update`. Only users with that role see the workspace. Affects all users, not just one.

3. **Block the whole module** — add the module to the user's `block_modules` list. Only viable if ALL workspaces under that module should be hidden (e.g. blocking "Accounts" hides both Financial Reports AND Invoicing — usually too blunt).

## Why this is non-obvious

The `Workspace` doctype looks like any other doctype so you'd expect `frappe.client.insert` with `for_user` set to work. The two blockers are unrelated — the insert fails for a naming reason before even reaching the permission check, which made it look like a naming issue initially. Switching to `new_page` revealed the actual permission guard.

The per-user workspace model in Frappe is designed for end-users to customise their own desk; there is no admin-on-behalf-of-user path in the API.

## See also

- `gotchas/2026-05-07-frappe-v16-modern-desk-click-interception.md` — related: other Frappe desk API limitations
- Frappe source: `frappe/desk/doctype/workspace/workspace.py` → `new_page()`
