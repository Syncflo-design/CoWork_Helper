# Wipe a company's transactions (clean books, keep CRM) — the SIMPLE way

**Russell's rule (2026-05-28):** when he asks to clear/zero a company's books, **do NOT improvise per-document deletes or piecemeal TDRs.** Front-load the work:

1. **Search first** — one batched count across every company-scoped transaction doctype for that company.
2. **Hand over the complete non-zero list** in one message.
3. He adds them all to a **Transaction Deletion Record → "DocTypes To Delete"** (manual Add row; Company Field = `company` for each), Save (counts populate), **Submit**. One pass.

Spending 10 minutes building the full list up front beats an hour of circling. **He likes simple — give the one move, not options.**

## Why the shortcuts don't work (don't retry these)

- `frappe.client.delete` / UI delete on cancelled vouchers → `LinkExistsError` (GL Entry / Payment Ledger Entry / Advance Payment Ledger Entry guards). Dead end.
- Submitting a TDR via the **API** → empty `doctypes_to_delete` (`No DocTypes in To Delete list`); hand-filled rows carry `document_count=0` → "Completed" but **deletes nothing**; `populate_doctypes_table` is **not whitelisted**. So the TDR MUST be driven from the desk UI (draft → populate the table → submit).
- Deleting the **Company** is blocked the same way until its ledger rows are gone (run the TDR first).

## Step 1 — the batched "what needs deleting" query (MCP)

`frappe.client.get_count` for each candidate, filtered `{"company": "<COMPANY>"}`. Report the **non-zero** ones as the to-delete list. (DocField is permission-locked on the connector, so we can't auto-enumerate Company-link fields — use this curated candidate list instead.)

**Accounts / ledgers (almost always the bulk):**
`GL Entry`, `Payment Ledger Entry`, `Advance Payment Ledger Entry`, `Journal Entry`, `Payment Entry`, `Sales Invoice`, `Purchase Invoice`, `POS Invoice`, `POS Closing Entry`, `Bank Transaction`, `Dunning`, `Period Closing Voucher`, `Payment Request`

**Selling / Buying:**
`Quotation`, `Sales Order`, `Purchase Order`, `Delivery Note`, `Purchase Receipt`, `Supplier Quotation`, `Blanket Order`

**Stock:**
`Stock Ledger Entry`, `Stock Entry`, `Stock Reconciliation`, `Material Request`, `Pick List`, `Landed Cost Voucher`, `Repost Item Valuation`

**Assets / Mfg / Projects (if used):**
`Asset`, `Asset Movement`, `Asset Repair`, `Work Order`, `Job Card`, `Expense Claim`, `Timesheet`

**KEEP — do NOT add these (masters + CRM):**
`Account`, `Cost Center`, `Warehouse`, `Customer`, `Supplier`, `Item`, `Item Default`, tax templates, `Letter Head`, `Mode of Payment`, `BOM`, and — for a "keep the CRM" wipe — **`Lead`** and **`Opportunity`** (the only company-tagged CRM doctypes).

> ⚠️ Easy to miss: **`Payment Ledger Entry`** (left 136 orphan rows behind once — orphan PLE can show phantom customer balances) and **`Advance Payment Ledger Entry`**. Always include all three ledgers when present.

## Step 2 — the TDR run (desk UI)

New **Transaction Deletion Record** → Company → **Save as draft** (the populate/Add-row UI only shows on a draft) → add one row per non-zero doctype, **Company Field = `company`** → Save (confirm Document Count populated, not 0) → **Submit** → Status: Completed.

## Step 3 — verify (MCP)

Re-count the same list → all **0**. If keeping the CRM, confirm total `Lead` count is unchanged. Then the Company can be deleted if desired (it won't be blocked once ledgers are 0).

## If the CRM (Leads) must survive a FULL company wipe

Either run the TDR with Lead/Opportunity simply **not in the list** (they won't be touched), or if deleting the whole company, **park the leads on another company first** (bulk edit; relax `Lead-source-reqd`/`Lead-utm_source-reqd` to 0 if Source is mandatory, then restore). The TDR's "Delete Leads and Addresses" step only deletes `Lead WHERE company = <the company>`.

See `gotchas/2026-05-28-erpnext-clean-company-restart.md` for the full war story.
