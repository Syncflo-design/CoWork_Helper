# "The site takes 30 seconds to load" is ASP.NET cold start, not slow code

**Date:** 2026-08-04
**Domain:** ASP.NET WebForms on IIS (QMEasy, and any copy/paste-deployed site: SBMS, Fuse)
**Severity:** annoying

## Symptom

Users report the login page taking ~30 seconds. Any single page can be the victim; it is
always the first one somebody opens after a quiet spell or after a deploy. Try it again
straight afterwards and it is instant, which makes it look like it fixed itself.

```
live Login.aspx attempt 1: 703 ms      <- already warm when measured from a dev machine
live Login.aspx attempt 2: 130 ms
local, first hit after an app restart: 14 219 ms ... 58 808 ms
local, warm:                               72 ms
```

## Cause

Three things stacking up, none of them the page:

1. **Idle recycle.** A low-traffic app pool shuts down after 20 minutes (IIS default). The
   next visitor pays app-domain startup plus JIT.
2. **On-demand compilation.** With the source `.aspx` files deployed (copy/paste deploy),
   ASP.NET compiles each page on first request. `debug="false"` makes it *batch* compile
   the whole folder, so the first hit is slower still but every later page is ready.
3. **`debug="true"` in production.** The `Web.Release.config` transform that strips it only
   runs on a Visual Studio *publish* - copying files up ships the raw `Web.config`, so the
   live site runs unoptimised, uncached, with `customErrors mode="Off"` leaking stack traces.

## Fix

On the server, not in the app:

```xml
<!-- %windir%\Microsoft.NET\Framework64\v4.0.30319\Config\machine.config -->
<system.web>
  <deployment retail="true" />
</system.web>
```

Retail mode forces `debug=false` and hides detailed errors machine-wide, whatever the
pasted `Web.config` says - so the dev file can keep `debug="true"`.

```powershell
Install-WindowsFeature Web-AppInit
Import-Module WebAdministration
Set-ItemProperty "IIS:\AppPools\<pool>" -Name startMode -Value AlwaysRunning
Set-ItemProperty "IIS:\AppPools\<pool>" -Name processModel.idleTimeout -Value ([TimeSpan]::Zero)
Set-ItemProperty "IIS:\AppPools\<pool>" -Name recycling.periodicRestart.time -Value ([TimeSpan]::Zero)
Set-ItemProperty "IIS:\Sites\<site>"    -Name applicationDefaults.preloadEnabled -Value True
```

IIS then starts and warms the app itself, including after each paste-deploy, so no user
is ever the one who pays. On shared hosting with no IIS access, an uptime pinger every
10 minutes does the same job. Precompiling on publish removes step 2 entirely.

## Why this is non-obvious

Measuring from a dev machine almost always shows a *warm* app - you loaded a page a minute
ago, so you see 130 ms and conclude the users are exaggerating. The instinct is to hunt for
slow SQL or bloated pages; on QMEasy the login page is 38 requests and ~1.1 s fully loaded,
so the client side is innocent. The only way to see it is to force an app restart (touch
`Web.config`) and time the very next request.

Also worth knowing: several QMEasy pages call
`new WebClient().OpenRead("https://qmeasy.co.za")` in `Page_Load` as an "is there internet"
check. That is a synchronous outbound HTTP request on every single page load, and it will
hang the page for as long as the connection takes to fail. Not the cause of the 30 seconds,
but it is a second, permanent tax on every request.

## See also

- Related playbook: `playbooks/two-machine-workflow.md` (which machine owns C# work)
- Memory: `qmeasy_app.md` (live source location, MSBuild + aspnet_compiler verification)
