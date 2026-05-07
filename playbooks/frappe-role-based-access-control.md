# Frappe Role-Based Access Control — Custom Role Provisioning

**Domain:** Frappe MCP / Permissions / User Management
**First applied:** 2026-05-07 — nesterp / presales@syncflo.co.za
**Reusable for:** Every Frappe instance where you need per-user DocType restrictions

---

## Security requirement (non-negotiable)

> **No backdoors.** A blocked DocType must be unreachable by every path — Ctrl+K search, direct URL (`/app/doctype-name`), REST API, links inside other documents, reports. "Hidden from sidebar" is not a security boundary. Only the absence of any role permission is.

Frappe permissions are **additive**. If a user has five roles and even ONE of them grants read on a DocType, the user can reach it. This means:

- Removing access from the *new custom role* is not enough if a *remaining standard role* still grants it.
- Every standard role the user keeps (Sales User, Purchase User, Stock User, etc.) must be audited against the blocked list.
- Where a standard role bleeds into blocked territory, that role must either be replaced with a restricted custom equivalent or the offending DocType permissions must be surgically removed.

**The audit step is mandatory for every user before their permissions are considered complete.** See "Security audit checklist" below.

---

## Standing workflow — how Russell commissions a new role

This is a **recurring task**. Russell will describe a job role and its responsibilities in plain language. The AI should:

1. **Map the description to ERPNext modules and DocTypes.** Think: what does this person create, approve, read? What are they explicitly NOT responsible for?
2. **Identify the closest standard ERPNext roles** that cover their needs (Sales User, Purchase User, Accounts User, Stock User, etc.).
3. **Pull the Custom DocPerm records for those standard roles** on the target site (they differ per instance — always check live).
4. **Propose a blocked list** — everything outside their job description. Confirm with Russell before creating.
5. **Create the custom role** and all Custom DocPerm records per Steps 4–6 below.
6. **Assign to the user(s)** by updating their roles child table.
7. **Document the new role** in the reference table at the bottom of this playbook and in `sites/<site>.md`.

**Key inputs Russell provides:**
- Role name (e.g. "Warehouse Operator", "Sales Manager")
- Job responsibilities in plain English
- Which site/instance (determines which standard roles and custom perms to audit)
- User email(s) to assign

**Do not start creating until the blocked list is confirmed.** Access removal is the whole point — wrong assumptions waste a rollback.

---

## The principle

Frappe permissions are **additive and role-based only**. There is no per-user DocType deny. The only way to truly block a DocType from a user — including from search (Ctrl+K) — is:

> Remove every role that grants access to that DocType, and ensure no remaining role has it.

Hiding workspace shortcuts is cosmetic only. Real access lives in roles → DocPerm records.

---

## When to use this playbook

- A user needs access to *some* of what a standard ERPNext role provides, but not all.
- You want DocTypes gone from search, not just from the sidebar.
- You're onboarding a new user type across multiple sites with consistent access rights.

---

## Step-by-step process

### 1. Audit the user's current roles

```
frappe_list("User", filters=[["name","=","user@email"]], fields=["name","roles"])
frappe_get("User", "user@email")  # full doc with roles child table
```

Note every role they have. Identify which roles are standard (e.g. `Accounts User`, `Sales User`) and which are custom.

### 2. Pull custom permissions for each role you plan to replace

```
frappe_list("Custom DocPerm",
  filters=[["role","=","Role Name"]],
  fields=["parent","role","read","write","create","delete","submit","cancel","permlevel"])
```

Do this for **every role you intend to replace**. Standard roles have both built-in DocType JSON permissions (invisible via API) and Custom DocPerm overrides (visible via API). You will carry over the custom ones; the built-in standard ones will NOT transfer automatically to the new role — which is the desired behaviour for restricted roles.

### 3. Identify blocked DocTypes

List the DocTypes the user must NOT access. These fall into two categories:

- **In Custom DocPerm** — don't copy these records to the new role.
- **In standard DocType JSON** — automatically blocked because the new role won't have any record for them. No action needed.

### 4. Create the new role

```
frappe_create("Role", {
  "role_name": "New Role Name",
  "desk_access": 1,
  "is_custom": 1
})
```

### 5. Create Custom DocPerm records for the new role

