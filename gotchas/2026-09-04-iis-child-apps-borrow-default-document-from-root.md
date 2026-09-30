# IIS: /za and /zademo borrow their default document from the ROOT web.config

**Date:** 2026-09-04
**Domain:** IIS / ASP.NET WebForms — mydatafusion.online (marketing site root + Data Fusion app at `/za`, `/zademo`)
**Severity:** OUTAGE — the live app returned **403 Forbidden** for every user until fixed

## Symptom

After publishing the revamped marketing site, `https://mydatafusion.online/za/` and
`/zademo/` returned the grey IIS page:

```
403 - Forbidden: Access is denied.
You do not have permission to view this directory or page using the credentials that you supplied.
```

The marketing site itself (`/`) was fine. Nothing in the app had been touched.

## Cause

The Data Fusion app (`SBMS` codebase) has **no `<defaultDocument>` in its own
web.config**, and its landing page is `Login.aspx` — not one of IIS's built-in
defaults (`Default.aspx`, `index.html`, …). So `/za/` only resolves because the
**root site's** `web.config` lists `Login.aspx` and IIS config inherits down into
child applications.

Two things then broke that inheritance, one after the other:

1. The publish overwrote the server's root `web.config` with the project copy,
   whose default-document list was `index.aspx` only.
2. Trying to "protect" the child apps, the root `<system.webServer>` was wrapped in
   `<location path="." inheritInChildApplications="false">`. That is the textbook
   pattern for stopping root settings leaking into child apps — and it is exactly
   wrong here, because the child apps *depend* on inheriting the default document.

Result: `/za/` had no default document → IIS 403.14 (directory listing denied),
shown to the public as the generic 403 page.

The generic 403 page hides the substatus; the IIS log (`sc-substatus` column,
`C:\inetpub\logs\LogFiles\W3SVC<site-id>\`) is the only place that shows `403 14`.
Each site has its own `W3SVC<id>` folder — the first log grabbed was the Fuse
site's and had no `/za` lines at all.

## Fix

Root `web.config` on the server (and the project copy, so publish carries it):

```xml
<system.webServer>
  <!-- Inherited by /za and /zademo, which have no defaultDocument of their own.
       Login.aspx MUST stay here or /za/ returns 403.14. -->
  <defaultDocument>
    <files>
      <add value="index.aspx" />
      <add value="Login.aspx" />
    </files>
  </defaultDocument>
  ...
</system.webServer>
```

No `<location … inheritInChildApplications="false">` wrapper. No `<clear />`
(it would also strip anything else the children happen to rely on).

## Rules going forward

- **Never put `inheritInChildApplications="false"` on the mydatafusion.online root
  config.** `/za` and `/zademo` are child apps that rely on inheriting from it.
- **Never remove `Login.aspx` from the root default-document list.** It looks
  unrelated to the marketing site — it isn't.
- Before publishing the marketing site, diff the project `Web.config` against the
  server's `C:\inetpub\wwwroot\MyDataFusion\Web.config`. Anything on the server
  that isn't in the project is there because the children need it.
- Publish profile is FileSystem to `C:\inetpub\wwwroot\MyDataFusion` with
  `DeleteExistingFiles=False` — keep it False; `/za` and `/zademo` may sit inside
  that folder.
- The durable fix is to give the app its **own** `<defaultDocument>` with
  `Login.aspx` in `SBMS/Web.config`, so it stops depending on the root. Do that in
  the next SBMS release (see `projects/` — SBMS_v2). Until then the root config
  carries it.
- A 403 with the generic message is not diagnosable from the browser. Get the
  substatus from the **right site's** IIS log first, then change config.

## Related

- `gotchas/2026-08-18-page-css-served-stale-when-the-cache-buster-is-not-bumped.md`
  (same deploy, different lesson)
- Memory: `mydatafusion-website`
