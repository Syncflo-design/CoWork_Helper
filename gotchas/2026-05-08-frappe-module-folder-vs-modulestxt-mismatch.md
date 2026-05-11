# Frappe v16 — `modules.txt` rename without folder rename causes a silent site-update loop

**Date:** 2026-05-08
**Domain:** custom-app / Frappe Cloud / ERPNext v16
**Severity:** day-killer

## Symptom

Frappe Cloud site shows an **Update Available** pill that never clears.

- Click the pill → Update dialog → "complete" → success notice → page reload → pill is back, offering the *same* update.
- Bench screen says **Latest Version Deployed** for the app, so the bench layer is fine.
- The site never actually catches up. New DocType / Page / Workspace content from the latest commit never lands. No clear error message anywhere.
- Trying to install a *different* app onto the site afterwards fails or never queues, because the site is stuck on this loop.

`bit me on:` `production_floor` (module renamed from "Floor Ops" → "RM Issue") on `blomoplastics.jh.frappe.cloud`.

## Cause

The module was renamed in `modules.txt` but the on-disk folder under the package wasn't moved.

```
production_floor/
├── modules.txt              ← contained "RM Issue" (renamed)
└── production_floor/
    └── floor_ops/           ← folder STILL named after the old module
        ├── page/
        └── workspace/
            └── production_floor.json   ← module: "RM Issue"
```

Frappe v16 expects the snake_case of the human module name as the folder name (`"RM Issue"` → `rm_issue/`). At migrate time it:

1. Reads `modules.txt`, registers/updates **Module Def "RM Issue"**.
2. Walks `production_floor/rm_issue/...` to discover DocTypes / Pages / Workspaces. Folder doesn't exist → 0 content found.
3. The `floor_ops/` folder, with its JSONs all pointing at `module: "RM Issue"`, is invisible to the discovery pass.
4. The migration partially completes, the site is left in an inconsistent state, and Frappe Cloud's update tracker re-flags it as needing update on the next page load. Hence the loop.

## Fix

Rename the folder to match the snake_case of the module name. Use `git mv` so the rename is recorded as a rename, not delete+add:

```bash
cd /c/path/to/<app>
git mv production_floor/floor_ops production_floor/rm_issue
git status      # confirm "renamed:" lines, not "deleted: + new file:"
git commit -m "Rename module folder floor_ops -> rm_issue to match modules.txt"
git push
```

Then on Frappe Cloud:
1. **Bench → Apps** → row for the app → **Update** (pulls the new commit into the bench).
2. **Bench → Deploys → New Deploy** (rebuilds the bench image, ~5 min).
3. **Sites → <site>** → click the **Update Available** pill → confirm.

The pill should clear after the update.

If an orphan **Module Def** with the *old* name still exists in the DB ("Floor Ops" in our case), it won't break anything but it's tidy to delete it from the desk: `https://<site>/app/module-def → Floor Ops → Delete`.

## Why this is non-obvious

- The **bench build** succeeds (flit packages whatever's on disk, doesn't care about folder vs `modules.txt` mismatches), so the bench shows "Latest Version Deployed". This makes you think the app side is healthy.
- The **site update dashboard** reports the update as *complete* — there's no red X, no error toast, no failure log to chase. It just silently re-flags itself afterwards.
- The Update Bench dialog only lists apps with newer git commits to pull, so when an app is already at the latest on the bench, this dialog hides it entirely. You can't tell from that screen whether the SITE has it or not. (Site install/update lives at **Sites → <site>**, not Bench → Apps.)
- All the Page / Workspace / DocType JSONs inside the wrongly-named folder still reference `module: "<correct name>"`. Reading any single JSON looks fine. The failure is at the *discovery* layer that maps "module name" → "folder name", which is invisible until you compare `modules.txt` to the directory listing.
- Easy to walk straight past during code review — the rename commit (`Rename module: Floor Ops → RM Issue`) sounds complete and the per-file diffs all check out.

## Tell-tale (how to spot this fast)

- Site's Update Available pill returns after every Update.
- `cat <app>/<package>/modules.txt` vs `ls <app>/<package>/` → snake_case of the contents of `modules.txt` is *not* in the folder listing.

## See also

- Playbook: `playbooks/frappe-custom-app-v16.md` — `modules.txt` section.
- Gotcha: `gotchas/2026-05-06-frappe-cloud-update-vs-deploy-assets.md` (different gotcha but same dashboard behaviour: update reports success while real work isn't done).
- Related: `projects/quick_purchase_invoice/DEPLOY.md` § "Common deploy issues" — covers the SSH-based fallback diagnostics.
