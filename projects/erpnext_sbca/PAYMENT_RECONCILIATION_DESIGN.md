# Payment Reconciliation — Architecture Decision

**Date:** 2026-05-13  
**Status:** Decided — design pending, not yet built

## Decision

Do not replicate individual payment transactions from Sage into ERPNext.  
Instead, pull monthly customer/supplier statements from Sage and use them  
to create a single reconciliation Journal Entry per entity per month that  
brings ERPNext's AR/AP closing balance into line with Sage.

## Why

- Sage payment workflows are complex: receipts can be unallocated, payments  
  can be contra'd, credit notes allocated instead of cash, advance payments  
  sitting as account credits. Replicating at transaction level is a large,  
  fragile build with many edge cases.
- Monthly statement reconciliation is clean, auditable, and sufficient for  
  the intended use cases.
- One journal per customer per month rather than hundreds of individual  
  payment entries.

## What Each System Owns

| Concern | Owner |
|---|---|
| Financial GL, individual transactions | Sage |
| SARS-compliant calculations and submissions | Sage |
| VAT returns, tax periods | Sage |
| Operational data (stock, orders, manufacturing) | ERPNext |
| Month-end AR/AP balances (aligned to Sage) | ERPNext (via reconciliation journals) |
| Management reporting | ERPNext (on aligned data) |
| Consolidated multi-entity reporting | ERPNext (on aligned data) |

## How It Works

1. **Scheduled monthly pull** — Pharoh endpoint returns customer and supplier  
   statements per entity (closing balance, ageing buckets, transaction list  
   for the period).

2. **Delta computation** — compare Sage closing balance to ERPNext closing  
   balance for the same customer/supplier/period.

3. **Reconciliation journal** — if a delta exists, create and submit a  
   Journal Entry in ERPNext:
   - Sales side: DR Sage Payments Clearing / CR Accounts Receivable  
   - Purchase side: DR Accounts Payable / CR Sage Payments Clearing  
   - Reference: `SAGE-RECON-{company}-{customer}-{YYYY-MM}`

4. **Idempotent** — if the journal for that company/customer/month already  
   exists, skip. Safe to re-run.

5. **Clearing account** — "Sage Payments Clearing" per company. Always nets  
   to zero when Sage and ERPNext are in sync. No bank account detail needed  
   in ERPNext.

## What This Enables

- **Month-end AR/AP in ERPNext matches Sage** — not transaction-for-transaction,  
  but closing balance accurate.
- **Management reporting from ERPNext** — P&L, balance sheet, debtor ageing  
  are accurate enough for internal management use. Not SARS-compliant (that  
  stays in Sage) but accurate for decision-making.
- **Consolidated multi-entity reporting** — multiple companies in one Frappe  
  instance, each with aligned month-end balances. ERPNext's standard  
  consolidation reports work correctly because the underlying data is sound.
- **No double-entry complexity** — users never create payments in ERPNext.  
  Payments happen in Sage only. ERPNext reflects the result monthly.

## What It Does NOT Do

- Replicate individual payment transactions or allocation detail
- Replace Sage for SARS submissions, VAT, or any statutory reporting
- Provide real-time payment status (monthly cadence only)
- Handle intercompany eliminations (separate design required when needed)

## Invoices Captured Directly in Sage (Bypassing ERPNext)

This scenario is handled cleanly by the architecture:

**Financial side — automatically reconciled.**  
The monthly statement pull sees the full Sage closing balance regardless of  
where the invoice was captured. The reconciliation journal aligns ERPNext's  
AR/AP to match Sage. Revenue and expense accounts align at month end.  
No manual intervention required.

**Stock side — not reconciled (by design).**  
If a sales or purchase invoice for physical goods is captured in Sage directly,  
ERPNext's stock ledger has no record of the movement. Stock quantities in  
ERPNext will be incorrect for those items.

**The process rule this requires:**  
> Anything involving physical stock must originate in ERPNext.  
> Pure service invoices captured directly in Sage are fine.

This is a clean, enforceable boundary:
- Service invoice in Sage only → financial impact reconciled monthly, no stock impact, no problem
- Stock item transaction → must go through ERPNext first, then pushes to Sage

This rule covers every scenario without additional system logic. Accounts  
always align. Stock integrity is maintained by process discipline on the  
one category (physical goods) where it matters.

## Build Prerequisites

Before implementation:
1. Confirm Sage exposes customer/supplier statements with period closing  
   balances via the Sage Business Cloud API.
2. Design the Pharoh endpoint (`get-customer-statements-for-erpnext`,  
   `get-supplier-statements-for-erpnext`).
3. Involve the accountant to define: which accounts, which period boundaries,  
   how to handle the first reconciliation run on a site with existing data.

## Files to Create (when ready to build)

- `erpnext_sbca/API/reconciliation.py`
- Pharoh endpoints (Copilot prompt TBD)
- New DocType: `Sage Reconciliation Log` (one row per company/party/period,  
  tracks journal created, delta, status)
