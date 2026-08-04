# Deploying a Frappe app overwrites live DocType permissions with the app JSON

**Date:** 2026-05-20
**Domain:** Frappe / ERPNext / custom-app / Frappe Cloud
**Severity:** day-killer (silently breaks integrations/users mid-project)

## Symptom

A connector/API user (or a staff role) that could read/write an app-owned DocType
yesterday suddenly can't, right after a Deploy + migrate:

```
PermissionError: User hello@syncflo.co.za does not have doctype access via
role permission for document Business Subscription
```

Nothing about the user changed. The only change was pushing an updated app and
deploying it. Roles that had been added through the desk UI (Role Permission
Manager / Customize Form) are simply gone from the DocType's permission list.

## Cause

For a DocType that is **owned by an app** (`custom: 0`, shipped in the app's
`*.json`), the `permissions` array in that JSON is the source of truth. `bench
migrate` re-imports the DocType on every deploy and **replaces** the live
permission rows with exactly what's in the JSON. Any role row added later via the
UI is not in the JSON, so it gets wiped.

In this case the app JSON only listed `System Manager`. We edited it to
`System Manager + Accounts Manager + Accounts User` and deployed — which reset the
live permissions to those three and dropped the role the MCP connector user had
been relying on.

## Fix

Two safe patterns:

1. **Grant access via a role that is already in the app JSON** — change the *user's*
   roles, not the DocType's permissions. User role assignments are not touched by
   migrate. (We added `Accounts Manager` to the connector user, since that role is
   in the JSON.)
2. **If a role must have DocType access, put it in the app JSON** so it's restored
   on every deploy instead of wiped.

```diff
# business_subscription.json -> "permissions"
  { "role": "System Manager", ... },
+ { "role": "Accounts Manager", "submit": 1, "cancel": 1, "amend": 1, "delete": 1, ... },
+ { "role": "Accounts User",   "submit": 1, ... }
```

Do **not** rely on permissions added through the desk UI for an app-owned DocType —
they won't survive the next deploy.

## Why this is non-obvious

The break is delayed and disconnected from its cause: you edit *code/permissions*,
deploy hours later, and a *different* user/integration starts failing. The error
("does not have doctype access") reads like the user was misconfigured, sending you
to check User → Roles — when the real cause is that migrate reset the DocType's
permission table to the app JSON. Reflex is to assume `migrate` only touches schema;
it also reimports DocPerms.

Rule of thumb: the app JSON's `permissions` block is the *complete* allow-list for an
app-owned DocType after every deploy. Anything not in it is gone.

## See also

- App: https://github.com/Syncflo-design/custom-subscription
- Related gotchas: `gotchas/2026-05-06-mcp-user-restricted-doctypes.md`,
  `gotchas/2026-05-06-frappe-cloud-update-vs-deploy-assets.md`
- Related playbook: `playbooks/frappe-role-based-access-control.md`
