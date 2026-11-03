# Claude Desktop (MSIX/Microsoft Store) hides claude_desktop_config.json under AppData\Local\Packages

**Date:** 2026-05-17
**Domain:** Claude Desktop / Cowork tooling
**Severity:** annoying (cost ~20 min the first time)

## Symptom

Claude Desktop pops a modal at startup:

```
Could not load app settings

There was an error reading or parsing claude_desktop_config.json:
Expected double-quoted property name in JSON at position 140 (line 5 column 41)
```

The "obvious" config location — `C:\Users\<user>\AppData\Roaming\Claude\claude_desktop_config.json` — **does not exist**. A recursive search of the user profile for `claude_desktop_config.json` turns up nothing under `Roaming\Claude`.

You spend ten minutes wondering whether the file the app is complaining about is real, then another ten convinced the error is referring to a phantom path.

## Cause

The Microsoft Store / MSIX-packaged build of Claude Desktop is sandboxed under a per-app package container. Anything the app writes to "AppData\Roaming\Claude" is silently redirected to the package's `LocalCache\Roaming\` shadow. The real path is:

```
C:\Users\<user>\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json
```

The `Claude_pzs8sxrjxfjjc` part is the MSIX Package Family Name and is stable across reinstalls of the Store build (but will differ from any non-Store install on the same machine).

## Fix

Find it explicitly with a recursive search that does NOT stop at the standard Roaming path:

```powershell
Get-ChildItem -Path C:\ -Filter claude_desktop_config.json -Recurse -Force 2>$null |
  Select-Object FullName
```

Then edit / replace that exact file. If you need to swap the whole file (e.g. syncing config from another machine), use a Copy-Item with `-Force`:

```powershell
Copy-Item "C:\path\to\new\claude_desktop_config.json" `
  "C:\Users\<user>\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json" -Force
```

Then **fully quit Claude** (right-click tray icon → Quit, or kill from Task Manager — closing the window is not enough) and relaunch.

## The stale-dialog twin

A second 10-minute black hole: the "Could not load app settings" error dialog can **outlive** the broken state of the file. If Claude failed to parse the config once, the dialog stays on screen even after the file has been fixed (or auto-regenerated to defaults by Claude itself). Validating the file at that point shows it's already valid JSON, which is confusing.

Always do a full quit-and-relaunch of Claude after touching the config — don't trust that the dialog reflects the *current* state of the file.

## Why this is non-obvious

- The error message references `claude_desktop_config.json` without a path, so the natural reflex is to look in `%APPDATA%\Claude\` — which on the Store build is a dead end.
- File Explorer with hidden items shown still doesn't help unless you happen to know to go to `AppData\Local\Packages\`.
- Cowork's `request_cowork_directory` tool refuses to mount anything under `AppData\Roaming\Claude` ("Cowork's internal session storage"), so Claude-the-assistant can't help directly with the config file unless the user copies it into a reachable folder first.
- The stale-dialog behavior makes you think the file is still broken when you've already fixed it — leading to extra "find another candidate file" wild goose chases.

## When syncing config between machines

If pulling a `claude_desktop_config.json` from another machine, you must rewrite:

- **Username paths** — anything like `C:\\Users\\<OldUser>\\...` in MCP server `args` needs to become `C:\\Users\\<NewUser>\\...`. Don't forget the JSON-escaped double backslashes.
- **`preferences.remoteToolsDeviceName`** — this names *this* device; never overwrite with the source machine's value.
- **`preferences.chromeExtension`** — the `pairedDeviceId` / `pairedDeviceName` are bound to the source machine's browser. Drop the block and re-pair from the target machine.

Other prefs (sidebarMode, scheduledTasksEnabled, webSearchEnabled, epitaxyPrefs) are safe to merge in.

## See also

- Related gotchas: `gotchas/2026-05-06-host-vs-bash-fs-sync.md` (Cowork file-tool limits)
- Microsoft docs on MSIX file-system redirection: https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-behind-the-scenes
