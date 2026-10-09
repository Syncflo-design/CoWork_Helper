# Restoring a Fuse demo profile rewinds naming series, so Intacct control IDs repeat

**Date:** 2026-10-08
**Domain:** Fuse (fuse_core gateway) / Sage Intacct / demo profiles
**Severity:** day-killer if it lands mid-demo

## Symptom

Not hit yet; found while building the NSE Energy profile. Every Fuse write sends a
deterministic control ID with `<uniqueid>true</uniqueid>`, built from
`(doctype, name, purpose)` in `fuse_core.rules.control_id_for`. Restore a profile backup and
the naming series winds back: the next certificate after the restore is `SC-00001` again,
so it carries the control ID of the rehearsal's `SC-00001`, which Intacct has already taken
and refuses as a replay.

## Cause

The demo site is restored over itself between demos (see `demo_profiles/PROFILES.md`), but
Intacct is not. Document names are only unique within one life of the site.

## Fix

Put something that changes per life of the document into the purpose, e.g. append
`doc.creation`: `purpose=f"{purpose}:{doc.creation}"`. A retry of the same document keeps the
same creation time, so replay protection still holds. (fuse_projects 0.2.0 did this for its
construction postings; 0.2.1 dropped those postings, so no shipped code does it today.)

The stock postings in fuse_manufacturing do NOT do this. They have not hit it only because
`post_movements` is off on the demo site. Turn it on for a demo that is restored between runs
and the second run's first movement will be refused.

## Why this is non-obvious

The control ID looks per-document and is per-document; the backup is what breaks the
assumption that a name is used once.

## Also learned the same day

- **leadertread-DEV has no task dimension on AP or AR lines.** `APBILLITEM` has no `TASKID`
  field, and reading `TASKID` from `ARINVOICEITEM` fails with a ValidationError. Project
  goes on the line; the BOQ section has to be held in Fuse.
- **`fuse_core.gateway.read` pages the WHOLE object before it truncates.** An unfiltered
  `ARINVOICE` read timed out the MCP call. Always pass a filter, e.g.
  `<lessthan><field>RECORDNO</field><value>30</value></lessthan>`.
- **A failed diagnostic read writes an Intacct Request Log row** on the site (successful reads
  are not logged). Keep that in mind before poking a site that is about to be backed up.
- leadertread-DEV accounts usable without department or location: `50300` COGS Services,
  `40900` Revenue - Other, `20191` Retainage Payable, `10191` Retainage Receivable.

## See also

- `S:\Products\Fuse\demo_profiles\PROFILES.md`
- `fuse_core/fuse_core/rules.py` (`control_id_for`)
