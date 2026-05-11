# Frappe — `<app>/__init__.py` must contain `__version__`, even if `pyproject.toml` sets `version` statically

**Date:** 2026-05-11
**Domain:** custom-app / Frappe v16
**Severity:** annoying (clear error, but easy to miss when scaffolding)

## Symptom

A freshly-handcoded Frappe app, with all the right files, refuses to install:

```
AttributeError: module 'nest_crm_tasks' has no attribute '__version__'
```

…or, on Frappe Cloud, the Bench → Apps page fails to import the app entirely and `bench get-app` raises during install. The repo builds and pushes fine; pip / flit doesn't complain.

## Cause

Frappe's app loader imports `<app>/__init__.py` and reads `__version__` — used by the desk's "About" dialog, by the Frappe Cloud apps listing, and by `bench update` to detect newer versions. The `version` declared in `pyproject.toml` is for the *package* (used by pip/flit); Frappe doesn't read it. Both must exist.

Handcoded / AI-generated apps routinely ship an **empty** `__init__.py` because the layout playbook doesn't make the requirement loud.

## Fix

```python
# <app>/__init__.py
__version__ = "0.0.1"
```

If using `pyproject.toml` with `dynamic = ["version"]` (per the v16 playbook), flit reads the same `__version__` value at build time — so one declaration covers both pip and Frappe.

```toml
# pyproject.toml
[project]
dynamic = ["version"]

[tool.flit.module]
name = "<app>"
```

## Why this is non-obvious

- The pip build doesn't fail. `flit build` happily wheelifies the app — it can find `__version__` via the dynamic resolver, or fall back to the version declared elsewhere in `pyproject.toml`, depending on how flit was invoked.
- The error message names the right symbol but in a generic way (`module has no attribute '__version__'`) — easy to read it as a Python import problem rather than a Frappe convention.
- `bench get-app` clones the repo and runs `pip install`, which succeeds, then tries to register the app in Frappe and *that* step is what fails. You see a green git clone followed by a red Frappe error, several seconds apart, and have to scroll up to find the cause.

## Detection recipe

```bash
test -s <app>/<app>/__init__.py && grep -q '__version__' <app>/<app>/__init__.py \
  && echo "__version__ present" \
  || echo "MISSING __version__ — Frappe install will fail"
```

## See also

- Related: `gotchas/2026-05-11-frappe-new-app-missing-nested-module-folder.md` — the other "won't install" trap. Bundle the checks together when scaffolding.
- Playbook: `playbooks/frappe-custom-app-v16.md` § `pyproject.toml` — mentions `__version__` but doesn't flag the consequence of omitting it.
- Project where this surfaced: `nest_crm_tasks` (`Syncflo-design/nest_crm_tasks`).
