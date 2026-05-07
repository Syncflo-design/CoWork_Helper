# Insights v3 `code` operation runs Python, not SQL

**Date:** 2026-05-06
**Domain:** Frappe Insights v3
**Severity:** day-killer

## Symptom

Putting native SQL in the `code` operation of an `Insights Query v3` document fails with:

```
Line 1: SyntaxError: invalid syntax at statement: 'SELECT COUNT(*) AS shortfall_items FROM `tabBin` WHERE projected_qty < 0'
```

Every SQL keyword fails — `SELECT`, `<`, backticks, `LIKE '%x%'`, etc. Removing each one in turn just exposes the next one.

## Cause

That's a **Python** SyntaxError, not a SQL one. Insights v3 runs the `code` field through Python's parser (it expects ibis Python expressions). `SELECT` isn't a valid Python token, so it dies on the first word.

## Fix

Use operation type `"sql"` with field `"raw_sql"` (not `"code"`):

```diff
- {"type": "code", "code": "SELECT COUNT(*) FROM `tabBin`", "data_source": "Site DB"}
+ {"type": "sql", "raw_sql": "SELECT COUNT(*) FROM `tabBin`", "data_source": "Site DB"}
```

Inside `raw_sql` you have plain MariaDB: backticks for identifiers (`` `tabWork Order` `` for spaced names), single `%` in `LIKE`, `<`/`>`/`IN(...)` all work normally.

## Why this is non-obvious

The error mentions "syntax" and quotes the SQL, which leads you to "fix" each SQL token in turn. None of those edits help because the parser is Python. The doctype field is also called `code` and the official UI lets you write SQL-looking things in it — but those are ibis expressions like `con.sql("SELECT ...")`, not bare SELECT statements.

The decisive evidence: `frappe/insights/insights/insights/doctype/insights_query_v3/insights_query_v3.py` `execute()` explicitly checks for `op.get("type") == "sql" and op.get("raw_sql")` to extract native SQL.

## See also

- [`gotchas/2026-05-06-insights-data-query-empty-stub.md`](2026-05-06-insights-data-query-empty-stub.md)
- [`playbooks/insights-v3.md`](../playbooks/insights-v3.md)
- [`skills/frappe-insights-v3-dashboard/`](../skills/frappe-insights-v3-dashboard/SKILL.md)
- [Frappe Insights GitHub](https://github.com/frappe/insights)
