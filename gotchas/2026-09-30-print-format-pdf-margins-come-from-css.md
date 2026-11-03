# Custom Jinja print format + repeating letterhead: page margins come from the `.print-format` CSS rule

**Date:** 2026-09-30
**Domain:** ERPNext / Frappe print formats (nesterp, Print Settings pdf_generator = chrome, repeat_header_footer = 1)
**Severity:** annoying (cost a dozen reprint round-trips)

## Symptom

On nesterp `2026 Quotation` / `2026 Invoice`:
- Margin Left/Right = 25 on the Print Format did nothing; PDF ran edge to edge.
- Letterhead logo covered the DRAFT heading and the first table row, or the logo was cut off the top.
- A blank second page appeared.
- Changing the Print Format's Margin Top field (10 → 15) changed nothing.

## Cause

Frappe copies `margin-*` from the CSS rule whose selector is exactly `.print-format` into the PDF
options; the Print Format margin fields are overridden. The template had
`.print-format { margin-left: 0mm !important; margin-right: 0mm !important; }` → zero side margins.

The repeating letterhead is drawn in the top margin, bottom-aligned to the margin line. Anything in the
header box below the logo (Frappe's default `.print-format .letter-head { margin-bottom: 30px }`, or any
margin you add) spills past the margin line and paints white over the top of the body.
Setting `margin-bottom` in the `.print-format` rule brought the overlap and a blank 2nd page back.

## Fix (verified on the real PDF)

```css
.letter-head { margin-top: 0 !important; padding-left: 12mm; }   /* align logo with body */
.print-format .letter-head { margin-bottom: 0 !important; }      /* nothing spills below the logo */
.invoice-wrapper { padding: 0 12mm; }                            /* side white space */
.print-format { ... margin-top: 34mm; margin-left: 0mm !important; margin-right: 0mm !important; }
/* NO margin-bottom in the .print-format rule */
```
34mm = 80px logo (~21mm) + ~12mm white space above it. Status heading h4 gets `margin: 8px 0 4px 0`.

## Why this is non-obvious

- The margin fields save fine and look authoritative.
- The MCP `download_pdf` result is text-decoded, so the binary is corrupt and can't be inspected.
  **Verify in the user's signed-in Chrome instead:** open
  `/api/method/frappe.utils.print_format.download_pdf?doctype=...&name=...&format=...&no_letterhead=0`
  (Chrome renders it inline) and screenshot. Patch the format from that tab with
  `frappe.xcall('frappe.client.set_value', ...)` string replacements. Small payloads, fast iteration.
- Don't reason about the header/margin interaction on paper. Test each change on the real PDF.

## See also

- Line Amount must use `item.amount`, not `item.net_amount`, when a document-level Discount row is
  printed (net_amount already has the discount spread in, so it double-counts).
