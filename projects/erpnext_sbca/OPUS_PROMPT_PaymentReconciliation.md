================================================================================
META-PROMPT FOR CLAUDE OPUS — erpnext_sbca Payment Reconciliation Build
Date: 2026-05-14
Purpose: Build the payment reconciliation feature end-to-end:
         (a) ERPNext custom app changes (Python + DocType + Settings)
         (b) Pharoh .NET endpoint Copilot prompt
================================================================================

You are working on the **erpnext_sbca** custom Frappe app — a Sage ↔ ERPNext
bridge written by Doreen (9t9it). The app lives at:
  C:\ClaudeCode\Erpnext-Sbca\erpnext_sbca\

Before doing anything else, read the following files in order:
  1. C:\ClaudeCode\CoWork_Helper\CLAUDE.md  (session rules + working style)
  2. C:\ClaudeCode\CoWork_Helper\projects\erpnext_sbca\PAYMENT_RECONCILIATION_DESIGN.md  (the full architecture decision)
  3. C:\ClaudeCode\CoWork_Helper\gotchas\2026-05-13-pharoh-copilot-prompt-style.md  (required format for the Pharoh Copilot prompt)
  4. C:\ClaudeCode\CoWork_Helper\projects\erpnext_sbca\Pharoh_StockAdjustment_Endpoint_Prompt.txt  (style reference — a working Copilot prompt)
  5. C:\ClaudeCode\Erpnext-Sbca\erpnext_sbca\API\stock_adjustment.py  (pattern reference — the most recently written Python worker)
  6. C:\ClaudeCode\Erpnext-Sbca\erpnext_sbca\API\cancellation.py     (pattern reference)
  7. C:\ClaudeCode\Erpnext-Sbca\erpnext_sbca\hooks.py                (to see where to add the new scheduled job)
  8. C:\ClaudeCode\Erpnext-Sbca\erpnext_sbca\erpnext_sbca\doctype\erpnext_sbca_settings\erpnext_sbca_settings.json  (to see the existing Settings field layout)

--------------------------------------------------------------------------------
WHAT NEEDS TO BE BUILT
--------------------------------------------------------------------------------

### A. erpnext_sbca Python changes

**1. New file: erpnext_sbca/API/reconciliation.py**

Implement a scheduled reconciliation job that:

a) Reads the `Company Sage Integration` child rows from `Erpnext Sbca Settings`
   (same per-company loop pattern as stock_adjustment.py and cancellation.py).

b) For each company row, check that `push_reconciliation_on_schedule` is enabled
   (new toggle — see Settings below). If not, skip.

c) Call the new Pharoh endpoint:
     POST /api/ReconciliationSync/get-customer-balances
   Payload:
   {
     "credentials": { <standard credentials block from the company row> },
     "openingDate": "<last_reconciliation_sync or financial year start>",
     "closingDate": "<now() as ISO date>"
   }
   This returns a list of customers with opening and closing balances for the
   date range. Only customers with activity in the period are returned.

d) For each customer returned by Sage:
   - Look up the matching ERPNext Customer (by name or custom_sage_customer_id).
   - Get the ERPNext outstanding balance for that customer
     (use frappe.db or the Accounts Receivable report — whichever is simpler).
   - Compute delta = Sage closing balance − ERPNext outstanding.
   - If delta == 0: skip.
   - Check the `Sage Reconciliation Log` DocType for an existing journal for
     this company/customer/period — if found, skip (idempotent).
   - Create and submit a Journal Entry:
       DR  Sage Payments Clearing   (delta amount)
       CR  Accounts Receivable      (delta amount, against the customer)
     Reference: SAGE-RECON-{company_abbr}-{customer}-{YYYY-MM}
     Posting Date: last day of the period (or today if current month).
   - Create a `Sage Reconciliation Log` record to record the run.

e) Repeat steps c–d for suppliers:
     POST /api/ReconciliationSync/get-supplier-balances
   Same logic; journal is reversed:
       DR  Accounts Payable         (delta amount, against the supplier)
       CR  Sage Payments Clearing   (delta amount)

f) After all companies processed successfully, write now() to
   `last_reconciliation_sync` on the Settings doc (a single shared timestamp,
   not per-company, since the opening date is the same for all companies in
   one run).

