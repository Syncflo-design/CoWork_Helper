# Enabling an hourly Server Script runs it immediately; Phone fields refuse numbers without a country code

**Date:** 2026-10-21  **Site:** ardmoreceramics.c.frappe.cloud (Frappe 16.51)

## What happened

1. Rewrote a disabled daily Server Script (`get-customers-for-erpnext-new`) as an **Hourly**
   Scheduler Event and enabled it at 17:43. Its Scheduled Job Type had `next_execution` in
   the past, so the scheduler ran it at 17:44 - at the same moment I triggered it by hand
   through a temp API script (`execute_scheduled_method()`), whose MCP call then timed out
   at 120 s while the request kept running on the server. Two copies ran at once:
   `Duplicate entry 'X' for key 'PRIMARY'` on inserts and `has been modified after you have
   opened it` on saves, 153 errors in one pass.
2. The script wrote Sage telephone numbers into a **Phone** fieldtype (`custom_phone`):
   `Please select a country code for field custom_phone` / `... is not a valid Phone Number`.
   Free text like `082 116 669 / 0828946317` or `031 123 4567` is refused.
3. Sage email fields often hold `a@x.com;b@y.com` -> `is not a valid Email Address`.
4. After fixing 2 and 3 the SAME errors kept coming for existing customers: Paul's 2025 sync
   had stored the raw Sage text in `email_id`, `mobile_no` and `custom_phone`, and
   `doc.save()` re-validates every field, not just the ones you changed. Any record that
   was inserted with bad data cannot be saved until you clean those fields in the same save.
5. Still failing after that: `Customer.email_id` and `mobile_no` are **fetch_from the primary
   Contact**, so on save Frappe copies the Contact's raw `a@x;b@y` back over the cleaned value
   and the Email validation fails again. Clean (and save) the primary Contact first - its
   `email_id`, `mobile_no`, `phone` and the `email_ids` / `phone_nos` child rows.

## Fix / rule

- **Never run a Scheduler Event script by API call.** Enqueue it on the worker instead:
  `frappe.core.doctype.scheduled_job_type.scheduled_job_type.execute_event` with
  `doc` = the Scheduled Job Type as a JSON string (name, method, server_script, frequency,
  stopped, create_log). Returns at once; the job runs in the long queue.
- Expect a newly enabled scheduler script to fire straight away. Enable it, then leave it.
- A paged sync with a saved cursor does NOT revisit customers that errored on an earlier
  page until the next full pass - after fixing the script, reset the cursor to 0.
- Phone fieldtype: normalise first (digits only; `0xxxxxxxxx` -> `+27xxxxxxxxx`; keep `+..`;
  anything else -> blank). Email: take the first token containing `@` and `.`.
- Sandbox has no `re`; write the digit filter as a loop.

6. (27 Oct) A Scheduler Event script that switches itself off with
   `frappe.db.set_value("Server Script", name, "disabled", 1)` keeps running: the flag is
   only read when the Server Script is SAVED (on_update syncs the Scheduled Job Type).
   The customer cleanup ran every 2 minutes for a day logging "finished". Also set
   `stopped = 1` on the Scheduled Job Type (frappe.db.set_value works for that one, the
   scheduler reads it directly).

## Related

- `sites/ardmore.md` 2026-10-21 (Account Sales + customer sync).
- Memory: `frappe_server_script_sandbox.md`.
