# Frappe Cloud — "install app on site" is the **Site → Update** button, not Bench → Apps → Install

**Date:** 2026-05-08
**Domain:** Frappe Cloud
**Severity:** annoying

## Symptom

Custom app has been added to the bench. The **Bench → Apps** screen shows it at "Latest Version Deployed". You expect the next click to be a per-site **Install** action, but:

- The **Update Bench** dialog (the modal that opens from Bench → Apps → Update) lists only apps with newer git commits than what's already deployed. It will *not* let you install an app onto a site from here.
- There's no obvious "Install on site" button on the Bench → Apps row.
- Going to the site's dashboard, you may see only an **Update Available** pill — no separate **Install App** button — and clicking it offers framework / ERPNext upgrades, not your custom app.

So the app is "deployed" but you can't seem to get it onto the site. You may be tempted to redeploy or SSH in.

## Cause

Frappe Cloud separates the *bench layer* (build/deploy of code) from the *site layer* (which apps a particular site has installed). When the bench gets a new app baked in, every site on that bench shows **Update Available**, and the site's Update dialog is what installs new bench-layer apps onto that site.

There is no separate "Install App" button on the site dashboard. The Update Site dialog *is* the install path for new apps that arrived in the bench.

## Fix

1. **Sites** tab in Frappe Cloud → click the site (e.g. `blomoplastics.jh.frappe.cloud`).
2. Click the **Update Available** pill (or the **Update Site** button if shown).
3. The dialog lists what will change: framework/ERPNext bumps + any newly-deployed-on-bench-but-not-yet-installed-here custom apps. Confirm.
4. ~2-5 min downtime, then the new app appears in `https://<site>/app/<workspace-or-page>`.

If the dialog does *not* offer your custom app even though the bench shows it as "Latest Version Deployed", trigger a fresh **Bench → Deploys → New Deploy** to rebuild the image, then retry the site update.

## Why this is non-obvious

- "Update Bench" and "Update Site" sound like variations of the same action but they're at different layers and do different things. Update Bench updates *apps* in the bench. Update Site updates the site's *connection* to the bench (and brings new apps across as part of that).
- The **Bench → Apps → Update** modal screenshots are misleading because they show "Latest Version Deployed" for every app already at the latest commit, which is most apps most of the time. So when your custom app is already at the latest commit but the site doesn't have it yet, the bench-level dashboard is a dead end and looks complete.
- Most other PaaS dashboards (Heroku, Vercel, etc.) have a per-environment "Install" or "Add to project" affordance that's separate from the version-update flow. Frappe Cloud collapses them into a single Update.
- The `bench install-app <app>` SSH command exists but is *not* what Frappe Cloud users normally need. Use the dashboard Update Site flow first; reach for SSH only when an actual error needs diagnosing.

## See also

- Gotcha: `gotchas/2026-05-08-frappe-module-folder-vs-modulestxt-mismatch.md` (site Update can also loop if the migrate fails silently).
- Gotcha: `gotchas/2026-05-06-frappe-cloud-update-vs-deploy-assets.md` (Update vs Deploy at the bench level).
- Playbook: `playbooks/frappe-custom-app-v16.md` § "Deploy to Frappe Cloud".
- `projects/quick_purchase_invoice/DEPLOY.md` § 5 — same flow, written up the first time we did this.
