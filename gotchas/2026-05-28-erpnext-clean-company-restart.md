# Clean "zero-history" company restart in ERPNext v15 — new company beats wiping the old one

**Date:** 2026-05-28
**Site:** `Syncflo_internal_V16` (nesterp, Frappe Cloud private bench)
**Context:** Tenant "never went live" on `Syncflo (Pty) Ltd` (test junk: 38 SIs, 27 payments, 286 GL, etc.). Wanted a clean 1-June start — zero books, **CRM/customer history kept**.

## TL;DR — what to do next time

For a "never-went-live, want clean books, keep CRM" restart, **create a NEW company and move the leads to it.** Do NOT try to wipe the existing company unless its setup is precious — wiping fights ERPNext's ledger-link guards and the Transaction Deletion Record (TDR) UX for an hour. A new company is zero-books by definition; customers/contacts/communications are shared site-wide and need no migration.

## Key facts that drove every decision

- **In one ERPNext site, only `Lead` and `Opportunity` carry a `company` tag.** `Customer`, `Contact`, `Address`, `Communication`, `ToDo`, `Comment` are **site-wide, not company-scoped** — they survive any company-level deletion untouched. So "keep the CRM" only ever means "protect the Leads."
- A brand-new Company starts with its own zeroed Chart of Accounts. Create it with **"Create Chart of Accounts Based On = Existing Company"** to clone the old layout (new abbreviation required — can't reuse the old one).
- Set the new company as default: **Global Defaults → Default Company** (via MCP: update the `Global Defaults` single doctype).

## The walls we hit (so you can skip them)

1. **Cancelled invoices won't delete — by design.** `frappe.client.delete` / UI delete refuse with `LinkExistsError: ... linked with GL Entry`. Same for the company delete, which is blocked by `GL Entry`, `Payment Ledger Entry`, **`Advance Payment Ledger Entry`**, etc. Only the TDR's force-SQL clears them.

2. **`delete_company_transactions` module is gone** in v15 — `erpnext.setup.doctype.company.delete_company_transactions...` → `No module named`. It's now the **Transaction Deletion Record** (TDR) doctype.

3. **TDR's "Delete Leads and Addresses" step deletes `Lead WHERE company = <the company>`.** On this site all 199 leads were tagged to the company → a vanilla TDR submit would have wiped the CRM. **Protect leads first** (see below). If 0 leads are on the company, the step shows `Skipped`.

4. **Creating + submitting a TDR via the API is a trap.** `frappe.client.submit({doctype:"Transaction Deletion Record", company:...})` submits with an **empty `doctypes_to_delete`** → fails: `No DocTypes in To Delete list. Please generate or import the list before submitting.` And if you hand-populate `doctypes_to_delete` rows via the API, they carry **`document_count = 0`** (read-only, normally computed by Generate) → the run reports **"Completed" but deletes nothing** (hollow success). The populate method **`populate_doctypes_table` is NOT `@frappe.whitelist()`**, so you can't trigger it via `run_doc_method` either (`not whitelisted`).
   - **Therefore the TDR must be run from the desk UI**: New → set Company → **Save as draft** (the Generate/Add-row UI only appears on a draft, not on a submitted record) → populate the "DocTypes To Delete" table → Submit. On this build there was no working "Generate" button; the user added rows manually (DocType + **Company Field = `company`**) and Save computed the counts.

5. **Lead bulk-edit blocked by a mandatory field.** Moving leads via list **Bulk Edit** died after 33 rows: `MandatoryError: ... utm_source (Source)`. Source was forced mandatory by two Property Setters (`Lead-source-reqd`, `Lead-utm_source-reqd`, both `reqd=1`). **Temporarily set them to `value=0`, do the bulk edits, then restore to `1`.**

## The recipe that worked (new-company pivot)

1. **Create new company** `Syncflo Pty Ltd` (abbr `SYN`), CoA based on existing company, ZAR/South Africa. Set as Global Default.
2. **Relax** `Lead-source-reqd` + `Lead-utm_source-reqd` → `value=0`.
3. **Bulk-edit all leads** to the new company (List → filter Company → Select all → Edit → Company = new). ~All 199 move once Source isn't mandatory.
4. **Restore** the two Property Setters → `value=1`.
5. (Optional, to delete the old company) Clear the old company's transactions with a **UI TDR**: add rows for every company-linked doctype that has records — on this site: **GL Entry, Payment Ledger Entry, Advance Payment Ledger Entry, Sales Invoice, Purchase Invoice, Payment Entry, Journal Entry, Sales Order, Purchase Order** — each with Company Field = `company`. Save (counts populate) → Submit. Then delete the company; if it names another linked doctype, add that and re-run (it converges).
   - **Easy to miss:** `Payment Ledger Entry` (an obscure row) — left 136 rows behind on the first pass and would have blocked the company delete.

## Verifying lead safety at each step (MCP)

`frappe.client.get_count Lead` (total must stay constant) + per-company counts. The whole job hinges on **total Lead count never dropping**. `DefaultValue` and `DocField` are permission-locked to the MCP connector — read company defaults via `Global Defaults` and field config via the parent doctype meta instead.

## Related

- `gotchas/2026-05-28-nest-home-tile-needs-layout-not-just-library.md` (same session, different topic).
- Playbook candidate: if we do another tenant go-live restart, promote this into `playbooks/erpnext-clean-restart.md`.
