# A desk Page's CSS is served stale after deploy unless you bump its cache-buster

**Date:** 2026-08-18
**Domain:** Frappe / ERPNext / custom app / Frappe Cloud
**Severity:** looks like a broken build; wastes a deploy cycle

## Symptom

You change a desk Page's JS **and** its CSS, push, run a full Deploy, hard-refresh —
and the page renders as unstyled markup. Raw SVGs at their natural size, text with no
layout, elements stacked down the left.

The giveaway: the *new* markup is there. The JS did update. Only the styling is
missing, and other pages using the same stylesheet look fine.

## Cause

A desk Page's JS is a **fingerprinted bundle** — Frappe rebuilds it with a new hash
each deploy, so browsers always fetch the new one. A stylesheet linked from that JS is
not:

```js
link.href = '/assets/fuse_theme/css/fuse_home.css?v=' + encodeURIComponent(BUILD_MARKER);
```

The URL only changes when `BUILD_MARKER` changes. Edit the CSS, leave the marker alone,
and the browser re-requests a URL it already has cached and gets yesterday's file.
New JS, old stylesheet — which is exactly what unstyled markup looks like.

`fuse_home.js` even carries the instruction at the top of the file:

> Bump BUILD_MARKER every deploy. It is the only reliable way to tell whether Frappe
> Cloud actually rebuilt assets or served the cached bundle.

It was still missed, because the change felt like a CSS change rather than a JS one.

## Fix

**Bump the marker in the same commit as any CSS edit.** Treat them as one change, not
two — the marker is part of the stylesheet, not part of the JS.

And check every page actually has a buster. `fuse_floor.js` had none at all:

```js
// Was — a fixed URL, so a CSS change was permanently one cache away from the user
link.href = '/assets/fuse_manufacturing/css/fuse_floor.css';

// Now
link.href = '/assets/fuse_manufacturing/css/fuse_floor.css?v=' + encodeURIComponent(BUILD_MARKER);
```

## How to tell this apart from a real CSS fault

Open the stylesheet URL directly with a fresh query string
(`/assets/<app>/css/<file>.css?probe=1`) and look for the rules you just wrote. Present
there but not applied on the page means caching, not CSS.

## The other half of the same afternoon

Twice in one session Frappe Cloud showed **no "Update Available"** after a deploy was
expected. Both times the cause was the same and neither was a Frappe problem: the work
was **committed but not pushed**. `git status -sb` said `ahead 1` and `ahead 5`.

Frappe Cloud pulls from GitHub. A commit that has not been pushed does not exist as far
as it is concerned. When a deploy shows nothing to update, check `git log origin/main..HEAD`
before looking at anything else.

## See also

- `gotchas/2026-05-06-frappe-cloud-cdn-stale-assets.md` — the same failure from the CDN side
- `gotchas/2026-05-06-frappe-cloud-update-vs-deploy-assets.md` — Update skips `bench build`
