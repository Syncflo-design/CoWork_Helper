# Gotcha: a custom app's scheduled job can trip its own doc_event hooks (feedback loop)

**Date:** 2026-05-14
**Project:** erpnext_sbca
**Status:** Caught in review before it shipped

## The Gotcha

A Frappe custom app that BOTH (a) hooks a doctype's events via `doc_events` AND
(b) programmatically creates documents of that same doctype will trigger its
own hooks on the documents it creates.

In erpnext_sbca: `journal_entry.py` registers a `Journal Entry` `on_submit`
hook that pushes Journal Entries to Sage. The new `reconciliation.py` scheduled
job *creates and submits Journal Entries* (the monthly AR/AP reconciliation
journals). Without a guard, every reconciliation journal — which is DERIVED
FROM Sage's own balance — would be pushed straight back into Sage on submit:
a journal built from Sage's number, posted back to Sage, changing the number
the next run reads. Classic feedback loop.

It is easy to miss because the two pieces live in different files and neither
"knows" about the other — the coupling is implicit, through the shared doctype
and the framework's event dispatch.

## The Fix

Tag the internally-generated documents with a recognisable marker, and have the
push hook skip anything carrying it. erpnext_sbca's reconciliation journals are
created with a `cheque_no` reference of `SAGE-RECON-{company}-{party}-{period}`,
and the push hook bails early:

```python
def post_journal_entry(doc, method):
    if not is_sync_enabled("push_journal_entry_on_submit"):
        return
    # Reconciliation journals are derived FROM Sage balances -- pushing them
    # back would create a feedback loop. They carry a "SAGE-RECON-" reference.
    if (doc.get("cheque_no") or "").startswith("SAGE-RECON-"):
        return
    frappe.enqueue(...)
```

A reference-prefix marker works well because it is visible to a human browsing
the ledger too, not just to code. `doc.flags` does NOT survive — a fresh
`frappe.get_doc` in an enqueued worker won't see flags set on the original
in-request object.

## The General Rule

Whenever a custom app both reacts to a doctype's events and programmatically
creates documents of that doctype, ask: "will my own hook fire on the thing I
just created, and is that what I want?" If not, add a self-recognition guard at
the very top of the hook. Re-audit for this any time you add a new
document-creating scheduled job or method to an app that already has
`doc_events`.

## See also

- `projects/erpnext_sbca/PAYMENT_RECONCILIATION_DESIGN.md` — the reconciliation
  feature whose journals needed the guard.
