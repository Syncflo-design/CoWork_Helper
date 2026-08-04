# "Outdated POS Opening Entry" blocks the till the day after one is left open

**Date:** 2026-07-24 · **Site:** ardmoreceramics.c.frappe.cloud · **Area:** ERPNext POS

## Symptom

A user clicks **Open POS** and, instead of the "Create POS Opening Entry" box,
gets a red dialog:

> **Outdated POS Opening Entry** — The current POS opening entry is outdated.
> Please close it and create a new one.

Dismissing it lets you sell, but on a *stale* (previous-day) opening entry, which
corrupts the day-end reconciliation. To non-technical users it reads as "the till
is broken" and they stop. **This is the most likely cause of an Ardmore user
report "we followed the guide and it failed."**

## Cause

ERPNext treats a **POS Opening Entry from a prior day that was never closed** as
outdated. You cannot cleanly open a new day until the old opening entry is closed
via a POS Closing Entry. It happens whenever someone opens the till and never runs
the day-end closing — routine during casual UAT. (In this instance `POS-OPE-2026-00040`
had been Open since 2026-07-20; discovered 2026-07-24.)

## Fix / recovery (per user, no admin needed)

1. Home screen → **POS Closing**.
2. In **POS Opening Entry** pick the old/outdated entry. Enter **Feet Through Door**
   (0 is fine for a past day). **Save → Submit → Yes**.
3. **Open POS** again → the normal "Create POS Opening Entry" box now appears →
   open the till and carry on.

Verified 2026-07-24 as `testpos@mail.com`: closed `POS-OPE-2026-00040`
(→ `POS-CLO-2026-00040`), reopened POS (clean dialog), opened fresh, completed a
sale (`ACC-PSINV-2026-00042`, Paid). Full transfer→open→sell chain confirmed.

## Prevention + doc

The real prevention is operational: **always run the day-end closing (Part 5)
before leaving.** Training guide `Ardmore Store Stock & POS Guide.docx` v1.2 now
covers this — Part 2 has the red-message recovery, rule 4 of "five things to
remember" states the consequence, and the FAQ has a row.

## Operator lesson

Don't leave a POS Opening Entry open at the end of a testing/handover session —
it silently becomes a next-day blocker for the whole team. If you open a till to
"leave it live," either close it when done or tell the client it must be closed
each night.
