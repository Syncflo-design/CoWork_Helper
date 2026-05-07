# Frappe MCP user — restricted DocType reads

**Date:** 2026-05-06
**Bit me on:** Verifying schema assumptions on `nesterp.jh.frappe.cloud` while building `quick_purchase_invoice`.

## Symptom

The Frappe MCP API user (the role used by the `frappe-<site>` connector) does NOT have read permission on:

- `Company` — list returns `[]` and count returns `0`, even though companies exist.
- `DocField` — returns `PermissionError: Insufficient Permission for DocField`.
- Implicitly, `Account` filtered through normal list calls returns `[]` (probably blocked by the User Permission on Company).

But it CAN read:

- `DocType` (the meta records, not their fields)
- `Supplier`, `Item`, `Purchase Invoice Item` (child rows), `Purchase Taxes and Charges Template`
- Most transactional doctypes

## Why this happens

The MCP user is configured as an `API` user (or System Manager with restricted Roles) and User Permissions on Frappe Cloud limit what doctypes are exposed externally. This is by design — you don't want your MCP token to be able to dump full COA / company config.

## Workarounds

1. **For schema introspection**: use `frappe.client.get_value` on `DocType` directly, or load existing transactional records and inspect their shape. Don't rely on `DocField` listing.
2. **For "what companies exist?"**: read from a referencing doctype (e.g. list `Purchase Taxes and Charges Template` with `company` in the fields — those rows reveal company names even when the Company list itself is blocked).
3. **For end-to-end testing of new code**: assume MCP-only verification will be partial. Reserve final smoke testing for after install on the actual bench, where the logged-in user has full perms.

## Don't do

- Don't try to escalate the MCP user's permissions just to verify code locally — the restricted-by-default posture is a security feature. Run integration tests on the bench instead.
- Don't assume an empty `frappe.client.get_list("Company")` means the site has no companies. Cross-check via `frappe.client.get_value("DocType", ...)` or via an unrestricted referencing doctype.
