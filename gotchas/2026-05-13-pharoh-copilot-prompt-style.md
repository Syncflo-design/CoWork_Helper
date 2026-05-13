# Gotcha: GitHub Copilot prompt style for Pharoh .NET endpoints

**Date:** 2026-05-13  
**Project:** erpnext_sbca / Pharoh middleware  
**Symptom:** GitHub Copilot struggles with or ignores a Pharoh endpoint prompt.

## What happened

Directly-written Copilot prompts (casual CONTEXT / TASK / FIELD NOTES style)
produced poor results. Copilot worked well when given the JournalEntry prompt
style (structured sections, field mapping table, explicit strategies, numbered
task list).

## The fix

**Do not write a Copilot prompt for a Pharoh endpoint in a casual style.**  
The prompt must follow the exact structured format below. Write it directly
using this format, OR use a meta-prompt to Opus (see bottom of file) to produce it.

### Correct Copilot prompt format (the one that works)

Every section below is required. Match the wording of the section headers exactly.

```
================================================================================
PROMPT FOR GITHUB COPILOT  --  Pharoh .NET project (VS 2022, other machine)
Date: YYYY-MM-DD
Purpose: <one or two lines describing what this prompt adds or changes>
================================================================================

You are working on the Pharoh middleware -- a .NET / C# Web API that bridges
between ERPNext (the customer-facing custom app "erpnext_sbca") and Sage
Business Cloud Accounting. The project is open in Visual Studio 2022.

--------------------------------------------------------------------------------
BACKGROUND
--------------------------------------------------------------------------------

ERPNext custom app "erpnext_sbca" posts financial documents to Pharoh; Pharoh
translates camelCase -> PascalCase and forwards to Sage Business Cloud
Accounting's REST API.

Sage's API docs live at:
  https://resellers.accounting.sageone.co.za/api/2.0.0

Relevant page(s) for this task:
  <specific Sage API help page URL(s)>

The existing endpoint <name> is the closest reference -- use it as your
structural template. <OR: "A brand new controller is required.">

--------------------------------------------------------------------------------
WHAT NEEDS TO BE BUILT
--------------------------------------------------------------------------------

<Endpoint URL(s), what they do, full JSON request body with REAL example values
-- not "string" placeholders. Notes on each field immediately after the body.>

--------------------------------------------------------------------------------
WHAT PHAROH MUST DO WITH THE PAYLOAD
--------------------------------------------------------------------------------

<Step by step. If decomposition is needed, name the strategy explicitly
(e.g. "Strategy B -- Pivot decomposition ** USE THIS **"). If it is a
single Sage call, say so clearly.>

--------------------------------------------------------------------------------
FIELD MAPPING (camelCase Pharoh input -> PascalCase Sage body)
--------------------------------------------------------------------------------

<Table format:>

  Pharoh input          Sage field          Notes
  --------------------  ------------------  --------
  ...                   ...                 ...

<Note any fields Sage treats as read-only that must NOT be sent.>
<Note any fields that must be logged at INFO level.>

--------------------------------------------------------------------------------
RESPONSE PHAROH RETURNS TO ERPNEXT
--------------------------------------------------------------------------------

Success:
{ "success": true, "sageOrderId": ..., "documentNumber": ..., "errorMessage": null }

Failure:
{ "success": false, "sageOrderId": null, "documentNumber": null, "errorMessage": "..." }

<Note any fields that are null on success for this specific endpoint.>
<Note what ERPNext does with the response (stamps which custom fields).>

--------------------------------------------------------------------------------
ALREADY DONE ON THE ERPNEXT SIDE (don't re-derive)
--------------------------------------------------------------------------------

<Bullet list of what erpnext_sbca already does so Copilot doesn't try to
re-implement it on the Pharoh side. Include: which events trigger the push,
which custom fields carry the Sage IDs, which Settings toggle gates it.>

--------------------------------------------------------------------------------
YOUR TASK
--------------------------------------------------------------------------------

1. <DTO / model class to create or update>
2. <Controller action(s) to create -- class name, route, file location>
3. <Decomposition or Sage call implementation>
4. Return the success/failure shape above.
5. Update the swagger / OpenAPI spec so the new endpoint shows in /swagger/index.html.

When done, run the project locally and confirm the swagger renders the new
endpoint and shape. ERPNext-side testing happens separately on the live deployment.

================================================================================
END OF PROMPT
================================================================================
```

### Key rules for the format

- **Real example values in the JSON body** — not `"string"`, not `"yyyy-MM-dd"`.
  Use actual document names, actual amounts, actual account IDs.
- **Sage API help page URL** — always include the specific endpoint page, not
  just the root docs URL.
- **Existing reference controller** — always name it. Copilot follows patterns
  better than descriptions.
- **Field mapping table** — required even for simple endpoints. Helps Copilot
  get PascalCase right.
- **Already done on ERPNext side** — prevents Copilot reimplementing ERPNext
  logic inside Pharoh.
- **Swagger update** — always the last numbered task. Copilot skips it otherwise.

## Verified working examples

| Prompt file | Endpoint |
|---|---|
| `projects/erpnext_sbca/Pharoh_JournalEntry_Update_Prompt.txt` | POST /api/JournalEntriesSync/post-journalentry-to-sage |
| `projects/erpnext_sbca/Pharoh_StockAdjustment_Endpoint_Prompt.txt` | POST /api/StockAdjustmentSync/post-stock-adjustment-to-sage |
| `projects/erpnext_sbca/Pharoh_Cancellation_Endpoint_Prompt.txt` | POST /api/SalesOrder/cancel-salesorder-in-sage + PurchaseOrder |

Use any of these as a concrete style reference when writing the next prompt.

## Alternative: use Opus to write the Copilot prompt

If unsure about the structure, give Opus a meta-prompt instead:

1. Paste the full contents of `Pharoh_JournalEntry_Update_Prompt.txt` as the style example.
2. Describe the new endpoint: what it accepts, what it calls in Sage, what it
   returns, what's already done on the ERPNext side.
3. Say: "Produce a complete, self-contained Copilot prompt the developer can
   paste directly into their IDE, matching the style and structure of the example above."

Opus output can be used directly — it reliably reproduces the correct format.
