# erpnext_sbca — Russell's Sage ↔ ERPNext bridge

**Importance: CRITICAL.** This app is a keystone of Russell's ecosystem. It is the live two-way bridge between ERPNext and Sage Business Cloud Accounting (SBCA). Do not disable, uninstall, or "tidy up" the scheduled jobs without checking with Russell first.

**Author:** Doreen (`doreen@9t9it.com` — 9t9it, a Frappe partner).
**App name:** `erpnext_sbca`. **Module name in ERPNext:** `Erpnext Sbca`.
**On the nesterp bench since:** 2026-04-11.
**Last audited:** 2026-05-12.

---

## What it does (plain English)

It keeps ERPNext and **Sage Business Cloud Accounting** in sync.

Every few minutes (every scheduler tick — roughly every 4 min) the app reaches out to Sage and:

**Pulls FROM Sage INTO ERPNext:**

- Items (the catalogue)
- Item categories (Sage's grouping → ERPNext's Item Groups)
- Price lists, additional/tiered prices
- Inventory levels (qty on hand)
- The chart of accounts
- Suppliers
- Sales orders
- Purchase orders

**Pushes FROM ERPNext BACK TO Sage:**

- Item price updates
- Item updates (a "job"-style push for batched item edits)

That's it — 11 scheduled jobs in total, each handling one of those flows.

*(That count and list predate the 2026-05 additions — see "Recent additions" below.)*

## Recent additions (2026-05-14)

The 2026-05 work added two features on top of the original sync set. Both are
gated by their own Settings toggles.

