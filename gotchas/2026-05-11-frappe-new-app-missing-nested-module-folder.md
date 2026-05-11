# Frappe v16 — new custom apps need a nested `<app>/<module_snake>/` folder, even with one module

**Date:** 2026-05-11
**Domain:** custom-app / Frappe v16
**Severity:** day-killer (app won't install at all, or installs with no page / no DocType)

## Symptom

You build a new Frappe app from scratch (no `bench new-app` — handcoded, or AI-generated, or copy-paste-edited from another repo). The file layout looks like:

```
nest_crm_tasks/
├── pyproject.toml
└── nest_crm_tasks/                      ← app package
    ├── __init__.py
    ├── hooks.py
    ├── modules.txt                      ← "nest_crm_tasks"  (snake)  ← WRONG
    ├── fixtures/
    │   └── client_script.json           ← "module": "Nest CRM Tasks"
    └── page/                            ← page/ directly under app package
        └── lead_activity/
            └── lead_activity.json       ← "module": "Nest CRM Tasks"
```

`bench install-app nest_crm_tasks` then either:
- silently skips the Page / DocType / Client Script (`/app/lead-activity` 404s after install), or
- fails with `frappe.exceptions.DoesNotExistError: Module Def Nest CRM Tasks not found` when the fixture import runs.

## Cause

Three things must all agree, and a fresh-built app routinely gets one wrong:

1. **`<app>/modules.txt`** lists module names in **title-case** (`Nest CRM Tasks`), matching Frappe core / ERPNext convention. The snake-case form is for the folder, not the file.
2. **There must be a folder at `<app>/<module_snake>/`** — the snake_case of the title-case name. Pages live at `<app>/<module_snake>/page/...`, DocTypes at `<app>/<module_snake>/doctype/...`. Frappe's discovery walks this exact path.
3. **Every fixture/page/doctype JSON's `"module"` field** must exactly match the title-case string in `modules.txt`.

The trap unique to **single-module apps**: the app package and the module's snake-cased name are often identical (`nest_crm_tasks/` is both). The layout *looks* like the inner module folder is redundant — but it isn't. You still need `<app>/<app>/` (a duplicate-named inner folder).

## Fix

Lay the app out as:

```
nest_crm_tasks/                          ← repo root
└── nest_crm_tasks/                      ← app package (same name as repo)
    ├── __init__.py                      ← must contain `__version__ = "0.0.1"`
    ├── hooks.py
    ├── modules.txt                      ← "Nest CRM Tasks"  (title case)
    ├── patches.txt                      ← both section headers (see 2026-05-08 gotcha)
    ├── fixtures/
    │   └── client_script.json           ← "module": "Nest CRM Tasks"
    └── nest_crm_tasks/                  ← module folder (snake of "Nest CRM Tasks")
        ├── __init__.py                  ← empty marker file
        └── page/
            └── lead_activity/
                ├── __init__.py
                ├── lead_activity.json   ← "module": "Nest CRM Tasks"
                └── lead_activity.js
```

If you're fixing an already-scaffolded app: from the repo root,

```bash
mkdir -p <app>/<module_snake>
touch    <app>/<module_snake>/__init__.py
git mv   <app>/page <app>/<module_snake>/page
git mv   <app>/doctype <app>/<module_snake>/doctype 2>/dev/null   # if you have one
# leave fixtures/ at <app>/fixtures/ — that location IS correct
```

And edit `modules.txt` to use title-case.

## Why this is non-obvious

- **The error doesn't point at the cause.** "Module Def not found" sends you hunting in `tabModule Def` for the title-case name. You find it (or don't), and miss that the issue is `modules.txt` registered a *different* name.
- **`bench new-app` scaffolds it right.** When you go the official route, you never see this. When you handcraft / AI-generate / copy-paste a skeleton, the nested module folder is the first thing that gets dropped.
- **A single-module app *looks* like it should collapse.** `<app>/<app>/` (Python package) and `<app>/<app>/<module_snake>/` end up named the same when there's only one module. It's natural to drop one of them, and the wrong one to drop.
- **Fixtures import from `<app>/fixtures/`, NOT `<app>/<module>/fixtures/`.** So your Client Script fixture sometimes lands successfully while the Page silently doesn't — and that asymmetry is confusing. Half the app works.
- **The bench build succeeds** — flit / setuptools doesn't care about folder layout, it packages whatever Python files exist. The bench page says "Latest Version Deployed". The failure is at site-install discovery time.

## Detection recipe — before any `git push`

```bash
cd <app>
# 1. modules.txt must be title-case
cat <app>/modules.txt
# 2. snake_case of that line must exist as a folder
ls <app>/$(cat <app>/modules.txt | tr '[:upper:] ' '[:lower:]_')
# 3. every "module": references the same string
grep -rh '"module"' <app>/ | sort -u
# 4. __version__ exists
grep -c '__version__' <app>/__init__.py
```

All four of those must check out. (1) any text → (2) directory exists → (3) one unique value, matching (1) → (4) returns 1.

## See also

- Related: `gotchas/2026-05-08-frappe-module-folder-vs-modulestxt-mismatch.md` — the *rename* failure mode (folder left behind after renaming the module). Same root cause, different trigger.
- Related: `gotchas/2026-05-11-frappe-app-init-needs-version.md` — empty `<app>/__init__.py` is the other "won't install" trap on new apps.
- Related: `gotchas/2026-05-08-frappe-patches-txt-needs-both-section-headers.md` — bundle these checks together when scaffolding.
- Playbook: `playbooks/frappe-custom-app-v16.md` — the file layout section already documents this; the gotcha exists because it's easy to miss when working from memory.
- Project where this surfaced: `nest_crm_tasks` (`Syncflo-design/nest_crm_tasks`).
