# Till returns never reached Sage, and a failed sale was never retried

**Date:** 2026-09-29 · **Site:** ardmoreceramics.c.frappe.cloud · **Area:** Sage bridge (Pharoh) / POS · **Severity:** stock and accounts drift silently

## Symptoms

1. A return done on the till never appeared in Sage, yet the return document showed
   **Sage Sync Status = Synced** with a Sage invoice number on it.
2. A sale that failed to reach Sage (Sage down, item not mapped) stayed `Failed` for ever.
   Nothing tried again.

## Causes

- `post-customerreturn-to-sage` began with `if is_return and is_pos: pass`. It was written
  for the old day-end consolidated credit note. In Sales Invoice POS mode that document
  no longer exists, so till returns went nowhere.
- The "Synced" on the return was a **copy**. ERPNext copies custom fields from the sale
  onto the return unless the field is `no_copy`. The return carried the SALE's Sage order
  id and document number.
- The old return script used the single `Sage Integration` login, the customer's own Sage
  id and `Item.custom_sage_selection_id`, none of which match how sales are posted.
- There was simply no retry job.

## What is in place now

| Piece | What it does |
|---|---|
| `post-customerreturn-to-sage` (rewritten) | Posts every return, till or back-office, the moment it is submitted. Mirrors `post-taxinvoice-to-sage`: per-company `Company Sage Integration`, `Sage Item Selection`, Sage POS customer, soft-fail for till documents, the TEST-only lock with its second guard. Refers back to the original sale's Sage invoice. |
| `post-taxinvoice-to-sage` (updated) | Records the reason and attempt count on failure. Skips quietly when already Synced. |
| `retry-failed-sage-sync` (Scheduler, cron `7-59/15 * * * *`) | Picks up `Failed` documents dated from 2026-09-21, max 8 attempts, 15 per run, sales before returns, and runs the SAME posting script via `server_script.execute_doc(inv)`. One posting routine, one lock. |
| `ardmore-send-invoice-to-sage` (API) + Client Script `Sales Invoice - Send to Sage` | Button on the desk form for `Failed` / `Check Sage` documents. |
| Custom Fields on Sales Invoice | `custom_sage_sync_error` (why), `custom_sage_sync_attempts` (how many). The three existing Sage fields are now `no_copy = 1`. |
| Custom Field on Company Sage Integration | `custom_sage_pos_sales_rep_id`. TEST = 740886. |

### Statuses

- **Synced**: in Sage.
- **Failed**: Sage refused it or we never sent it. Retried automatically.
- **Check Sage**: the connection dropped AFTER sending (timeout, connection aborted). Sage
  may have it. Never retried automatically, because a resend could create a duplicate.
  A person looks in Sage for the reference, then uses Send to Sage.

## Things that bit on the way

- **Sage refuses a customer return without a sales representative** ("Sales Representative
  is Required"). Sales invoices do not need one. Rep ids belong to ONE Sage company, so the
  id is held per company on Company Sage Integration, not taken from Sales Person.
- **The Pharoh API key is in the request URL**, so any HTTP error message contains it. The
  first failed test wrote the key into `custom_sage_sync_error` on the invoice. Both
  scripts now do `str(http_err).replace(str(apikey), "***")`. Frappe's own
  `make_post_request` still logs the full URL to Error Log on failure; that is core
  behaviour and visible to System Managers only.
- **The Error Log used to receive the whole payload, login password included.** Both
  scripts now log only the invoice or return part.
- `frappe.has_permission` does not exist inside a Server Script
  (`module has no attribute 'has_permission'`). Use `doc.has_permission("write")`.
- One Server Script CAN run another: `frappe.get_doc("Server Script", name).execute_doc(doc)`.
  That is what keeps the retry from becoming a second copy of the posting logic.
- A newly created API Server Script answers "Failed to get method for command ..." until it
  has been saved a second time.
- To run a scheduler Server Script on demand:
  `frappe.core.doctype.scheduled_job_type.scheduled_job_type.execute_event` with
  `doc = {"doctype": "Scheduled Job Type", "name": <name>}`. Find the name by filtering
  Scheduled Job Type on `server_script`.

## Proof (all against the Sage TESTING company)

- ACC-SINV-2026-00055, a real till return from 24 Sept that had never been sent: reset,
  then sent with the button's API. Sage **CRN0000003**.
- ACC-SINV-2026-00061, a return done on the till in the browser against
  ACC-SINV-2026-00060: posted by itself on submit. Sage **CRN0000004**. Sage fields were
  NOT copied from the sale. Closed in POS-CLO-2026-00078.
- **Sage stock followed.** After the next quantity sync (16:38) Sage's on-hand figure,
  stamped on `Item.custom_quantity_on_hand`, read BN189JUL26 19 -> **20** and CUSHCCD50
  **20**, matching POS Store - ACT. Main Distribution stayed 0 and no reconciliation was
  raised. Note the check has to be made on that field: Main Distribution is clamped at 0,
  so it looks the same whether or not the return reached Sage.
- Retry job run on demand: ACC-SINV-2026-00049 / 00050 (item FABCBBLUE has no TEST id) and
  00051 (its sale is not in Sage) each went to attempt 1 with the reason recorded. They
  will stop at 8.

## Go-live

Add to the unlock list in `2026-09-22-ardmore-uat-sage-test-lock-register.md`:

1. `post-customerreturn-to-sage`: set `SAGE_FORCE_COMPANY = ""` together with the tax
   invoice script. Never one without the other.
2. Fill `custom_sage_pos_sales_rep_id` on Home, Ceramics and Fashion, next to the POS
   customer id. Without it every return fails with a clear message.
3. `retry-failed-sage-sync`: move `START_DATE` to the go-live date so UAT leftovers are
   never posted to a live company.
4. Multi-company sales: the return finds the right Sage invoice per company by rebuilding
   the company order from the original sale's items. Prove it with one mixed-category
   sale and return before relying on it.

## See also

- `gotchas/2026-09-21-pos-sales-never-reached-sage-stock-leak.md`
- `gotchas/2026-09-22-ardmore-uat-sage-test-lock-register.md`
