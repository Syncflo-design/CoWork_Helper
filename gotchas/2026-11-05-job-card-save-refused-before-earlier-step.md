# A later job card can't be saved until the step before it is finished

**Date:** 2026-11-05
**Domain:** ERPNext v16 Job Card
**Severity:** annoying

## Symptom

Saving any job card after the first step of a works order fails, even with nothing completed and
only a date changed:

    OperationSequenceError: As per the sequence of the operations in the work order ...,
    complete the operation Print before the operation Laminate.

The first step's card saves fine, which makes a bulk update look half-broken.

## Cause

`JobCard.validate()` calls `validate_sequence_id()` on every save where the card has a Sequence ID,
not only when a quantity is recorded. So anything that saves a waiting step is refused: a desk edit,
`frappe.client.set_value`, `bulk_update`, or adding a row to the card.

Separately, `before_save` rebuilds `expected_start_date` and `expected_end_date` from the
`scheduled_time_logs` rows, so changing only the header dates doesn't stick.

## Fix

- On screens: work the steps in order. A later step can be saved once the step before it is
  submitted, which marks its Work Order Operation as Completed.
- To move a schedule on waiting steps (demo data, for instance), write the fields directly, on both
  the card and its schedule row. `frappe.db.set_value` from System Console works:

      frappe.db.set_value('Job Card', card, {'expected_start_date': start, 'expected_end_date': end}, update_modified=False)
      frappe.db.set_value('Job Card Scheduled Time', row, {'from_time': start, 'to_time': end}, update_modified=False)

- Work Order `planned_start_date`, `planned_end_date` and `expected_delivery_date` allow changes on
  submit, so a normal save moves those. The Work Order Operation planned times do not.
