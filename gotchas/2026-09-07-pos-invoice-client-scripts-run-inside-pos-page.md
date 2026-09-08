# POS customisations belong in Client Scripts on POS Invoice — they run inside the POS page, and `frappe.ui.form.on` works there

**Date:** 2026-09-07 · **Site:** ardmoreceramics.c.frappe.cloud · **Area:** ERPNext v16 POS · **Severity:** day-saver

## Symptom

Four separate POS complaints from Ardmore retail (Brittany, "ERP Next POS
Suggestions/Changes" PDF, Sept 2026):

1. New-customer "+" opened the quick entry, then **jumped to the full Customer
   form** after Save ("a second page that repeats everything").
2. "Add to mailing list" threw *please add an email address* **even with an
   email typed**.
3. Voucher + card split: the card amount had to be **retyped by hand**; the
   old "POS VoucherNumber" script said *voucher ref required* but **no field
   appeared**, and the value went to a field that does not exist
   (`voucher_reference_no`; the real one is `custom_voucher_ref`).
4. Partial returns: cashiers must **remove the items the customer keeps**,
   which reads backwards, so refunds came out as the wrong line (-R1380
   instead of -R4500).

## Cause

- (1) The "+" called `frappe.new_doc('Customer')`. With no `after_insert`
  callback, `QuickEntryForm.process_after_insert` → `open_form_if_not_list()`
  routes to the Customer form whenever you are not on the Customer list.
  The typed-in-search "Create a new Customer" path goes through
  `frappe._from_link` and does *not* redirect — hence "sometimes".
- (2) The script read the email from `cur_dialog.get_value('custom_email_address')`
  / `email_id`; the v16 Customer quick entry names the field `email_address`
  (mapped to `email_id` only inside `insert()`), so it always read blank.
- (3) ERPNext's `auto_set_remaining_amount` only fills a mode when it is empty
  and the remainder is positive. With `set_grand_total_to_default_mop` the
  card is pre-filled, so typing a voucher amount just overpays.
- (4) `make_sales_return` copies **every** line negated. That is upstream
  design, not a bug.

## Fix — what shipped (all Client Scripts, no deploy)

All on **POS Invoice / Form** except the last. They are evaluated by
`ScriptManager.setup()` when the POS builds its hidden `frappe.ui.form.Form`
("POS Invoice"), i.e. **inside the POS page**, and the POS reuses that one
Form for every invoice, so each script is evaluated once per page load.
`frappe.ui.form.on('Sales Invoice Payment', 'amount')` and
`frappe.ui.form.on('POS Invoice', 'validate')` fire normally because the POS
uses `frappe.model.set_value` and `frm.savesubmit()`.

| Script | What it does |
|---|---|
| `POS Customer UX` (rewritten) | Own `frappe.ui.Dialog` (Name, Mobile, Email, Add to Mailing List) → `frappe.client.insert` → `cur_pos.cart.customer_field.set_value(name)`. Also overrides `frappe.ui.form.make_quick_entry` for Customer on the POS route so the search-box "Create a new Customer" uses the same dialog. Inserting with `email_id`/`mobile_no` still makes the primary Contact (verified). `custom_phone` is deliberately NOT set — it is a **Phone** fieldtype and the server rejects numbers without a country code. |
| `POS Split Payment Autobalance` | On any non-default mode's `amount`: default mode = rounded_total − others, pushed through the POS control (`cur_pos.payment[sanitize_mode_of_payment(mode)+'_control'].set_value()`) so the on-screen figure updates too. Skips returns. |
| `POS Voucher Ref` (replaces `POS VoucherNumber`, now disabled) | Voucher amount > 0 → dialog for the ref → `custom_voucher_ref`; `validate` blocks Complete Order until captured, then re-clicks `.submit-order-btn`. |
| `POS Return Item Picker` | Wraps `cur_pos.make_return_invoice`: after the upstream call, a dialog lists the sold lines with tick + qty (unticked by default). Unticked → `frappe.model.clear_doc(row)`; ticked → `row.qty = -qty`; then `frm.cscript.calculate_taxes_and_totals()`. Refund goes on the mode that carried most of the sale. Cancel → `make_new_invoice()`. Rates are never touched (using `set_value('qty')` would call `apply_pricing_rule` and could re-price a return at today's list price). |
| `POS Closing - Cashier UX` (POS Closing Entry / Form) | Hides taxes; polls the reconciliation rows and pre-fills `closing_amount = expected_amount`; `after_save` → `frm.save('Submit')` (no confirm dialog). |

Receipt: the POS prints `frm.pos_print_format` = POS Profile `print_format` (else the
standard "POS Invoice"). Standard formats cannot be edited on Frappe Cloud, so a custom
`Ardmore POS Receipt` (copy of "POS Invoice with Item Image" + Voucher No + payments
block) is set on every profile. Custom Jinja formats get the same `layout` /
`print_settings` context as standard ones, so the `{% for page in layout %}` template
works unchanged.

Config, same day: **Cash removed from the payment modes of every till**
(Airport, Caversham, Joburg, Cermaics_User2, POS_Test2, Online Store Test; the
online OL_* profiles never had it). The user-less `Test` profile keeps Cash —
saving it with Credit Card fails on *"set default Cash or Bank account in
Mode of Payment Credit Card"* for company Ardmore.

## Why this is non-obvious

- Returns leave payments alone: `calculate_outstanding_amount` returns early
  for `is_return` (only `calculate_paid_amount` runs) and
  `set_default_payment` is gated on `total > 0`. So after trimming return
  lines the copied -full-amount payments stay and **submit fails** with
  *Total payments amount can't be greater than …* unless you rewrite them.
- The Page-doc route for POS JS is dead (see 2026-07-20 gotcha); Client
  Scripts on POS Invoice are the supported, no-deploy home — but guard with a
  `window.__flag` so a second `Form('POS Invoice')` (e.g. opening a POS
  Invoice in the desk) does not double-register handlers.
- `frm.save('Submit')` submits without the *Permanently submit?* prompt;
  `frm.savesubmit()` is the one that asks.

## See also

- `gotchas/2026-07-20-frappe-pos-page-custom-script-breaks-returns.md`
- `gotchas/2026-07-20-sage-return-script-blocks-pos-closing.md`
- `sites/ardmore.md` work log 2026-09-07
