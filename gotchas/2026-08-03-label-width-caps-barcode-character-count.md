# A 40mm label at 203 dpi holds a 9-character barcode — audit item code lengths BEFORE promising barcode printing

**Date:** 2026-08-03
**Domain:** ERPNext / retail / Zebra label printing
**Severity:** day-killer if discovered after committing to a design

## Symptom

Ardmore asked to print barcodes from ERPNext to a Zebra ZD230 on their existing
40 x 20mm 2-up labels, encoding the item code. Everything about the request sounds
trivial — until you check whether the data physically fits.

It doesn't. Of 6,404 enabled stock items, **only 1,059 (17%)** had a code that fits a
40mm label with readable bars, and 553 codes were the entire product description:

```
Furniture - Thanda Nest Midnight Velvet, Square Ottoman (Cube) with Brass Plated Feet
Napkin - Cheetah Kings Jade (50x50)
```

## Cause

Physics, not software. Code128 width is fixed by the data:

```
modules = 11 x (characters + 2) + 13        # start + data + checksum at 11 each, stop is 13
```

A ZD230 is **203 dpi = 8 dots/mm**, so a 40mm label is 320 dots. Add a standard 10-module
quiet zone each side. At a 2-dot module (0.25mm — the smallest most retail scanners are
specified for):

```
2 x (11n + 35) + 40 <= 320   ->   n <= 9.5   ->   9 characters
```

Dropping to a 1-dot module (0.125mm / 5 mil) buys ~24 characters but is below normal
scanner spec — it may read, and may fail intermittently at the till, which is worse.

Useful rule of thumb at 203 dpi: **label width needed ≈ 2.75mm per character + 14mm.**

| Label width | Characters |
|---|---|
| 40mm (theirs) | 9 |
| 45mm | 11 |
| 48mm | 12 |
| 50mm | 13 |
| 70mm | 20 |

Second constraint: the ZD230 images a **maximum 104mm** across. Two-up therefore caps at
about 48mm per label (48 + 4 gap + 48 = 100mm). Beyond that you go 1-up and halve the roll.

## Fix

**Do not print the item code.** Generate a short internal number instead, and print that:

- new `Item.custom_pos_barcode`, an 8-digit sequential number (`10000001`...)
- written to the standard **Item Barcode** child table as well — that is the row the POS
  scan resolves against, and it was empty on every item
- Sage never sees it; it is a POS-only identifier

An 8-digit numeric code fits the **existing 40 x 20mm stock** at a full 0.25mm module with
comfortable quiet zones — and Code128 auto-switches to subset C for all-digit data, making
it narrower still. No renaming, no new label stock, works for all 6,404 items including the
35-character description-as-code ones.

## Why this is non-obvious

- **"Can we print barcodes?" sounds like a software question.** It is a media question.
  The answer is determined by printer dpi and label width before any code is written.
- **A long barcode still prints.** Nothing errors. The bars just get thinner until
  scanners start failing intermittently — the worst possible failure mode, at the till,
  in front of a customer.
- The obvious remedy — "tell the client to shorten their item codes" — meant renumbering
  5,345 of 6,404 items. Generating a parallel internal number costs nothing and touches
  no existing data. **Reach for the second identifier, not the rename.**
- Check the printer's *print* width, not its media width. The ZD230 takes 108mm of media
  but only images 104mm; the difference lands exactly on the outer quiet zones.

## See also

- `sites/ardmore.md` — 2026-08-03 work log (generator, backfill, Item List print button)
- `gotchas/2026-08-03-frappe-child-row-insert-bypasses-parent-validation.md`
- Server Script `ardmore_barcode_label_zpl` on ardmoreceramics.c.frappe.cloud
