# A DocType folder missing its controller .py hard-fails every site migrate

**Date:** 2026-05-21
**Domain:** Frappe / ERPNext / custom-app / Frappe Cloud
**Severity:** day-killer (blocks the whole site, including unrelated apps)

## Symptom

`bench build` / the bench deploy succeeds, but every **site** migrate aborts:

```
ModuleNotFoundError: No module named 'nest_home.nest_home.doctype.nest_home_layout_tile.nest_home_layout_tile'
ImportError: Module import failed for Nest Home Layout Tile, the DocType you're trying to open might be deleted.
```

On Frappe Cloud this looks like "deploys reach the bench but not the sites" — because the bench build never runs migrate, but each site update does, and it dies here. The crash takes down the *entire* site migrate, so other apps' changes (e.g. a sibling app deploying in the same run) never land either.

## Cause

A DocType folder shipped with its `.json` (and `__init__.py`) but **without its controller module** `<scrubbed_name>.py`. `frappe.model.sync` imports the DocType JSON, then `run_module_method("on_doctype_update")` calls `load_doctype_module(...)`, which tries to import the controller module and raises `ModuleNotFoundError`. The bench build doesn't import controllers, so it stays green and hides the problem until migrate.

## Fix

Add the missing controller. Every DocType folder needs all three of:

```
doctype/<scrubbed_name>/
  __init__.py
  <scrubbed_name>.json
  <scrubbed_name>.py   <-- the one that was missing
```

`<scrubbed_name>` = DocType name lower-cased, spaces -> underscores. The class is the DocType name with spaces removed (PascalCase). Even an empty child table needs it:

```python
import frappe
from frappe.model.document import Document


class NestHomeLayoutTile(Document):
    pass
```

After adding it: `git push` the app, redeploy, migrate clears.

## Why this is non-obvious

The build is green and the failure is on a *different* surface (site migrate) and often a *different* app than the one you were deploying — so it reads like a Frappe Cloud platform/propagation issue, not a code bug. The fix is trivial; finding it isn't, because nothing flags the missing file until import time.

Pre-deploy check for any new custom app: every folder under `*/doctype/` has `__init__.py` + `<name>.json` + `<name>.py`, and the class name in the `.py` matches the DocType name in PascalCase.

## See also

- Related gotchas: `gotchas/2026-05-20-frappe-deploy-overwrites-doctype-permissions.md`, `gotchas/2026-05-06-frappe-cloud-update-vs-deploy-assets.md`
- Apps: `Syncflo-design/nest_home`, `Syncflo-design/custom-subscription`
