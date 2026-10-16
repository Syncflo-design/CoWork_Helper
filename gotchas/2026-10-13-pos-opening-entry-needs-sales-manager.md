# Opening a till (POS Opening Entry) needs the Sales Manager role

**Date:** 2026-10-13
**Domain:** ERPNext v16 / POS / permissions
**Severity:** annoying

## Symptom

A presenter with Sales User and Accounts User opens Point of Sale, fills the "Create POS Opening
Entry" dialog and gets a permission error on Submit. Closing the till fails the same way.

## Cause

ERPNext's own permissions give POS Opening Entry and POS Closing Entry to Sales Manager (and the
accounts managers), not to Sales User. The dialog itself is shown to anyone who can open the page.

## Fix

Give the login Sales Manager (Russell sets roles on the demo site; Claude never does). Or avoid
the till: fuse_counter sells without opening entries.

## Why this is non-obvious

Making the sale needs only Sales/Accounts User; it is the opening float that needs the manager.

## See also

- `gotchas/2026-07-24-pos-outdated-opening-entry-blocks-till.md`
