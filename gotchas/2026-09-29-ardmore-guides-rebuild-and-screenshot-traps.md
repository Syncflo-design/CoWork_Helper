# Ardmore training guides: sources were lost, and how to rebuild them

**Date:** 2026-09-29
**Domain:** Ardmore ERPNext / documentation / Claude in Chrome
**Severity:** annoying (half a day to rebuild what should have been a text edit)

## Symptom

Russell asked for the documentation to be updated after the 29 Sept till changes. The two
illustrated guides (`Ardmore Store Stock & POS Guide.docx`, `Ardmore Getting Stock In
Guide.docx`) were no longer anywhere on the machine, and neither were their generators or
their 28 screenshots.

## Cause

In July the generators (`build_doc.js`, `build_stockin.js`) and the screenshots were kept
in the **session scratchpad** under `%TEMP%\claude\...`. That folder was cleaned on
5 August. The .docx files in `C:\ClaudeCode` were later moved or deleted.

## Fix

Everything now lives in **`C:\ClaudeCode\_uatdoc`** (not temp):

| File | What it is |
|---|---|
| `guide_lib.js` | shared helpers (img, step, callout, grid, cover, build) |
| `build_pos_guide.js` | Store Stock & Till guide, v1.4 |
| `build_stockin_guide.js` | Getting Stock In guide, v1.4 |
| `gen_round3.js` | UAT Testing Guide, Round 3 (no screenshots, no passwords) |
| `shots\*.png` | the 28 screenshots, 1366x645 |
| `collect_shots.py` | copies Chrome screenshots out of the session tool-results folder |
| `render_check.ps1` | Word -> PDF for a page-by-page layout check |

Rebuild: `node build_pos_guide.js`, `node build_stockin_guide.js`, `node gen_round3.js`.
Output goes to `C:\ClaudeCode\*.docx`.

The generators were recovered by **replaying the Write and Edit tool calls** from the old
session transcript (`~/.claude/projects/C--ClaudeCode/<session>.jsonl`). That works for any
file a past session wrote, as long as the transcript still exists.

## Why this is non-obvious

- **A scratchpad is temp.** Anything that will be needed again (generators, screenshots,
  source sheets) belongs in the project folder.
- **Administrator cannot sell on POS_Test2 out of the box.** The till's invoice takes the
  user's own default profile (`Cermaics_User2` for Administrator) and Checkout fails with
  "No open POS Opening Entry found for POS Profile Cermaics_User2". For a screenshot run,
  set `cur_pos.frm.doc.pos_profile = 'POS_Test2'` before Checkout, on the sale AND on the
  return. Same warehouse either way (POS Store - ACT).
- **Chrome in the background (`document.visibilityState === 'hidden'`)**:
  - `Page.captureScreenshot` times out about every second call. A screenshot as its own
    call, retried once, succeeds. Inside a batch straight after JS it usually fails.
  - Bootstrap modals never finish their fade, so dialogs exist but stay invisible
    (`display: none`). Force them: `$m.removeClass('fade'); $m.modal('show')`, and remove
    the leftover `.modal-backdrop` afterwards.
  - The Recent Orders summary panel renders but stays hidden. Show it with
    `cur_pos.order_summary.toggle_component(true)`.
  - A screenshot taken right after a timeout can come back **tiled**. Retake it.
- **"Select POS User"** is injected by the custom `point-of-sale` Page script and did not
  appear for Administrator in this run, so screenshot 10 does not show it. The guide text
  still describes it.
- **v16 till: Recent Orders is a button** (secondary action, top right), not a menu item.
  The menu only has Open Form View and Close the POS. Checked against the bundle.
- **Setting a Link by `set_value` does not run the form's own handler.** On POS Closing
  Entry call `cur_frm.script_manager.trigger('pos_opening_entry')` to load the invoices.
- **Importer truth that the guides must not soften:** a Select value that is not on the
  allowed list is rejected, and the new item then shows the FIRST option of that field
  (Collection Bonnie, Colour Amber, Base Cloth Acrylic, Size Small). The guide says the
  field "may show a wrong value", not "is left blank".

## Test documents created for the screenshots (all TEST company, Sage TEST)

- Transfer Main Distribution -> POS Store, FABCBBOR x2 (MAT-STE-2026-00518); one sold,
  one moved back (MAT-STE-2026-00519).
- ACC-SINV-2026-00062 (BN189JUL26 x2, Voucher R500 + Credit Card R2,300, voucher ref
  TEST-VCH-0002) -> Sage INV0000039.
- ACC-SINV-2026-00063, full return of 00062 -> Sage CRN0000005.
- ACC-SINV-2026-00064 (FABCBBOR x1, R4,500) -> Sage INV0000040.
- POS-OPE-2026-00082 opened as Administrator on POS_Test2, closed by POS-CLO-2026-00081.
- Net stock effect: FABCBBOR Main Distribution 400 -> 399. UAT items unchanged.

## See also

- `sites/ardmore.md` (2026-09-29 documentation entry)
- `gotchas/2026-09-07-pos-invoice-client-scripts-run-inside-pos-page.md`
- `gotchas/2026-07-24-pos-outdated-opening-entry-blocks-till.md`
