# Payment Reconciliation — Architecture Decision

**Date:** 2026-05-13 (design) / 2026-05-14 (built & deployed)
**Status:** Built. The architecture decision below stands as written; the
implementation diverged on a few mechanical points — see **As Built** next.

## As Built (2026-05-14)

What actually shipped, and where it differs from the original design notes:

- **Cadence is a daily job, not a monthly poll.** `run_reconciliation` is
  registered on `scheduler_events["daily"]`. The *effect* is still one journal
  per party per month — the `Sage Reconciliation Log` idempotent guard is keyed
  on `{company, party, period (YYYY-MM)}`, so each party is reconciled at most
  once per calendar month. The first balance drift in a month is corrected
  within ~24h; later drift that month waits for the next month.
- **`last_reconciliation_sync` lives on the Erpnext Sbca Settings doc, not the
  child row.** It is a single shared timestamp (one opening date per run,
  across all companies), advanced only when every company processed cleanly.
- **The "Sage Payments Clearing" account is auto-provisioned.** If it does not
  exist on a company it is created as a leaf under that company's Asset root
  (`_ensure_clearing_account`). Party control accounts also fall back to the
  company's first Receivable / Payable account when the company defaults are
  unset. No manual chart-of-accounts prep is required.
- **The Sage report returns transaction detail; Pharoh strips it.** Sage's
  `CustomerTransactionListing` / `SupplierTransactionListing` report returns a
  per-party summary header (`OpeningBalance` / `ClosingBalance` already on it)
  PLUS a long nested `Transactions[]` array. Pharoh drops `Transactions[]` and
  returns only `{ sageId, name, openingBalance, closingBalance }`. ERPNext
  matches `sageId` -> `custom_sage_customer_id` / `custom_sage_supplier_id`,
  with the display name as a fallback, and uses `closingBalance` for the delta.
- **Feedback-loop guard.** Reconciliation journals carry a `SAGE-RECON-` cheque
  reference; `journal_entry.py`'s push hook skips them so they are never pushed
  back to Sage. See `gotchas/2026-05-14-custom-app-hook-feedback-loop.md`.
- **Gated by `push_reconciliation_on_schedule`** on Erpnext Sbca Settings —
  defaults OFF until Pharoh's ReconciliationSync endpoints are live.

## Decision

Do not replicate individual payment transactions from Sage into ERPNext.
Instead, pull customer/supplier statement balances from Sage and use them
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

### The Sage data pull

Pharoh wraps `CustomerTransactionListing` /
`SupplierTransactionListing` (the `...ReportingDetail` report) behind
`POST /api/ReconciliationSync/get-customer-balances` and
`get-supplier-balances`. ERPNext sends `{ credentials, openingDate,
closingDate }`; Pharoh sends Sage the full ten-field report request body and
returns a cleaned per-party list `{ sageId, name, openingBalance,
closingBalance }` — only the parties with movement in the period.

```
openingDate = last_reconciliation_sync on the Erpnext Sbca Settings doc
closingDate = now() at the time the job runs
```

On the first run `last_reconciliation_sync` is blank, so the opening date
falls back to the start of the current financial year.

### Per-entity processing

For each customer/supplier returned:

1. **Match** — resolve the Sage party to an ERPNext Customer/Supplier via
   `sageId` -> `custom_sage_customer_id` / `custom_sage_supplier_id`, falling
   back to the display name. No ERPNext match -> skip.

2. **Delta computation** — Sage `closingBalance` vs ERPNext outstanding for
   the same party. If delta = 0, skip (no journal needed).

3. **Reconciliation journal** — if delta != 0, create and submit a Journal
   Entry in ERPNext:
   - Sales side: DR Sage Payments Clearing / CR Accounts Receivable
   - Purchase side: DR Accounts Payable / CR Sage Payments Clearing
   - (lines reverse automatically when the delta runs the other way)
   - Reference: `SAGE-RECON-{company_abbr}-{party}-{YYYY-MM}`

4. **Idempotent guard** — check `Sage Reconciliation Log` before creating.
   If a `Created` journal for this company/party/period already exists, skip.
   Safe to re-run.

5. **Timestamp update** — after a fully successful run (every company clean),
   write `now()` back to `last_reconciliation_sync` on the Erpnext Sbca
   Settings doc (one shared timestamp).

### Clearing account

"Sage Payments Clearing" per company — auto-provisioned as a leaf account
under the company's Asset root on first run. Always nets to zero when Sage and
ERPNext are in sync. No bank account detail needed in ERPNext.

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
- Provide real-time payment status (monthly per-party cadence)
- Handle intercompany eliminations (separate design required when needed)

## Invoices Captured Directly in Sage (Bypassing ERPNext)

This scenario is handled cleanly by the architecture:

**Financial side — automatically reconciled.**
The statement pull sees the full Sage closing balance regardless of where the
invoice was captured. The reconciliation journal aligns ERPNext's AR/AP to
match Sage. Revenue and expense accounts align at month end. No manual
intervention required.

**Stock side — not reconciled (by design).**
If a sales or purchase invoice for physical goods is captured in Sage directly,
ERPNext's stock ledger has no record of the movement. Stock quantities in
ERPNext will be incorrect for those items.

**The process rule this requires:**
> Anything involving physical stock must originate in ERPNext.
> Pure service invoices captured directly in Sage are fine.

This is a clean, enforceable boundary:
- Service invoice in Sage only -> financial impact reconciled monthly, no stock impact, no problem
- Stock item transaction -> must go through ERPNext first, then pushes to Sage

This rule covers every scenario without additional system logic. Accounts
always align. Stock integrity is maintained by process discipline on the
one category (physical goods) where it matters.

## Setup (as built — most of this is now automatic)

1. `last_reconciliation_sync` (Datetime, blank = first run) and the
   `push_reconciliation_on_schedule` toggle are on the **Erpnext Sbca
   Settings** doc — added by the build, applied on `bench migrate`.
2. The "Sage Payments Clearing" account is **auto-provisioned** per company on
   the first run — no manual creation needed.
3. Opening date for the first run falls back to the financial year start
   automatically; involve the accountant only if a different start point is
   wanted on a site with existing history.
4. Pharoh's `ReconciliationSync/get-customer-balances` and
   `get-supplier-balances` endpoints must be deployed; the toggle stays OFF
   until they are.

## Files (built 2026-05-14)

- `erpnext_sbca/API/reconciliation.py` — the daily worker.
- `erpnext_sbca/erpnext_sbca/doctype/sage_reconciliation_log/` — the
  `Sage Reconciliation Log` DocType (one row per company/party/period;
  balances, delta, journal, status; also the idempotent guard).
- `erpnext_sbca_settings.json` — `push_reconciliation_on_schedule` toggle +
  `last_reconciliation_sync` timestamp.
- `erpnext_sbca/hooks.py` — `run_reconciliation` on `scheduler_events["daily"]`.
- `erpnext_sbca/API/journal_entry.py` — `SAGE-RECON-` feedback-loop guard.
- Pharoh: a `ReconciliationSync` controller with `get-customer-balances` /
  `get-supplier-balances` (built & tested separately by Russell).
- `Pharoh_Reconciliation_Endpoint_Prompt.txt` — the Copilot prompt (rev 2,
  corrected to the real transaction-listing shape).
- `Sage_ERPNext_Accounting_Sync_Guide.docx` — accountant-facing guide.