g) Log all activity at INFO level. On any Pharoh or ERPNext error for a
   specific customer/supplier, log the error and continue — do not abort the
   whole run.

Follow the per-company loop pattern and credential extraction from
stock_adjustment.py exactly. Use `frappe.enqueue` if the dataset could be
large (> ~200 customers), otherwise run inline from the scheduled job.

**2. New DocType: Sage Reconciliation Log**

A simple log DocType (no form needed, just a record). Fields:
- company (Link → Company)
- party_type (Select: Customer / Supplier)
- party (Dynamic Link via party_type)
- period (Data, e.g. "2026-05")
- sage_closing_balance (Currency)
- erpnext_outstanding (Currency)
- delta (Currency)
- journal_entry (Link → Journal Entry)
- status (Select: Created / Skipped / Failed)
- error_message (Small Text)
- reconciliation_date (Date)

Place in module `Erpnext Sbca`. Not submittable. `is_single: 0`.
Follow the existing DocType JSON style in the repo.

**3. Settings changes (erpnext_sbca_settings.json)**

Add two new fields in the main (non-child) Settings section, after the
existing push toggles:

  - `push_reconciliation_on_schedule`  (Check, label "Run Reconciliation Sync",
    default "0")
  - `last_reconciliation_sync`  (Datetime, label "Last Reconciliation Sync",
    read_only 1)

IMPORTANT: The settings JSON has had truncation issues in the past. After
editing, validate the file is valid JSON before saving:
  python3 -c "import json; json.load(open('erpnext_sbca_settings.json'))"

**4. hooks.py — add scheduled job**

Add to `scheduler_events`:
  "daily": [
    "erpnext_sbca.API.reconciliation.run_reconciliation"
  ]

(Daily is fine — this is a balance alignment job, not real-time.)

Also ensure the new DocType is registered if Frappe requires it (usually
automatic from the JSON file, but check if other DocTypes need explicit
registration in hooks.py in this repo).

--------------------------------------------------------------------------------

### B. Pharoh .NET endpoint Copilot prompt

After completing the Python side, produce a complete, self-contained Copilot
prompt for the Pharoh developer to build:
  POST /api/ReconciliationSync/get-customer-balances
  POST /api/ReconciliationSync/get-supplier-balances

**The prompt MUST follow the exact structured format** documented in:
  C:\ClaudeCode\CoWork_Helper\gotchas\2026-05-13-pharoh-copilot-prompt-style.md

Use the StockAdjustment prompt as your style reference:
  C:\ClaudeCode\CoWork_Helper\projects\erpnext_sbca\Pharoh_StockAdjustment_Endpoint_Prompt.txt

Key things the Pharoh prompt must cover:
- Background: Pharoh wraps Sage Business Cloud API; same pattern as existing controllers
- What needs to be built: two new action methods in a new ReconciliationSyncController
- The Sage API call Pharoh makes:
    POST CustomerTransactionListing/GetCustomerTransactionListingReportingDetail
    (with OData date filter for opening/closing date)
  And the equivalent for suppliers.
- The request body Pharoh accepts from ERPNext (credentials + openingDate + closingDate)
- Real example values in the JSON (not "string" placeholders)
- What Pharoh returns to ERPNext: the cleaned list of
    { partyName, sageName, openingBalance, closingBalance }
  for each active customer/supplier in the period
- Field mapping table (camelCase → PascalCase)
- Already done on ERPNext side: the reconciliation.py worker handles the delta
  and journal creation — Pharoh only needs to fetch and return the data
- Your Task: numbered list ending with swagger update

Save the completed prompt to:
  C:\ClaudeCode\CoWork_Helper\projects\erpnext_sbca\Pharoh_Reconciliation_Endpoint_Prompt.txt

--------------------------------------------------------------------------------
WORKING STYLE NOTES
--------------------------------------------------------------------------------

- Edit actual files — do not paste code into chat for Russell to apply.
- Validate JSON after every settings file edit.
- Follow the per-company credential pattern from stock_adjustment.py exactly.
- Short responses unless asked for detail.
- When done, confirm: files created, hooks updated, JSON valid, Pharoh prompt saved.

================================================================================
END OF PROMPT
================================================================================
