# Website Route Redirect: the source pattern is slash-stripped before matching

**Date:** 2026-08-26
**Domain:** Frappe v16 (comstruct)
**Severity:** annoying (the rule saves fine and silently never fires)

## Symptom

Needed `/nest-home` to redirect to `/home`. Added a row to
**Website Settings → Route Redirects**:

```
source: ^/nest-home/?$
target: /home
status: 302
```

Saved cleanly. `curl https://comstruct.jh.frappe.cloud/nest-home` still returned
**404 Not Found**. Re-saved, tried again — still 404. Nothing in the logs, because
nothing errored: the rule simply never matched.

The existing rule on the same table *did* work:

```
source: ^/?$   ->  /home
```

which is what made it look like redirects were fine in general.

## Cause

`frappe/website/path_resolver.py` strips slashes from **both sides** before matching:

- the incoming path is stored as `self.path = path.strip("/ ")`, so `/nest-home`
  becomes `nest-home` — **no leading slash**
- each rule is compiled as `rule["source"].strip("/ ") + "$"`

`strip("/ ")` only removes leading/trailing `/` and spaces. In `^/nest-home/?$` the
first character is `^`, not `/`, so nothing is stripped and the pattern keeps its
literal `/`. It is then matched against `nest-home`, which has no leading slash, and
never matches.

`^/?$` works by accident: it happily matches the empty string that `/` strips down to.

## Fix

Write the source **without** a leading slash:

```
source: ^nest-home$
target: /home
```

Verified: `curl` now returns `302 -> https://comstruct.jh.frappe.cloud/home`.

Targets are unaffected — `/home` with the leading slash is correct there.

## Watch out

The redirect result is cached per path in the `website_redirects` cache hash, and a
previously served 404 can be cached at the CDN/proxy layer too. After fixing a pattern,
give it a moment or test with a cache-busting query before concluding it still fails —
this cost us a wrong diagnosis ("the redirect isn't firing") when the corrected rule was
in fact already live.

## Rule of thumb

Route-redirect sources are matched against the **stripped** path. Anchor them as
`^some-route$`, never `^/some-route$`.
