# Insights v3 raw_sql with explicit `JOIN` routes child tables to the wrong schema

**Date:** 2026-05-06
**Domain:** Insights v3 (raw_sql / DuckDB query planner)
**Severity:** day-killer if you don't realise the SQL silently returns 0 rows

## Symptom

A native (raw_sql) Insights query that joins a parent doctype to its child table — e.g., `tabPurchase Invoice` and `tabPurchase Invoice Item` — returns **0 rows**, even though both tables have data when queried separately.

The generated DuckDB SQL Insights actually executes makes the bug visible:

```sql
WITH "tabPurchase Invoice Item" AS (
  SELECT * FROM "temp"."main"."tabpurchase_invoice_item"   -- ← empty staging schema
), "tabPurchase Invoice" AS (
  SELECT * FROM "site_db"."tabpurchase_invoice"            -- ← real ERPNext data
)
SELECT pii.item_code, pii.amount, pi.posting_date
FROM "tabPurchase Invoice Item" AS pii
JOIN "tabPurchase Invoice" AS pi ON pii.parent = pi.name
WHERE pi.docstatus = 1
```

The parent table goes to `site_db` (correct), but the child table goes to `temp.main` (an empty staging area). Inner join → no matches → 0 rows.

## Cause

The Insights query planner has different schema-resolution paths depending on whether the second table is referenced via an explicit `JOIN ... ON ...` clause or via a comma-separated `FROM A, B WHERE ...` (implicit/cross-join) clause. The explicit `JOIN` path mis-resolves the child table to `temp.main`. The comma-join path resolves both to `site_db` correctly.

Probing the same child table standalone resolves correctly to `site_db.tabpurchase_invoice_item` — so the table is fully populated and Insights knows how to find it; the bug is specifically in the multi-table `JOIN` planner.

## Fix

Use **implicit comma-join** (`FROM A, B WHERE A.x = B.y`) instead of explicit `JOIN ... ON ...` for any raw_sql Insights query that touches a child table.

```diff
- SELECT pii.item_code, pii.amount, pi.posting_date
- FROM `tabPurchase Invoice Item` pii
- JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
- WHERE pi.docstatus = 1
+ SELECT pii.item_code, pii.amount, pi.posting_date
+ FROM `tabPurchase Invoice Item` pii, `tabPurchase Invoice` pi
+ WHERE pii.parent = pi.name AND pi.docstatus = 1
```

Both forms are semantically equivalent (inner join), and on the comma form Insights' generated SQL routes both tables to `site_db`:

```sql
FROM "tabPurchase Invoice Item" AS pii, "tabPurchase Invoice" AS pi
WHERE pii.parent = pi.name AND pi.docstatus = 1
```

13 rows returned — same shape, correct data.

## Why this is non-obvious

- No error fires. The query "succeeds" — it returns 0 rows, which looks like "no matching data" rather than a bug.
- Both tables exist in DuckDB and resolve correctly when queried alone, so introspection ("does the table have rows?") yields a yes — the bug only appears in the multi-table planner.
- The MariaDB/Frappe REST side has no issue with explicit JOINs; this is specifically Insights' DuckDB-translation layer.

## See also

- Playbook: [`playbooks/insights-v3.md`](../playbooks/insights-v3.md)
- Related gotcha: [`2026-05-06-insights-dashboard-filter-needs-source-column.md`](2026-05-06-insights-dashboard-filter-needs-source-column.md)