For each DocType the user **should** access, create a record:

```
frappe_create("Custom DocPerm", {
  "parent": "DocType Name",
  "parenttype": "DocType",
  "parentfield": "permissions",
  "role": "New Role Name",
  "read": 1,
  "write": 1,   # only if needed
  "create": 1,  # only if needed
  "delete": 0,
  "submit": 0,
  "cancel": 0,
  "permlevel": 0
})
```

Repeat for each DocType. If a DocType has multiple permission levels (e.g. Timesheet has permlevel 0 and 1), create one record per level.

**Source of truth for what to include:**
- All Custom DocPerm records from the replaced roles (minus blocked DocTypes)
- Any standard DocType perms you know the user needs that aren't in Custom DocPerm (e.g. `Payment Entry` for an accounting role)

### 6. Update the user's roles

Send the complete new roles array — Frappe replaces the child table wholesale:

```
frappe_update("User", "user@email", {
  "roles": [
    {"role": "Role One"},
    {"role": "Role Two"},
    {"role": "New Role Name"}
    # omit the replaced roles
  ]
})
```

### 7. Have the user hard-refresh

Frappe caches permissions in the session. The user must reload or log out/in for changes to take effect.

### 8. Security audit — remaining standard roles (MANDATORY)

After assigning the new custom role, audit every standard role the user still holds. For each one:

```
frappe_list("Custom DocPerm",
  filters=[["role","=","Sales User"]],   # repeat for each remaining role
  fields=["parent","read","write","create","delete","submit","cancel"])
```

Cross-reference each result against the blocked DocType list. If ANY remaining role grants access to a blocked DocType, you must either:

a) **Replace that role** with a custom restricted equivalent (same process as above), or
b) **Add a Custom DocPerm** for that role on that DocType with all permissions set to 0 — but note this is unreliable in Frappe (additive system; zero-permission records are not guaranteed to override). Option (a) is always safer.

**Do not mark a user's permissions as complete until this audit passes cleanly for every role they hold.**

### 9. Smoke test

Log in as (or ask) the user to:
- Search (Ctrl+K) for a blocked DocType — should return nothing
- Navigate directly to `/app/budget`, `/app/tax-category` etc. — should get a Permission Error
- Verify they can still access everything they need

---

## Security audit checklist

For each user, tick off before sign-off:

- [ ] Custom role created with only required DocTypes
- [ ] Original replaced roles removed from user
- [ ] All remaining standard roles audited against blocked list
- [ ] No standard role bleeds into blocked territory
- [ ] Ctrl+K search test passed for each blocked DocType
- [ ] Direct URL navigation test passed for each blocked DocType
- [ ] User can access all required DocTypes without errors
- [ ] Session refreshed (user logged out/in)

---

## DocType permission levels

| permlevel | Meaning |
|---|---|
| 0 | Standard fields |
| 1+ | Fields with `permlevel` set — typically sensitive fields (e.g. salary amounts) |

Always check the original role's records for multiple permlevels on the same DocType.

---

## Gotchas

- **Standard DocType permissions are invisible via API.** You can only see Custom DocPerm records. This means if a role has standard perms (baked into ERPNext), they won't show up in your audit. The new role starts with zero — which is what you want for a restricted role.
- **Additive only — no deny.** If the user has ANY role that grants read on a DocType, they can see it. Make sure you remove the original role, not just add the new one.
- **Search respects permissions.** Once the role is removed and the new role has no perm for the DocType, it disappears from Ctrl+K search. No extra steps needed.
- **Block modules is a different layer.** `block_modules` on the User doc hides entire workspaces from the sidebar. This is separate from DocType permissions and sits on top of them. Keep block_modules in sync with the new role's actual access.
- **Frappe Cloud MCP user can't read Company/DocField/Account directly.** Use Purchase Taxes and Charges Template etc. to cross-reference. See `gotchas/2026-05-06-mcp-user-restricted-doctypes.md`.

---

## Reuse pattern for new sites

When onboarding a user with the same role type on a different instance:

1. Check that instance's Custom DocPerm for the standard roles (they may differ site-to-site).
2. Create the same role name (e.g. `Presales User`) for consistency.
3. Run through Steps 4–7 above.
4. The blocked DocType list is a business decision — confirm with Russell per site.

