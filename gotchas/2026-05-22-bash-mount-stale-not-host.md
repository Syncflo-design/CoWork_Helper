# Cowork host↔bash desync, inverse direction: the bash mount served a STALE, truncated copy while the host Read tool was correct

**Date:** 2026-05-22
**Domain:** Cowork-mode tooling (Read/Write/Edit on Windows host vs. `mcp__workspace__bash` Linux mount)
**Severity:** annoying (cost ~15 min, nearly mis-shipped a "syntax error" that didn't exist)

## Symptom

Edited `nest_crm_tasks/.../page/party_activity/party_activity.js` with the Edit tool. Host-side `Read` showed the full, correct, balanced 559-line file. But `node --check` over the bash mount failed:

```
.../party_activity.js:473
            frappe.db.insert(pay
                             ^^^
SyntaxError: missing ) after argument list
```

`wc -l` from bash showed **472 lines**, cut mid-statement. `stat` showed an **old mtime (2026-05-18)** — i.e. the mount was serving a pre-edit cached copy, not even the original full file.

## Cause

The host filesystem had the correct, current file (the Edit tool writes to the Windows host and `Read` reflects it). The Linux mount used by `bash` was serving a **stale, partially-cached** version and never picked up the day's writes. This is the existing host↔bash sync gotcha, but in the **opposite direction** from the documented one: here **bash was wrong and the host Read was ground truth**.

## Fix

Don't try to validate through the stale mount, and don't trust its "truncation" as real.

1. `request_cowork_directory` to **remount did NOT bust the cache** — bash still showed the old mtime/length.
2. The **outputs mount is a separate mount and stays fresh.** Probe it first (write a token via Write, `cat` via bash). Then transfer the real on-disk content there and check it:

```
# host Write tool: copy the verified-correct file content to outputs/check.js
# then, in bash (outputs mount is fresh):
cd /sessions/<id>/mnt/outputs && node --check check.js && echo OK
# sanity: balanced delimiters
node -e "s=require('fs').readFileSync('check.js','utf8');c=x=>s.split(x).length-1;console.log(c('{'),c('}'),c('('),c(')'),c('['),c(']'))"
```

A clean check on that copy validates the host content, since the copy is built from a direct host `Read`.

## Why this is non-obvious

The existing gotcha (`2026-05-06-host-vs-bash-fs-sync.md`) says "trust the bash view as ground truth." That advice is **direction-dependent** — it assumed the *Write tool* truncated on disk. This time the Write/Edit succeeded on the host and **bash was the stale liar**. Blindly following the old rule would mean "fixing" a file that was already correct, or reporting a phantom syntax error to the user. Two contradictory failure modes share one symptom (`node --check` fails after a successful edit); the only way to disambiguate is to compare host `Read` against bash and check the mount's `mtime`.

Also: remounting the folder does **not** reliably refresh the bash cache. The fresh **outputs mount** is the reliable escape hatch.

## See also

- `gotchas/2026-05-06-host-vs-bash-fs-sync.md` (the original, opposite-direction case)
- Rule of thumb: when host `Read` and bash disagree, check `stat` mtime. Whichever reflects your just-made edit is the truth; route tooling/syntax checks through the **outputs** mount if the working-folder mount is stale.
