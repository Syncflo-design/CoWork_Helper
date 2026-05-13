# `erpnext_sbca` — Technical Reference

**Repo:** `C:\ClaudeCode\Erpnext-Sbca` · GitHub `Syncflo-design/Erpnext-Sbca`
**Last major refactor:** 2026-05-13
**Companion doc:** `ASSESSMENT.md` (historical, pre-refactor — read for background only)

**External API references:**
- **Pharoh middleware swagger** — `https://pharoh.co.za/swagger/index.html` (raw spec at `/swagger/v1/swagger.json`). Use this to confirm endpoint URLs and DTO shapes for both push and pull paths.
- **Sage Business Cloud Accounting API docs** — `https://resellers.accounting.sageone.co.za/api/2.0.0`. Use this to confirm the underlying Sage data model when designing Pharoh-side translations (e.g. the `Effect` enum on Journal Entry: 1=Debit, 2=Credit; nullable foreign keys etc.).

Purpose: a reference for the non-obvious sync features in the app — where the code lives, what custom fields exist, what shape the Pharoh middleware speaks, and how each setup is bootstrapped on a fresh tenant. Skip the simple pulls (Suppliers, Customers) which are linearly the obvious thing.

## Design principles (re-stated for context)

- **Sage owns financial GL.** ERPNext mirrors the chart of accounts and pushes invoice/credit-note/payment values to Sage as the financial source of truth.
- **ERPNext owns stock and operations.** Every Item pushed to Sage is created as a **non-stock service** (`Physical: false`) so Sage never tries to track quantities. Sage records the *value* of every stock movement via the invoice push; ERPNext records the *quantity* via its own stock ledger.
- **Strict additive after Phase 1.** Once initial setup has completed, syncs only add new records — they never delete or modify existing ones. Stale records get `disabled = 1` instead of deletion so historical mappings keep resolving.
- **Pharoh is the only adapter.** All Sage-side calls go through the Pharoh middleware. Credentials live per-Company in the `Company Sage Integration` child table on `Erpnext Sbca Settings`. The custom app never talks to Sage directly.

## Common patterns across sync handlers

These conventions apply to every sync described below.

**Credentials envelope.** Each Pharoh call POSTs a JSON body with these five fields, plus an `apikey` URL query parameter:

```python
{
    "loginName": integration.username,
    "loginPwd": integration.get_password("password"),
    "useOAuth": bool(integration.use_oauth),
    "sessionToken": integration.get_password("session_id"),
    "provider": integration.get_password("provider"),
}
```

**Sage IDs land in `custom_*` fields.** Every sync target gets a `custom_sage_<entity>_id` field on its ERPNext doctype. Field is created idempotently on first sync run by an `_ensure_*_field()` helper. Pattern:

```python
def _ensure_<entity>_id_field():
    if frappe.db.exists("Custom Field",
                        {"dt": "<DocType>", "fieldname": "custom_sage_<entity>_id"}):
        return
    frappe.get_doc({
        "doctype": "Custom Field",
        "dt": "<DocType>",
        "fieldname": "custom_sage_<entity>_id",
        "label": "Sage <Entity> ID",
        "fieldtype": "Data",
        "read_only": 1,
        "description": "...",
    }).insert(ignore_permissions=True)
    frappe.db.commit()
```

**Match key order.** Upserts try Sage ID first, fall back to a natural ERPNext key (name) for pre-existing records that don't yet carry the Sage ID. On every successful upsert, the Sage ID is (re-)written.

**Settings toggles.** Every sync is gated by a `sync_<entity>` Check field on `Erpnext Sbca Settings`. `is_sync_enabled(fieldname)` reads it and defaults `True` if the field doesn't exist (preserves prior behaviour on freshly-migrated sites).

**Whitelisted methods called by buttons must return a truthy payload** — see `gotchas/2026-05-13-frappe-whitelisted-action-needs-return-value.md`.

---

## 1. Account sync with Opening Balances

Two related but distinct flows. The first builds the chart of accounts; the second adds opening balances against those accounts.

### 1a. Account sync — `erpnext_sbca/API/account.py`

