# POS Register is empty when POS Settings invoice type is Sales Invoice

**Date:** 2026-10-28
**Domain:** ERPNext v16 POS
**Severity:** annoying

## Symptom

On a site whose POS Settings > Invoice Type is **Sales Invoice** (our standard: Ardmore, the Fuse
demo), till sales post fine and the POS Closing Entry picks them up, but the **POS Register**
report returns no rows for the same profile and day.

## Cause

POS Register reads the **POS Invoice** doctype only. In Sales Invoice mode the till writes Sales
Invoices (`is_pos = 1`, `is_created_using_pos = 1`), so the report has nothing to read.

## Fix

Report till sales from what Sales Invoice mode does fill:

- **POS Closing Entry** (one per till per shift): sales, taxes and the cash-up per Mode of Payment
  (opening, expected, counted, difference). This is the cash-up by terminal.
- **Sales Payment Summary** report with `is_pos = 1`: sales, tax and payments per day and cashier,
  with warehouse (= branch). Its payment-mode column lumps tenders together, so use the closing
  entry for the cash / card / EFT split.
- **Sales Register** for item and customer detail.

Building a till by API: create the Sales Invoice with `is_pos`, `is_created_using_pos = 1` and
`pos_profile`, posted after the opening entry's `period_start_date`, or
`pos_closing_entry.get_invoices(start, end, pos_profile, user)` will not return it.

## Why this is non-obvious

The report's name says POS and it sits in the POS workspace, so an empty result looks like the
sales never posted. They did — check `pos_closing_entry.get_invoices` before chasing the posting.

## See also

- `gotchas/2026-09-21-pos-sales-never-reached-sage-stock-leak.md` (why we run Sales Invoice mode)
