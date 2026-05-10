# Frappe v16 — `patches.txt` must contain BOTH section headers, even if one is empty

**Date:** 2026-05-08
**Domain:** custom-app / Frappe Cloud / Frappe v16 framework
**Severity:** day-killer

## Symptom

Site update on Frappe Cloud fails at the **Migrate Site** step. The expanded job log shows DocType sync completing for every app, then:

```
Traceback (most recent call last):
  ...
  File "/home/frappe/frappe-bench/apps/frappe/frappe/migrate.py", line 143, in run_schema_updates
    frappe.modules.patch_handler.run_all(
        skip_failing=self.skip_failing, patch_type=PatchType.post_model_sync
    )
  File ".../patch_handler.py", line 105, in get_patches_from_app
    return parse_as_configfile(patches_file, patch_type)
  File ".../patch_handler.py", line 136, in parse_as_configfile
    frappe.throw(_("Patch type {} not found in patches.txt").format(patch_type))
frappe.exceptions.ValidationError: Patch type PatchType.post_model_sync not found in patches.txt
```

Frappe Cloud auto-runs **Recover Site** after the failure, so the dashboard reports the update as done from the user's perspective — but the **Update Available** pill on the site reappears on the next page load. Loop forever.

`bit me on:` `wo_wip` v1.2.0 going live on `blomoplastics.jh.frappe.cloud`. Cost half a day to track down.

## Cause

A custom app's `patches.txt` was written with only one section header:

```ini
[pre_model_sync]
wo_wip.patches.v1_2.rename_operator_session_to_run
```

Frappe iterates every installed app and calls `parse_as_configfile(patches_file, patch_type)` separately for `pre_model_sync` and `post_model_sync`. The parser is implemented strictly: if the requested section header is **missing**, it raises `ValidationError`, even if you genuinely have no post_model_sync patches to run. There is no fallback to "treat absent section as empty".

## Fix

Always include both section headers, even if one section has no patches under it:

```diff
  [pre_model_sync]
  wo_wip.patches.v1_2.rename_operator_session_to_run
+
+ [post_model_sync]
```

(Blank line and trailing-blank-section is fine — Frappe just needs the header to exist.)

Then push, Bench → Apps → Update on the app row, Site → Update Available pill → confirm. Migrate Site goes green.

## Why this is non-obvious

- The `pre_model_sync` patches **run successfully first** (`Success: Done in 3.424s`). The successful pre-sync run is super misleading because it proves the patches.txt file is parseable — you naturally assume the file format is correct. The post-sync pass is a **second** call to `parse_as_configfile` that fails on the missing header that the first call didn't need.
- Error message reads like a code path issue (`PatchType.post_model_sync not found in patches.txt`) — it sounds like Frappe is trying to find a specific patch *named* `post_model_sync`, not that the file is missing a section header. You waste minutes searching for a misspelled patch import path.
- Frappe Cloud's auto-Recovery hides the failure in the user-facing UI. The dashboard only shows the **Update Available** pill come back; you have to dig into Bench → Jobs → click into the failed Update Site job → expand the **Migrate Site** step to see the traceback. Without that path the symptom looks like "the site won't take the update for no reason".
- The `frappe-custom-app-v16` playbook describes patches.txt as "headers `[pre_model_sync]` / `[post_model_sync]`" but doesn't make the BOTH-required rule explicit. Easy to read it as "use whichever headers apply".
- An entirely empty `patches.txt` is also valid — Frappe doesn't trip on no sections at all (the loop just iterates zero times). It's specifically the case where you have ONE section that explodes. So existing apps with empty patches.txt files work fine and provide no warning.

## Tell-tale (how to spot this fast)

`grep -c '\[' apps/<your_app>/<your_app>/patches.txt` should return `2`. If it returns `1`, you've got this gotcha.

## See also

- Playbook: `playbooks/frappe-custom-app-v16.md` — should be amended to call out the both-headers rule explicitly.
- Gotcha: `gotchas/2026-05-08-frappe-cloud-site-update-is-the-app-install-path.md` — the gotcha that explains where to find the failure log when Site Update silently rolls back.
- Gotcha: `gotchas/2026-05-06-frappe-cloud-update-vs-deploy-assets.md` — different issue but same dashboard pattern (success notice while real work didn't actually finish).
- Source: `frappe/modules/patch_handler.py` `parse_as_configfile()`.

## Template snippet (for new apps)

Always start `patches.txt` with this — it's safer to leave the empty section than to omit it and add it back later:

```ini
[pre_model_sync]
# patches that run BEFORE DocType sync go here
# example: <app_name>.patches.v1_2.rename_some_doctype

[post_model_sync]
# patches that run AFTER DocType sync go here
```