---

## Presales User — reference implementation (nesterp, 2026-05-07)

**v2 — Pure whitelist build (2026-05-07 evening)**

All standard ERPNext roles removed. Lyndsay holds only: `Workspace Manager`, `Presales User`.
No standard role bleeds possible — any new ERPNext update cannot add access silently.
FCRM unblocked in sidebar (she does CRM work).

**v1 notes (superseded):** Earlier in the day, `Pre_Sales` and `Accounts User` were replaced but Sales User, Stock User, Item Manager, Purchase User were retained. v2 removes all four.

---

**Granted via Custom DocPerm (48 records):**

### CRM

| DocType | R | W | C | D | S | X |
|---|---|---|---|---|---|---|
| Lead | ✓ | ✓ | ✓ | ✓ | | |
| Opportunity | ✓ | ✓ | ✓ | ✓ | | |
| Prospect | ✓ | ✓ | ✓ | ✓ | | |
| Contact | ✓ | ✓ | ✓ | ✓ | | |
| Address | ✓ | ✓ | ✓ | ✓ | | |
| Customer | ✓ | ✓ | ✓ | ✓ | | |
| Customer Group | ✓ | | | | | |
| CRM Campaign | ✓ | ✓ | ✓ | ✓ | | |
| Lead Source | ✓ | | | | | |
| Territory | ✓ | | | | | |
| Industry Type | ✓ | | | | | |

### Items & Masters

| DocType | R | W | C | D | S | X |
|---|---|---|---|---|---|---|
| Item | ✓ | ✓ | ✓ | ✓ | | |
| Item Group | ✓ | | | | | |
| Item Price | ✓ | ✓ | ✓ | ✓ | | |
| Brand | ✓ | ✓ | ✓ | | | |
| UOM | ✓ | | | | | |
| Price List | ✓ | | | | | |
| Warehouse | ✓ | | | | | |

### Suppliers

| DocType | R | W | C | D | S | X |
|---|---|---|---|---|---|---|
| Supplier | ✓ | ✓ | ✓ | ✓ | | |
| Supplier Group | ✓ | | | | | |

### Sales & Invoicing

| DocType | R | W | C | D | S | X |
|---|---|---|---|---|---|---|
| Quotation | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Sales Order | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Sales Invoice | ✓ | ✓ | ✓ | | ✓ | |
| Sales Taxes and Charges Template | ✓ | | | | | |
| Terms and Conditions | ✓ | ✓ | ✓ | ✓ | | |
| Payment Terms Template | ✓ | ✓ | ✓ | ✓ | | |

### Purchases & Payments

| DocType | R | W | C | D | S | X |
|---|---|---|---|---|---|---|
| Purchase Invoice | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Purchase Taxes and Charges Template | ✓ | | | | | |
| Payment Entry | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Mode of Payment | ✓ | | | | | |
| Journal Entry | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### Subscriptions

| DocType | R | W | C | D | S | X |
|---|---|---|---|---|---|---|
| Business Subscription | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Subscription Plan | ✓ | | | | | |

### Tasks & Communication

| DocType | R | W | C | D | S | X |
|---|---|---|---|---|---|---|
| ToDo | ✓ | ✓ | ✓ | ✓ | | |
| Note | ✓ | ✓ | ✓ | ✓ | | |
| Communication | ✓ | ✓ | ✓ | ✓ | | |
| Timesheet (pl0) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Timesheet (pl1) | ✓ | ✓ | | | | |

### Helpdesk

| DocType | R | W | C | D | S | X |
|---|---|---|---|---|---|---|
| HD Ticket | ✓ | ✓ | ✓ | | | |
| HD Team | ✓ | | | | | |
| HD Agent | ✓ | | | | | |

### Reference / Read-only

| DocType | R | W | C | D | S | X |
|---|---|---|---|---|---|---|
| Company | ✓ | | | | | |
| Account | ✓ | ✓ | ✓ | ✓ | | |
| Finance Book | ✓ | | | | | |
| Currency | ✓ | | | | | |
| Letter Head | ✓ | | | | | |
| Email Account | ✓ | ✓ | | | | |
| Page | ✓ | | | | | |

*R=read, W=write, C=create, D=delete, S=submit, X=cancel*
