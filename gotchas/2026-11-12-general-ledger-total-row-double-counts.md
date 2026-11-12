# General Ledger report: the bottom "Total" row double-counts on nesterp

**Date:** 2026-11-12
**Domain:** ERPNext v16 General Ledger report / customer statements
**Severity:** annoying (wrong totals on anything printed from the report)

## Symptom

A customer statement printed from the General Ledger shows inflated totals. For Praxis Financial Services,
October 2026, the bottom row read Debit 29,050 / Credit 17,430 / Balance 17,430. The real figures are an
opening balance of 5,810, period debits of 5,810, period credits of 5,810 and a closing balance of 5,810.

## Cause

The `General Ledger` Report record on nesterp has `add_total_row = 1`. The report already returns its own
`'Opening'`, `'Total'` and `'Closing (Opening + Total)'` rows. The added total row sums every row,
including those three, so opening and closing get counted again.

## Fix

Don't build statements on the General Ledger report. `custom_subscription/statement.py` reads `GL Entry`
directly (party_type Customer, is_cancelled 0, opening = before the period or is_opening Yes) and works out
closing = opening + debits - credits. The standard Report record was left alone, because the next migrate
may resync it.

## Why this is non-obvious

The report's own Opening, Total and Closing rows are correct. Only the extra row at the very bottom is
wrong, and it looks like the grand total.
