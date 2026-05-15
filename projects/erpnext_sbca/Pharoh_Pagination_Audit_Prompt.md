# Copilot Task — Standardise pagination across the Pharoh API

Paste everything below the line into GitHub Copilot Chat with the
`SageErpNextAPI` solution open in Visual Studio.

---

## Context

You are working in the Pharoh middleware (`SageErpNextAPI`) — a .NET / C# Web API
that bridges ERPNext and Sage Business Cloud Accounting. Controllers live in
`Controllers/`, the Sage HTTP layer in `Services/SageService.cs`, DTOs in
`Models/`. ERPNext is the consumer: it calls these endpoints and loops over the
results.

## The rule

Any endpoint that returns a **collection** which could realistically exceed
~100 rows must use **pass-through pagination** — the caller (ERPNext) drives the
loop, one page per request. Endpoints that loop internally and aggregate every
page into one giant response are NOT acceptable: on large datasets they produce
huge payloads and time the request out.

## The canonical pattern — copy this exactly

`InventorySyncController.GetInventoryForErpNext` (`[HttpPost("get-inventory-for-erpnext")]`)
and `GetInventoryQOHForErpNext` (`get-inventory-qtyonhand-for-erpnext`) are the
reference implementations. The pattern:

1. The action takes `[FromQuery] int skipQty = 0` in addition to its existing
   parameters.
2. It calls a **batch-aware** service method — e.g.
   `_sageService.GetInventoryItemsByBatchAsync(..., skipQty)` — that makes ONE
   Sage `$skip` call and returns a batch response carrying `.Items`,
   `.TotalResults`, `.ReturnedResults`.
3. The action returns this exact envelope:
   ```csharp
   return Ok(new
   {
       TotalResults = sageBatchResponse.TotalResults,
       ReturnedResults = sageBatchResponse.ReturnedResults,
       Items = <mapped list>
   });
   ```
4. The caller loops: start at `skipQty = 0`; after each response add
   `ReturnedResults` to `skipQty`; stop when `skipQty >= TotalResults` or
   `ReturnedResults == 0`.

`SageService.cs` already paginates against Sage's own `$skip` /
`TotalResults` / `ReturnedResults` for every pull — the data layer can already
page. What's missing is **exposing** that page-by-page to ERPNext instead of
aggregating it inside Pharoh.

## What to do

### Step 1 — Audit

Go through every controller in `Controllers/`. For each action that returns a
collection, classify it:

- **Already correct** — already uses `skipQty` plus the
  `{ TotalResults, ReturnedResults, Items }` envelope.
- **Needs conversion** — returns a plain list, OR aggregates all pages
  internally with a `do { ... skipQty += ReturnedResults } while (skipQty < totalQty)`
  loop inside the controller or service before returning.
- **Exempt** — returns a single record, or a collection that is provably
  bounded-small (e.g. tax types, analysis categories, price lists). State WHY
  you judged it bounded so a human can sanity-check the call.

Produce the audit as a table:
`Controller | Action / route | Returns | Classification | Reason`.

### Step 2 — Convert

For every "Needs conversion" endpoint:

- Add `[FromQuery] int skipQty = 0` to the action signature.
- Keep all existing filter parameters (`lastDate`, `InclZeroOnHand`, etc.)
  exactly as they are.
- If the service layer has no batch-aware method for that entity, add one that
  mirrors `GetInventoryItemsByBatchAsync`: it takes `skipQty`, makes **one**
  Sage `$skip` call (not a loop), and returns a batch-response DTO with `Items`,
  `TotalResults`, `ReturnedResults`. Replace the internal `do/while`
  aggregation with this single-page call.
- Return the `{ TotalResults, ReturnedResults, Items }` envelope.
- Leave the route string and HTTP verb unchanged.

### Step 3 — Report response-shape changes

Converting an endpoint from a plain list to the
`{ TotalResults, ReturnedResults, Items }` envelope **breaks the ERPNext
consumer** of that endpoint. Produce a list of every endpoint whose response
shape changed — `route | old shape -> new shape` — so the ERPNext side
(`erpnext_sbca/API/*.py`) can be repointed to loop. Do not assume ERPNext copes
automatically; it does not.

## Guardrails

- Do **not** touch POST/push endpoints that send data TO Sage (invoices,
  journals, item creation, stock reconciliation) — they don't return
  collections.
- Do **not** change route strings, controller names, or auth handling.
- Do **not** rename or recase the `TotalResults` / `ReturnedResults` / `Items`
  fields — ERPNext reads them by name.
- Work one controller at a time and keep each controller's conversion in its
  own commit, so each can be reviewed and rolled back independently.

## Deliverables

1. The audit table from Step 1.
2. The code changes, one controller per commit.
3. The response-shape-change list from Step 3, for the ERPNext team.