**Payment reconciliation.** A daily scheduled job (`API/reconciliation.py`)
pulls each customer's and supplier's closing balance from Sage and posts one
reconciliation Journal Entry per party per month to bring ERPNext's AR/AP into
line with Sage. New `Sage Reconciliation Log` DocType is the audit trail and
the idempotent guard. The "Sage Payments Clearing" account is auto-provisioned
per company. Gated by `push_reconciliation_on_schedule` (default OFF until
Pharoh's `ReconciliationSync` endpoints are live). Full design:
`PAYMENT_RECONCILIATION_DESIGN.md`; accountant-facing guide:
`Sage_ERPNext_Accounting_Sync_Guide.docx`.

**Customer / Supplier category -> group sync.** Two new scheduled pulls
(`get_customer_categories_from_sage` / `get_supplier_categories_from_sage`)
mirror Sage's customer/supplier categories into ERPNext as leaf Customer /
Supplier Groups, and the customer/supplier pulls now assign each party to its
category's group (previously: everyone dumped into the first leaf group).
Shared helper `ensure_party_group` in `helper_function.py`. Gated by
`sync_customer_categories` / `sync_supplier_categories`. See
`gotchas/2026-05-14-erpnext-party-group-must-be-leaf.md`.

Earlier 2026-05 work, also not covered by the 2026-05-12 audit above:
triggered pushes for Journal Entries and Stock Adjustments, and SO/PO
cancellation sync — see `hooks.py` `doc_events` and the
`Pharoh_*_Endpoint_Prompt.txt` files.

## Per-Company credentials

Each ERPNext Company that needs to sync with Sage gets its own row in the Settings child table. That row stores:

- Which **ERPNext Company** it represents
- The **Sage username + password + API key**
- The **OAuth bits** — auth URL, redirect-back URL, session id, provider, client type (always `webapp`)
- Optional Sage POS customer mapping (customer id + name)
- The tax id Sage should report against

So a single nesterp bench with three Companies can talk to three separate Sage accounts independently. Once a row exists and the OAuth login has run, syncing is automatic.

## What's on the nesterp bench right now (2026-05-12)

- The Settings panel **URL** field is empty.
- The credentials table has **zero rows** — no Company is wired up yet.
- All 11 scheduled jobs are enabled and firing every cron tick, but they exit immediately because they have nothing to authenticate as.
- No Scheduled Job Log entries visible — confirms the jobs are no-op-ing cleanly rather than erroring.

**Net:** the app is installed and ready, but nothing is actually syncing on nesterp. If syncing should be happening, someone (Doreen, or whoever has the Sage credentials) needs to fill in the Settings panel and run the one-time Sage login.

## What it would take to switch it on

1. Set the **URL** in `Erpnext Sbca Settings` (the base Sage API URL).
2. For each ERPNext Company that needs to sync, add a row to the `Company Sage Integration` child table with that Company's Sage login details (username, password, API key, auth URL, redirect URL, provider).
3. Trigger the OAuth handshake once — the app will redirect the user to Sage, Sage will redirect back, and a `session_id` gets written into the row. From that moment, the scheduled jobs have what they need and sync starts flowing.
4. Watch `Scheduled Job Log` for a few ticks to confirm jobs are completing successfully rather than erroring.

I can't do steps 1–3 from Cowork without the Sage credentials and without being able to follow the OAuth redirect. Doreen, or whoever set this up for the other companies, will know the exact values.

## Critical mental model — ERPNext is master, Sage is the ledger

**This is not a Sage-driven integration.** Russell also owns a separate commercial
product where Sage is the golden source — POs, SOs, and the item master all
originate in Sage and flow outward. That model is the opposite of this one.

In this build:

| Concern | Owner |
|---|---|
| Item master, stock, orders, manufacturing | **ERPNext** (master) |
| Financial ledger, VAT, SARS, payments | **Sage** (master) |

The flow is **ERPNext → Sage**, not the other way around. ERPNext creates the
transaction; Sage receives it and handles the financial/statutory side.

Practical consequences of this model:
- Sales invoices, purchase invoices, and orders are always **created in ERPNext**.
  Staff never need to touch Sage for operational transactions.
- Sage is where the **accountant lives** — payments, allocations, VAT, bank rec.
- If you ever find yourself thinking "should this originate in Sage?", the answer
  is almost certainly no — unless it is a pure-service invoice with no stock
  impact, which the monthly reconciliation handles automatically.
- Do not add logic that pulls document types (SO, PO, invoices, item master)
  **from** Sage into ERPNext as the authoritative source. That is the other product.

## Things to keep in mind

- The app **does not ship Custom Fields, Workspaces, Reports, or Print Formats.** It's pure background sync. All UI surface is the two DocTypes (Settings + the child credentials table).
- Credentials (`password`, `api_key`, `user_identifier`, `provider`) are stored encrypted as Frappe Password fields. They can't be read by simple SQL — you need `frappe.utils.password.get_decrypted_password()` from a bench console.
- The OAuth `redirect_back_to` URL is stored, not computed. **If the site URL ever changes** (e.g. apex `nesterp.co.za` DNS gets pointed somewhere, or the custom domain is renamed) the redirect URLs in every credential row need updating and Sage's OAuth client needs the new URL whitelisted.
- The source code lives in 9t9it's GitHub org, not in `Syncflo-design`. If a sync ever breaks and the cause is in the Python code (under `erpnext_sbca/API/*.py` on the bench), Doreen is the contact.

## What's running where (filesystem map)

Based on the scheduled job method paths, the Python code on the bench is laid out like:

```
~/frappe-bench/apps/erpnext_sbca/
└── erpnext_sbca/
    ├── API/
    │   ├── item_details.py    ← items, categories, prices, qty-on-hand, push updates
    │   ├── account.py         ← chart of accounts
    │   ├── supplier.py        ← suppliers
    │   ├── sales_order.py     ← sales orders
    │   └── purchase_order.py  ← purchase orders
    ├── erpnext_sbca/
    │   └── doctype/
    │       ├── erpnext_sbca_settings/
    │       └── company_sage_integration/
    └── hooks.py
```

The capital-A `API/` folder is unusual for Frappe (snake_case convention) but matches the actual method paths the scheduler is registered against.

## How I audited this (MCP recipe — for re-use)

Useful when auditing another inherited Frappe app:

```python
# 1. Find the app's module
frappe_list("Module Def",
    filters=[["app_name", "=", "erpnext_sbca"]],
    fields=["name", "module_name", "app_name"])

# 2. List its DocTypes
frappe_list("DocType",
    filters=[["module", "=", "Erpnext Sbca"]],
    fields=["name", "issingle", "istable"])

# 3. Inspect each DocT