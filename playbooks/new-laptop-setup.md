# Mirror this Claude Code set-up on another laptop (site visits)

Written 2026-10-26 for the Ardmore go-live trip. The whole working environment is four
things: the repos under `C:\ClaudeCode`, Claude's own folder under the user profile, the
Frappe connector config in the desktop app, and a handful of tools. Nothing lives on a
server except the repos (GitHub) and the deliverables on `S:`.

## What is where on the Dell (source machine)

| Piece | Path | Carries | Secret? |
|---|---|---|---|
| Repos + knowledge base | `C:\ClaudeCode\` (CoWork_Helper, nest_*, fuse_*, ...) | code, `CLAUDE.md`, `.claude\settings.local.json` (permission allow-list), `.claude\launch.json` | no |
| Claude folder | `C:\Users\User\.claude\` | `CLAUDE.md` (global rules), `settings.json`, `skills\`, `projects\C--ClaudeCode\memory\` (74 memory files + MEMORY.md), `plugins\` | `.credentials.json` = login token |
| Frappe connectors | `C:\Users\User\AppData\Roaming\Claude\claude_desktop_config.json` | the 7 MCP servers (frappe-ardmore, -nesterp, -demo, -comstruct, -blomo, -fuse-demo, -leader) with their site URLs and API keys | YES |
| Pharoh source | `C:\Users\User\source\repos\SageErpNextAPI` | C# gateway; only needed to change/publish Pharoh | publish profile holds server creds |
| Deliverables | `S:\Ardmore`, `S:\Products\...` | docs, generators | network share, needs VPN/LAN |

Memory is keyed by the PROJECT path (`C--ClaudeCode`), not by the Windows user, so it
works on the new laptop as long as the repos sit at `C:\ClaudeCode` again. The Python
path in memory (`C:\Users\User\AppData\Local\Programs\Python\Python313`) will differ if
the new Windows user is not `User` - adjust once.

## Before leaving the Dell

1. Commit and push the knowledge base (it had 7 uncommitted files on 2026-10-26):
   `cd /c/ClaudeCode/CoWork_Helper && git add -A && git commit -m "..." && git push origin main`
2. Any repo with local edits you do NOT want: `git checkout -- .` (nest_sales_history held
   the abandoned 0.1.5 edits). Any you do want: commit + push.
3. Copy to an external drive (Git Bash; the prefix stops MSYS turning `/E` into a path):
   - `MSYS_NO_PATHCONV=1 robocopy "C:\ClaudeCode" "E:\move\ClaudeCode" /E /XD node_modules .ruff_cache __pycache__`
   - `MSYS_NO_PATHCONV=1 robocopy "C:\Users\User\.claude" "E:\move\dot-claude" /E /XD sessions shell-snapshots file-history cache backups`
   - `MSYS_NO_PATHCONV=1 robocopy "C:\Users\User\AppData\Roaming\Claude" "E:\move\claude-app" claude_desktop_config.json`
   Keep the drive with you - the last file holds every site's API key.

## On the new laptop

1. Install: Claude desktop app; Git for Windows (Git Bash); Python 3.13 (tick "add to PATH")
   then `pip install ruff`; Node LTS (for `node --check`); .NET 9 SDK only if Pharoh may need
   a publish from site (then also Visual Studio + the publish profile).
2. Copy back: `E:\move\ClaudeCode` -> `C:\ClaudeCode` (same path, so memory and
   `settings.local.json` match); `E:\move\dot-claude` -> `C:\Users\<you>\.claude` (delete
   `.credentials.json` from the copy and sign in fresh); `claude_desktop_config.json` ->
   `C:\Users\<you>\AppData\Roaming\Claude\` BEFORE starting the app (or restart it after).
3. Start Claude, sign in, open the Code tab on `C:\ClaudeCode`. Check: the connectors list
   shows the seven frappe-* servers; a Frappe call works (list Company Sage Integration on
   frappe-ardmore); `~/.claude/CLAUDE.md` rules apply; memory recall mentions Ardmore.
4. Git identity: `git config --global user.name` / `user.email`, and sign in to GitHub once
   (HTTPS remotes; Git Credential Manager prompts in the browser on first push).
5. `S:` - map the share or accept that docs are read-only until back on the LAN.

## Coming back

Memory files written on the trip live only on that laptop: copy
`C:\Users\<you>\.claude\projects\C--ClaudeCode\memory\` back over the Dell's (newer wins),
and push CoWork_Helper from whichever machine edited it last. Repos: push from the laptop,
pull on the Dell.
