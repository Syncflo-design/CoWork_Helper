# Deploy fails at migrate with `No module named 'sqlglot.parsers'` — the Insights fork pins an old sqlglot and breaks Frappe itself

**Date:** 2026-09-29 · **Site:** ardmoreceramics.c.frappe.cloud (any bench carrying `Syncflo-design/insights`) · **Area:** Frappe Cloud deploy / Python dependencies · **Severity:** blocks every deploy

## Symptom

A routine deploy (here: nest_help 0.0.4, static files only) fails in the Migrate step:

```
File ".../sql_metadata/dialect_parser.py", line 17, in <module>
    from sqlglot.parsers.redshift import RedshiftParser
ModuleNotFoundError: No module named 'sqlglot.parsers'
```

The import chain starts in Frappe core (`frappe/desk/reportview.py` -> `sql_metadata`), so
nothing on the bench can even query the database. Frappe Cloud rolls the site back to the
previous bench; the site stays up on the old versions.

## Cause

- The deploy also pulled a newer Frappe v16, which now requires `sql_metadata~=3.0.1`.
- `sql_metadata` 3.x is built on sqlglot and needs `sqlglot>=30.12.0,<31`.
- Our Insights fork (branch `syncflo-custom-theme`, based on v3.12.2) still pinned
  `sqlglot<28.0.0`. Apps are pip-installed one after another, so Insights, installed after
  Frappe, **downgraded sqlglot underneath Frappe**. sqlglot < 30.12 has no `sqlglot.parsers`.

The app being deployed was irrelevant. Any deploy that picks up the newer Frappe fails.

## Fix

`insights/pyproject.toml`: `"sqlglot<28.0.0"` -> `"sqlglot>=30.12.0,<30.18"`.

Identical to upstream Insights (`version-3`, commits 89d381bbb 2026-08-18 and cf9af91e9
2026-09-05). Upstream changed the pin only, no code. The `<30.18` ceiling matters:
sqlglot 30.18 changed `Drop` and ibis 11 then emits `DROP TABLE IF EXISTS` with no table
name, which breaks DuckDB `create_table(overwrite=True)` and CSV import in Insights.

Push the fork, then a fresh Deploy.

**Confirmed 2026-09-29 15:35:** first migrate on a bench built after the push succeeded.
Site went Frappe 16.27.1 -> 16.35.1, ERPNext 16.28.0 -> 16.36.1. Six migrates before it
(one on 7 Sept, five on the day) all show **Recovered**.

## Reading the Frappe Cloud screens

- **Bench > Deploys = "Success"** only means the image built. It says nothing about the site.
- **Site > Updates** is where the truth is. `Recovered` = migrate failed and the site was
  rolled back to the old bench (site stays up, old versions). Row menu > view job > the
  migrate step holds the traceback.
- A migrate can only pass on a bench **built after** the fix reached GitHub. Re-running the
  site update against an older bench build just recovers again.
- Frappe Cloud had been failing quietly since 7 Sept. Nobody noticed because a recovered
  site looks healthy. Check Site > Updates after every deploy.

## Why this is non-obvious

- The traceback never mentions Insights. It reads like a broken Frappe release.
- The thing you deployed is not the thing that broke. Second time this fork has blocked
  every deploy on a Frappe bump (first: 2026-07-27, removed PostHog symbols).
- pip does not refuse the conflict on a bench: each app install only satisfies its own
  pins, last writer wins.

## How to check quickly next time

Compare the fork's pins with upstream before blaming the app you pushed:

- `https://raw.githubusercontent.com/frappe/insights/version-3/pyproject.toml`
- `https://raw.githubusercontent.com/frappe/frappe/version-16/pyproject.toml`
- `https://pypi.org/pypi/sql-metadata/json` (field `requires_dist`)

## Standing risk

The fork is frozen at Insights 3.12.2 plus three Syncflo commits. Every Frappe bump can
surface another incompatibility. Rebasing the three commits onto current `version-3` would
end this class of failure. Applies to every bench that carries the fork (Ardmore, Blomo).

## See also

- `sites/ardmore.md` entry 2026-07-27 (first fork incompatibility)
- `playbooks/insights-fork-themeing.md`
