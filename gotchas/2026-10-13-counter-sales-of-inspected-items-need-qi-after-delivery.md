# Counter / till sales of inspected items need "Allow to Make Quality Inspection after Purchase / Delivery"

**Date:** 2026-10-13
**Domain:** ERPNext v16 / POS / Sales Invoice with update stock
**Severity:** annoying

## Symptom

A till sale (Sales Invoice, update stock) of a pack with **Inspection Required before Delivery**
is refused on submit: `Row #1: Quality Inspection is required for Item ...`.

## Cause

`stock_controller.validate_inspection` treats a Sales Invoice with update stock like a Delivery
Note. A till has no step at which to take a delivery inspection, so it can never pass. The only
switch is Stock Settings → `allow_to_make_quality_inspection_after_purchase_or_delivery`: when it
is on, the whole check returns early for Purchase Receipt / Invoice, Sales Invoice and Delivery Note.

## Fix

Stock Settings → **Allow to Make Quality Inspection after Purchase / Delivery** = 1. Set by the
fuse_water_chemical 0.1.5 loader; documented in fuse_counter's README. The batch's production
inspection stays the quality record.

## Why this is non-obvious

The setting's name reads as "you may also inspect later", not "the check is skipped". And it is
site-wide: it relaxes delivery notes too.

## See also

- ERPNext v16 `erpnext/controllers/stock_controller.py` `validate_inspection`.
