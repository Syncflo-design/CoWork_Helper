# Sage credit-note Server Script rolls back every POS Closing that contains a return

**Date:** 2026-07-20 · **Site:** ardmoreceramics.c.frappe.cloud · **Area:** Sage bridge / POS Closing

## Symptom

Submitting a POS Closing Entry fails with:

```
POS Closing Failed
Sage Sync Failed: Original invoice ACC-SINV-2026-000XX has no Sage Order ID. Please sync it first.
```

The referenced invoice doesn't exist afterwards — it was created mid-transaction
and rolled back. Any day that includes a POS refund cannot be closed.

## Cause

Two After-Submit Server Scripts on Sales Invoice were asymmetric:

- `post-taxinvoice-to-sage` **skips** `is_pos` invoices ("POS invoice - skipping
  Tax Invoice sync") — so consolidated invoices never get a `custom_sage_order_id`.
- `post-customerreturn-to-sage` ran on **every** `is_return` invoice with no POS
  skip. During consolidation it loads the just-created consolidated original,
  finds no Sage Order ID (guaranteed, see above), and `frappe.throw`s — which
  rolls back the whole closing.

## Fix (applied 2026-07-20)

Added the mirror guard at the top of `post-customerreturn-to-sage`:

```python
if doc.get("is_return") and doc.get("is_pos"):
    frappe.msgprint("POS credit note - skipping Sage Customer Return sync ...")
elif doc.get("is_return"):
    ... original body unchanged ...
```

Verified: closing POS-CLO-2026-00039 (contained 2 sales + 2 returns) submitted
cleanly; messages show sale AND return sides both skipping Sage for POS docs.
Standalone (non-POS) credit notes still sync to Sage exactly as before.

## Access gotchas hit on the way

1. Server Script edits need the **Script Manager** role — System Manager alone
   gets `This action is only allowed for Script Manager`.
2. Adding the role directly to the user silently no-ops when the user has a
   **Role Profile** (profile overwrites roles on save). Add the role to the Role
   Profile instead (added Script Manager to profile `System Admin`).

## Watch out

When two integration hooks form a pair (out + back / sale + return), any skip
condition MUST exist on both sides — an asymmetric guard turns into a rollback
bomb in whatever transaction submits both doc types together (POS Closing,
bulk imports, amendments).
