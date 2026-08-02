# nest_home: adding a Nest Home Tile to the library doesn't show it — the user's Layout decides

**Date:** 2026-05-28
**Site:** `Syncflo_internal_V16` (nesterp) — `nest_home` app
**Symptom:** Created a new `Nest Home Tile` (General Ledger), enabled, role-gated to Accounts roles. Hard-refreshed `/desk/nest-home` as the target user (Lyndsay, PreSales). Tile did **not** appear.

## Root cause

`nest_home/api.py::tiles_for_user` has **two** paths:

```python
def tiles_for_user(user=None):
    layout = resolve_layout(user)
    if layout:
        return _layout_tiles(layout)      # explicit tile list, in admin's order
    return _default_tiles(_user_roles(user))  # role-filtered library fallback
```

- `_default_tiles` → every enabled tile in the library, filtered by `allowed_roles` (empty = everyone). This is the fallback for users with **no** matching layout.
- `_layout_tiles` → **only** the tiles listed in that layout's `tiles` child table, and it **ignores `allowed_roles` completely**.

A user matches a layout by **Role Profile** first, then **Role**, else falls through to `Nest Home Settings.default_landing`. (`resolve_layout` + `boot._resolve_landing`.)

So if the user is on an explicit layout (PreSales, Administrator Profile, etc.):
- Putting a tile in the shared library does nothing for them.
- The `allowed_roles` gating you set on the tile does nothing for them.
- The tile shows **only** once you add it to **their** `Nest Home Layout.tiles`.

## Fix

Add the tile to the matching layout's child table:

```
Nest Home Layout (e.g. name="PreSales") → tiles child table → append row { tile: "NEST-TILE-00XX" }
```

Via MCP: `frappe_update` the `Nest Home Layout`, passing the **full** `tiles` array (child-table updates replace, not merge) with the new `{"tile": "NEST-TILE-00XX"}` appended.

## How to tell which path a user is on

List `Nest Home Layout` and check `role_profile` / `role`. As of 2026-05-28 nesterp has three layouts: `Administrator` (role System Manager), `Administrator Profile` (profile Administrator), `PreSales` (profile PreSales). Anyone whose profile/role matches one of these is on `_layout_tiles` and needs the tile added to that layout. Everyone else gets the role-filtered library.

## Verifying without impersonating

`nest_home.api.get_tiles` called over MCP runs as the **connector user** (`hello@syncflo.co.za`), which resolves to *its own* layout — so it does NOT verify another user's view. Instead, re-`frappe_get` the specific `Nest Home Layout` and confirm the tile row is present. (The `Nest Home Layout Tile` child doctype is read-permission-locked over the API; read the parent layout instead.)

## Design takeaway

If the intent were "any Accounts-role user sees GL automatically," explicit layouts defeat that — `allowed_roles` is only honoured on the library fallback. For layout-driven profiles, tile membership is manual per layout (or scripted via `defaults.ensure_layout_for_profile` / `api.build_profile_view`, see the app's CLAUDE.md v0.0.6 notes).