**Endpoint:** `POST {url}/api/AccountsSync/get-accounts-for-erpnext?apikey={apikey}&lastDate=1970-01-01`

**Trigger:** Scheduled (`scheduler_events["all"]`), gated by `sync_accounts` toggle.

**Model:** Two-phase setup per Company.

- **Phase 1 — destructive setup.** User ticks `Apply Account Cleanup on Next Sync` on the relevant `Company Sage Integration` row (or calls the **Apply Account Cleanup** button on the Settings → Accounts tab, which after a typed-DELETE confirmation queues the same flag). The next account-sync tick:
  1. Deletes every non-Sage, non-system-required leaf account on the Company (best-effort — accounts linked to transactions are kept by Frappe's standard guard).
  2. Imports all Sage accounts fresh, tagged `custom_sage_managed = 1`.
  3. Flips `Setup Complete = 1` on the integration row.
- **Phase 2 — strict additive.** Once `Setup Complete = 1`, only new Sage accounts get added. Nothing is ever deleted or modified.

**Protected accounts.** `SYSTEM_REQUIRED_ACCOUNTS` set in `account.py` lists ERPNext-core leaf accounts (Stock Adjustment, Round Off, COGS, Stock In Hand, Accounts Receivable, etc.) that the cleanup never touches *unless* Sage has a same-named equivalent (then ERPNext's default is replaced so Sage's takes over the company-default slot).

**Custom field:** `Account.custom_sage_managed` (Check, read-only). Lets the sync distinguish Sage-owned accounts from manually-created sub-accounts that users add for budgeting.

**Helpers (whitelisted):**
- `get_companies_ready_for_setup()` — Companies that have a Sage Integration row AND at least one `custom_sage_managed` account. Drives the **Active Company** picker on the Accounts tab.
- `get_account_setup_status(company)` — counts (Sage-managed, to-be-deleted, locked) plus phase flag. Feeds the Accounts-tab status banner.
- `apply_account_cleanup(company)` — ticks `strip_defaults_on_next_sync`. **Returns `{"queued": True, ...}`** so the client-side success callback fires (see gotcha above).

### 1b. Opening Balances — `erpnext_sbca/API/account.py`

**Endpoint:** `POST {url}/api/AccountsSync/get-accountbalances-for-erpnext?apikey={apikey}`

**Trigger:** On-demand via **Pull Opening Balances** button on Settings → Opening Balances tab. **No scheduled task** — balances change rarely, so button-only.

**Response shape:**
```json
[{"account": "Unallocated Expense", "company": "", "opening_balance": 0}, ...]
```

The Sage payload's `company` field is empty — the tenant is identified by the `Company Sage Integration` row we're calling from, not by anything in the response.

**Cache DocType:** `Sage Account Opening Balance`. One row per `(company, account_name)` pair. Autoname `format:{company}-{account_name}`. Stale-record handling: when an account stops being returned, `disabled = 1` (kept as historical record, never deleted). `last_seen_at` Datetime records the most recent pull that returned the row.

**Account name handling.** Stored as the raw Sage name (e.g. `"Unallocated Expense"`), NOT the company-suffixed ERPNext name (`"Unallocated Expense - X"`). Downstream consumers resolve to ERPNext if needed — keeps the cache faithful to what Sage returned.

**Helpers:**
- `get_account_opening_balances_from_sage()` — whitelisted, callable from the Settings button. Walks `Company Sage Integration` rows, upserts, sweeps stale, returns per-Company summary `{company, created, updated, disabled, errors}`.
- `get_opening_balance_status()` — whitelisted, called by the Settings JS to render the tab banner. Returns per-Company `{active, disabled, last_seen_at, total_value}`.

**Setup sequence for a new tenant:**
1. Add `Company Sage Integration` row with credentials.
2. Wait for one account-sync tick OR trigger from Scheduled Job list. `Company` appears in **Active Company** picker.
3. On Accounts tab: pick the Company → click **Apply Account Cleanup** → type DELETE → Queue Cleanup.
4. Wait for next tick (~4 min) — accounts get mirrored from Sage.
5. On Opening Balances tab: click **Pull Opening Balances**. Banner shows counts.

---

## 2. Additional Price Lists and Item Prices

Sage's price lists are NOT ERPNext's `Price List` doctype directly — they're per-Sage-tenant numeric IDs with names. Two sync handlers and a Sage-ID-on-Price-List bridge field.

### 2a. Price Lists — `erpnext_sbca/API/item_details.py::get_price_list_from_sage`

**Endpoint:** `POST {url}/api/AdditionalPriceListSync/get-pricelists-for-erpnext?apikey={apikey}`

**Trigger:** Scheduled (`sync_price_lists` toggle).

**Response shape:**
```json
[{"id": 3795, "name": "Default Price List", "description": "Default Price List",
  "isDefault": true, "enabled": true}, ...]
```

**Cache DocType:** Standard ERPNext `Price List`, augmented with one custom field:
- `custom_sage_price_list_id` (Data, read-only) — populated by `_ensure_sage_price_list_id_field()` then written on every Price List upsert from the Sage `id` field.

This custom field is the linchpin for the other syncs that reference price lists by Sage ID (customer pull, additional item prices). **Match key on upsert is `price_list_name`** (not the Sage ID) so the field gets written to whichever ERPNext Price List shares Sage's name.

**Order constraint.** `get_price_list_from_sage` must run BEFORE `get_customers_from_sage` (which resolves `default_price_list_id` via the Sage ID) and BEFORE `get_addition_prices_from_sage` (which iterates the Sage IDs). Order is locked in `hooks.py::scheduler_events["all"]` with an inline comment.

### 2b. Item Prices — `erpnext_sbca/API/item_details.py::get_addition_prices_from_sage`

**Endpoint:** `POST {url}/api/AdditionalItemPricesSync/get-additional-prices-for-erpnext?apikey={apikey}&pricelistID={pl_id}`

Note: requires a Sage `pricelistID` query parameter, called once per Price List.

**Trigger:** Scheduled (`sync_additional_prices` toggle).

**How it iterates the pricelist IDs.**

```python
_ensure_sage_price_list_id_field()  # defensive — runs even if sync_price_lists is off
pricelist_ids = [
    pl.custom_sage_price_list_id
    for pl in frappe.get_all(
        "Price List",
        filters={"custom_sage_price_list_id": ["is", "set"]},
        fields=["custom_sage_price_list_id"],
    )
    if pl.custom_sage_price_list_id
]
if not pricelist_ids:
    pricelist_ids = ["3796", "3795"]   # historical hardcode, fallback only
```

The dynamic query drives the iteration off the Price Lists that the v2a sync has stamped with Sage IDs. The hardcoded `["3796", "3795"]` fallback only fires on a freshly-installed site where the Price List pull hasn't run yet; it evaporates after the first successful tick.

**Response shape (per-row):**
```json
{"itemCode": "...", "priceListName": "...", "priceListRate": 99.99}
```

Creates / updates ERPNext `Item Price` rows by `(item_code, price_list)`. Hardcoded `uom = "Nos"`, `currency = "ZAR"`, `selling = 1`, `buying = 1` — historical, unchanged this session.

**Customer linkage.** `customer.py::_upsert_customer` reads `default_price_list_id` from the Sage payload, looks it up in `Price List.custom_sage_price_list_id`, and sets `Customer.default_price_list`. Wrapped in try/except in case the Custom Field hasn't been created yet on a brand-new site. Missing matches are silent — the field gets set on the next tick.

---

## 3. Sales Reps and Sales Team

Each Customer in the Sage payload carries a `sales_team` child array referencing Sales Persons *by name*. For that linkage to resolve on the ERPNext side, Sales Persons must exist first.

### 3a. Sales Person sync — `erpnext_sbca/API/sales_person.py`

**Endpoint:** `POST {url}/api/SalesReps/get-salesperson-for-erpnext?apikey={apikey}`

**Trigger:** Scheduled (`sync_sales_persons` toggle).

**Response shape:**
```json
{"id": "2713", "first_name": "Fred", "last_name": "Brown",
 "sales_person_name": "Fred Brown", "active": true,
 "email_id": "fred@example.co.za", "mobile_no": ""}
```

**Custom field:** `Sales Person.custom_sage_rep_id` (Data, read-only). Created by `_ensure_sage_rep_id_field()` on first sync run.

**Match key order:**
1. `custom_sage_rep_id == sage_id`
2. Fallback: `sales_person_name == stripped_name` (for pre-existing ERPNext records without Sage ID)

Always (re-)writes `custom_sage_rep_id` on update.

**Defensive field-set.** `email_id` and `mobile_no` aren't standard fields on `Sales Person` in every ERPNext version, so the upsert uses `hasattr(doc, "email_id")` checks before setting them. Avoids breaking on older sites without those custom fields.

### 3b. Customer.sales_team population — `erpnext_sbca/API/customer.py::_apply_sales_team`

Each customer's `sales_team` child rows reference Sales Persons by name. The Sage payload often has trailing whitespace (e.g. `"Colin Peters "`) — the sync strips it before looking up.

```python
sp_name = sp_name_raw.strip()
if not frappe.db.exists("Sales Person", sp_name):
    sales_team_skips.append(f"{customer.customer_name} -> {sp_name}")
    continue
```

Sales Persons that don't exist in ERPNext get logged to `sales_team_skips` (visible in the per-Company summary in the error log) but DON'T block the customer upsert. The fix is to run the Sales Person pull, which is why it sits BEFORE the customer pull in the scheduler ordering.

**Reset-and-rebuild.** The sync clears `customer.sales_team` entirely before adding the new rows. Avoids stale-row accumulation across re-pulls.

**Hardcoded sales-rep ID worth knowing about.** `sales_invoice.py::_post_taxinvoice_return_worker` falls back to a hardcoded Sage rep ID `740886` (Fisokuhle Radebe) when no Sales Person can be resolved on a credit note. Now that the Sales Person pull populates `custom_sage_rep_id`, this fallback should rarely fire — but the line is still there and worth reviewing later.

---

## 4. Tax mapping (per-tenant Sage Tax + Item Tax Template Sage Map)

The most architecturally involved feature added in this refactor. Sage's tax records have **per-tenant internal IDs** — the same conceptual tax ("VAT Standard 15%") has different `sage_idx` values in different Sage tenants. Hardcoding doesn't work. The mapping is explicit and manual.

### 4a. Pull — `erpnext_sbca/API/tax.py::get_taxes_from_sage`

**Endpoint:** `POST {url}/api/SalesTaxSync/get-sales-taxes-for-erpnext?apikey={apikey}`

**Trigger:** On-demand via **Pull Taxes from Sage** button on Settings → Taxes tab. **No scheduled task** — taxes change rarely.

**Response shape:** Templates-with-children, modelled on ERPNext's `Sales Taxes and Charges Template`:

```json
[{
  "name": "Standard Rate (Capital Goods)",
  "title": "106161",
  "taxes": [{
    "sage_idx": 106161,
    "description": "VAT @ 0.15%",
    "rate": 0.15,
    "parent": "Standard Rate (Capital Goods)"
  }]
}, ...]
```

Each parent template has exactly one child tax row in the wild. The sync flattens — one `Sage Tax` record per (parent, child) pair. `sage_idx` from the child becomes the unique key; `parent` becomes the template_label for display.

**Rate convention.** Decimal fraction: `0.15` = 15%. The description string is sometimes `"VAT @ 0.15%"` (Sage formatting quirk — multiplies by nothing) but the numeric `rate` is the truth. Some Sage default records carry `rate: 1` (Goods/Capital Goods Imported, VAT Adjustments) which is genuinely 100% per SARS import treatment — passed through as-is.

**Cache DocType:** `Sage Tax`. One row per `(company, sage_idx)` pair. Autoname `format:{company}-{sage_idx}`. Fields: `company`, `sage_idx`, `description`, `rate`, `template_label`, `disabled`, `last_seen_at`.

### 4b. Item Tax Template Sage Map child table

ERPNext's standard `Item Tax Template` gets a Custom Field called `custom_sage_tax_map` (added idempotently by `_ensure_sage_tax_map_field()`). It's a Table linking to the new `Item Tax Template Sage Map` child doctype.

Each child row: `(company, sales_sage_tax, purchase_sage_tax)` — pairing the ERPNext template with the Sage Tax records to use per tenant. One row per tenant per template.

**Workflow on a new tenant:**
1. Click **Pull Taxes from Sage** on Settings.
2. Open each Item Tax Template the site uses, find the Sage Tax Mappings child table, add one row per Company, pick sales + purchase tax records from the dropdowns. The dropdowns are filtered per row's Company by `public/js/item_tax_template.js`.

### 4c. Push-time resolution — `tax.py::resolve_sage_tax`

Every transaction-push path calls this:

```python
sage_tax = resolve_sage_tax(item_doc, company_name, direction)
# direction: "sales" or "purchases"
tax_type_id = int(sage_tax.sage_idx)
rate = float(sage_tax.rate)
```

Used by `items.py`, `sales_invoice.py` (both regular and return workers), `purchase_invoice.py` (both workers), `pos_invoice.py::group_items`. Replaces every hardcoded `tax_id` read and every `* 1.15` calculation.

**Failure modes** — each one raises a precise `frappe.throw` naming what's missing:
- Item has no `Item Tax Template` assigned (empty `taxes` child table).
- Item Tax Template has no mapping row for this Company.
- Mapping row has no `sales_sage_tax` / `purchase_sage_tax` for the requested direction.
- Linked `Sage Tax` record is `disabled = 1` — resolves anyway (so historical mappings keep working) but logs a warning so the misalignment is visible.

### 4d. Price math — `tax.py::build_price_pair`

Called from `items.py` when pushing new Items to Sage. Auto-detects pricing direction:

```python
if doc.custom_retail_price_incl_vat > 0:
    # inclusive-driven: retail price is the source, excl is derived at 4dp
    incl = round(doc.custom_retail_price_incl_vat, 2)
    excl = round(incl / (1 + rate), 4)
else:
    # exclusive-driven: standard_rate is the source, incl is derived at 2dp
    excl = round(doc.standard_rate, 2)
    incl = round(excl * (1 + rate), 2)
```

4dp on the derived exclusive ensures the round-trip is exact at 2dp on the inclusive side — e.g. 99.99 incl at 15% rate stores excl as 86.9478, multiplying back gives 99.9925 → rounds to 99.99 cleanly. Without the extra precision, half the prices would round-trip to a cent off.

---

## 5. Stock items as Sage services (the model that ties everything together)

Every Item pushed to Sage is created as a non-stock service — `"Physical": false` always, regardless of ERPNext's `is_stock_item` flag. Set in `items.py::_post_item_worker` line ~56.

**Why this matters for the whole architecture:**
- Sage never tries to keep its own stock ledger for these items. ERPNext owns the count.
- Sage's internal GL mapping for each (service) item routes the invoice-line value to the right financial accounts when the invoice is posted on the Sage side. ERPNext's job ends at sending the invoice-line value over the wire.
- This is why the transaction push paths (`sales_invoice.py`, `purchase_invoice.py`, `pos_invoice.py`) don't need to send separate journal entries for Cost-of-Sales etc. — Sage's per-item GL config handles it because the items are properly set up.

**External setup step still required** — on the Sage side, every item must be configured as **Do Not Track Balance**. That's done in the Sage UI, outside this app, and is one-off per tenant on go-live. The custom app just ensures every NEW item created from ERPNext lands in Sage as a service.

**Out-of-source reminder.** A Server Script called `update-item-add-info` lives in the database (not in this repo) and is re-enabled by `item_details.py::update_item_job` on every cron tick. If it pushes item upserts to Sage, it needs the same `Physical: false` + `resolve_sage_tax` updates. Worth inspecting on the bench when redeploying.

---

## 6. Journal Entry push

ERPNext-side Journal Entries push to Sage on submit. Built 2026-05-13.

### 6a. The push handler — `erpnext_sbca/API/journal_entry.py`

**Pharoh endpoint:** `POST {url}/api/JournalEntriesSync/post-journalentry-to-sage?apikey={apikey}`

**Trigger:** `doc_events["Journal Entry"]["on_submit"]`. Gated by `push_journal_entry_on_submit` toggle on Erpnext Sbca Settings. **Defaults to OFF** until Pharoh's multi-row endpoint goes live — flip it ON in Settings once both sides are deployed.

**Async pattern:** matches the invoice pushes — the doc_event wrapper enqueues `_post_journal_entry_worker` so submit doesn't block on Pharoh. Worker iterates `Company Sage Integration` rows, builds the per-tenant payload, POSTs, and writes the Sage document references back to the ERPNext Journal Entry.

### 6b. Custom fields involved

- `Account.custom_sage_account_id` — stamped from Pharoh's `sageacct_idx` field by `get_accounts_from_sage`. Sage uses signed `long` IDs (negative for system accounts like VAT controls — e.g. -24). Read at push time to resolve each row's account.
- `Journal Entry.custom_sage_order_id`, `Journal Entry.custom_sage_document_number`, `Journal Entry.custom_sage_sync_status` — three tracking Custom Fields created idempotently by `_ensure_journal_entry_tracking_fields()` on first run. Mirror the existing tracking pattern used by the invoice pushes.

### 6c. Multi-row decomposition — the architectural decision

ERPNext Journal Entries are multi-row (N accounts in `accounts` child table, debits and credits balanced overall). Sage's underlying `JournalEntry/Save` endpoint takes a single (Account, ContraAccount, Debit, Credit) tuple per call.

**Decision locked 2026-05-13: one ERPNext journal → one Sage journal.**

ERPNext sends the **full multi-row journal in a single Pharoh call** with a `lines[]` array. **Pharoh** is responsible for decomposing into Sage's single-pair shape and posting under one shared `Reference` so the journal appears as one logical entry on the Sage side. Strategy recommended to Pharoh: pivot decomposition (pick one line as the contra, emit N-1 Save calls all referencing the pivot, all sharing the Reference).

Why this design: keeps the 1:1 model that every other push (Sales / Purchase / POS Invoice) already uses, so an accountant browsing Sage sees one journal per ERPNext journal — no mental rebuild required.

### 6d. Payload shape (camelCase, ERPNext → Pharoh)

```json
{
  "credentials": { "loginName": "...", "loginPwd": "...", "useOAuth": false,
                   "sessionToken": "...", "provider": "..." },
  "journalEntry": {
    "date": "yyyy-MM-dd",
    "reference": "<ERPNext JE name>",
    "description": "<doc.user_remark>",
    "memo": "<doc.user_remark>",
    "taxPeriodId": null,
    "analysisCategoryId1": null,
    "analysisCategoryId2": null,
    "analysisCategoryId3": null,
    "trackingCode": "",
    "businessId": null,
    "payRunId": null,
    "lines": [
      { "effect": 1, "accountId": <int>, "debit": <decimal>, "credit": 0,
        "exclusive": <decimal>, "tax": 0, "total": <decimal>,
        "taxTypeId": null, "description": "<row.user_remark>" },
      ...
    ]
  }
}
```

**Field notes:**
- `effect`: **1 = Debit, 2 = Credit** (from Sage's enum; see Sage docs link at top of this file).
- `accountId`: signed long. Negatives are valid (Sage system accounts).
- Nullable integers (`taxTypeId`, `taxPeriodId`, `analysisCategoryId1/2/3`, `businessId`, `payRunId`) are sent as `null` not `0` — Sage's API treats `0` as an invalid foreign key.
- `tax` is always `0`, `exclusive == total` on every line — ERPNext journals are tax-free at the journal level.
- Read-only/system-generated Sage fields (`Editable`, `Locked`, `HasAttachments`) are not sent.

### 6e. Failure modes (each raises a precise `frappe.throw`)

- Item-side row has both `debit > 0` AND `credit > 0` (Sage expects one direction per row).
- Row references an account that has no `custom_sage_account_id` stamped yet — means the account sync hasn't completed for that Company. Fix: run the account sync.
- `custom_sage_account_id` is non-numeric (defensive — shouldn't happen if Pharoh stamps it correctly).
- Sage credentials missing on a `Company Sage Integration` row.
- Pharoh returns non-success: error message logged + `custom_sage_sync_status = "Failed"` set.

### 6f. Carried-forward Pharoh-side requirement

The push depends on Pharoh accepting the multi-row `lines[]` shape and decomposing internally. The Pharoh prompt for that work is captured in `projects/erpnext_sbca/Pharoh_JournalEntry_Update_Prompt.txt`. Until Pharoh is updated, **leave the Settings toggle OFF** — submissions won't push but won't error either.

---

## 7. Settings UI structure

Five tabs on `Erpnext Sbca Settings`:

| Tab | Purpose |
|---|---|
| **Connection** | Per-Company Sage Integration credentials, sync toggles, "Get Authentication Details" OAuth helper. |
| **Accounts** | Active Company picker + status banner + **Apply Account Cleanup** button. |
| **Taxes** | Per-Company Sage Tax catalogue counts + **Pull Taxes from Sage** button. |
| **Opening Balances** | Per-Company opening balance counts + total value + **Pull Opening Balances** button. |
| *(more as added)* | |

Status banners on the Taxes and Opening Balances tabs are populated by client-side calls to `tax.get_tax_status` and `account.get_opening_balance_status` on form refresh. Shared rendering in `_build_status_table_html` (in `erpnext_sbca_settings.js`).

---

## Carried-forward technical debt

Captured here so future sessions don't have to rediscover:

- **`update-item-add-info` Server Script** lives in the DB on the bench. Needs the same `Physical: false` + tax-resolution updates as `items.py`. Inspect via desk → Server Script list.
- **`update_prices`, `get_inventory_from_sage`, `get_item_inventory_qty_on_hand_from_sage`** — still on `scheduler_events["all"]` (every cron tick). Chatty-cron pattern. Each one early-exits via `is_sync_enabled()` but the no-op cost is multiple DB reads per minute. Worth moving to a `daily` schedule or button-on-demand.
- **`update_item_job`** — every cron tick it `.save()`s a Scheduled Job Type and a Server Script. References `update_item_add_info_cron` (not in fixtures). On a fresh install this raises `DoesNotExistError` every minute.
- **POS Invoice cross-posting bug** (`pos_invoice.py`) — for each `custom_category` grouping key, the push loops ALL Company Sage Integrations rather than just the matching one. Means items get sent to wrong tenants if multi-Company is configured. The tax fix doesn't change this — it's a structural pre-existing bug.
- **`get_addition_prices_from_sage`** has `pricelist_ids` hardcoded fallback `["3796", "3795"]`. Used only when no Price List has a Sage ID stamped yet (effectively never after the first sync). Could be removed once all sites have run a price-list pull at least once.
- **`sales_invoice.py` hardcoded fallback** — `sales_rep_id = 740886` (Fisokuhle Radebe) when no Sales Person resolves on a credit note. Now that Sales Person pull stamps `custom_sage_rep_id`, this should rarely fire.

---

## File map

| Concern | Path |
|---|---|
| Accounts + Opening Balances | `erpnext_sbca/API/account.py` |
| Tax catalogue + resolver + price-pair | `erpnext_sbca/API/tax.py` |
| Journal Entry push (multi-row, on_submit) | `erpnext_sbca/API/journal_entry.py` |
| Item push (Physical: false, price math, tax resolve) | `erpnext_sbca/API/items.py` |
| Item details (price lists, additional prices, inventory) | `erpnext_sbca/API/item_details.py` |
| Sales / POS / Purchase Invoice push | `erpnext_sbca/API/sales_invoice.py`, `pos_invoice.py`, `purchase_invoice.py` |
| Supplier sync | `erpnext_sbca/API/supplier.py` |
| Customer sync (with default_price_list + sales_team) | `erpnext_sbca/API/customer.py` |
| Sales Person sync | `erpnext_sbca/API/sales_person.py` |
| Common helpers | `erpnext_sbca/API/helper_function.py` |
| Hooks (doc_events + scheduler_events + doctype_js) | `erpnext_sbca/hooks.py` |
| New DocTypes | `erpnext_sbca/erpnext_sbca/doctype/sage_tax/`, `item_tax_template_sage_map/`, `sage_account_opening_balance/` |
| Settings form + client script | `erpnext_sbca/erpnext_sbca/doctype/erpnext_sbca_settings/` |
| Item Tax Template Link filter | `erpnext_sbca/public/js/item_tax_template.js` |
