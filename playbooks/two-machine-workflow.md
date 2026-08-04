# Two-Machine Dev Workflow — Playbook

How Russell splits **Visual Studio / C# (ASP.NET WebForms)** work across two machines/AI instances: one owns **design & layout**, the other owns **development, review & testing**. This playbook is the shared contract both instances read so they enforce the same boundaries instead of each guessing. Model-neutral on purpose — the two machines may run different models.

> **Applies to: VS / C# projects only** — e.g. QMEasy, SBMS, Fuse. **ERPNext / Frappe development is NOT split** — this machine (`C:\ClaudeCode`) remains the sole box for all Frappe/ERPNext work. Do not route Frappe tasks to the other machine.
>
> **Scope note:** Two machines for now. A third instance for **QA & Audit** is planned but **not active yet** — do not route work to it. When it lands, it gets its own section here.

## Prerequisites

- Both machines can reach the same source of truth: the git repo (branch-based handoff) and this `CoWork_Helper` knowledge base.
- **Design machine** (`C:\ClaudeCode`, this box) has the `ui-ux-pro-max` skill installed globally. See [`machine-role-split`] in auto-memory.
- Git is run **by Russell himself** from Git Bash (MINGW64) on whichever machine owns the change. Neither AI instance pushes, pulls, or commits — they hand Russell the exact commands. (Same rule as the root `CLAUDE.md`.)

## Mental model

The two instances **share no memory or context** — each only knows what is written down. So the workflow can't depend on "the other machine remembers"; it depends on three durable artifacts:

1. **The git branch** is the single source of truth for *code*. Work flows machine-to-machine as branch commits, never as edits to a live share both boxes poke at.
2. **This knowledge base** (`CoWork_Helper`) is the single source of truth for *conventions* — roles, gotchas, definition-of-done. Both instances read it at session start.
3. **Independent review.** The Dev/Test machine did not do the design; the Design machine does not certify its own output as shippable. Each stage is checked by the side that didn't produce it. That independence is the point, not overhead.

The real risk with two instances is **drift** (two boxes diverging on the same files) and **silent gaps** (each assuming the other covered something). The guardrails below exist to kill both.

## Roles

### Machine A — Design & Layout (this box, `C:\ClaudeCode`)
- Owns (for VS/C# projects): markup/UI (`.aspx`/`.ascx`), CSS, static layout, visual polish, front-end JS behaviour.
- **Also remains the sole machine for all ERPNext/Frappe development** — that work is not part of this split and stays here end-to-end.
- Tooling: `ui-ux-pro-max` skill for styles/palettes/components; browser preview for visual verification.
- Produces: a branch with UI/layout changes + before/after visual proof (screenshots).
- Does **not**: touch codebehind logic (`.cs`), DB schema, or business rules unless explicitly asked.

### Machine B — Development, Review & Testing (the other box)
- Owns: codebehind (`.cs`), data access, business logic, build (MSBuild), functional + regression testing, code review.
- Produces: working, built, tested code on the branch; review notes; test results.
- Reviews Machine A's UI changes for correctness (does the markup still bind, postback, validate) before they merge.

**Boundary rule:** Design and Dev **do not edit the same file in the same pass.** If a change needs both markup and codebehind, it's a handoff, not a simultaneous edit.

## End-to-end recipe

Most common flow — a UI/layout change to an existing feature:

1. **Design (Machine A):** cut a branch, make the UI/layout changes, run the preview, capture before/after screenshots. Syntax/markup-check. Commit (Russell runs git).
2. **Handoff → Dev:** push branch; note in the PR/commit what changed and what Dev needs to verify (see checklist).
3. **Dev/Review/Test (Machine B):** pull the branch, build, review the diff for correctness, run functional + regression tests, fix any codebehind fallout. Commit.
4. **Definition of Done met?** (see below) If yes → Russell merges. If no → back to whichever machine owns the gap.
5. **Capture** any non-obvious lesson as a `gotchas/` entry before closing.

## Handoff checklist

**Design → Dev** (Machine A hands over):
- [ ] Branch name + what changed, in one line.
- [ ] Which files touched (and confirmation: no codebehind edited, or exactly which).
- [ ] Before/after screenshots attached.
- [ ] Any server control IDs / bindings renamed or moved (Dev must check codebehind references).
- [ ] Known-unverified: anything Design couldn't test (data-backed states, auth-gated paths).

**Dev → done / back to Design** (Machine B hands over):
- [ ] Builds clean (MSBuild, no new warnings introduced).
- [ ] Diff reviewed for correctness — bindings resolve, postbacks fire, no null/exception paths opened.
- [ ] Functional test of the changed path + a regression pass on the feature.
- [ ] List of anything that needs a Design fix, with specifics.

## Definition of Done (per stage)

**Design stage is done when:**
- Change matches the request and doesn't drift the established look (unless a redesign was asked for).
- Renders correctly in the preview at target sizes; before/after captured.
- Markup is valid; no codebehind broken by renamed/removed controls.
- No stray inline styles that belong in the shared stylesheet; no unused assets left behind.

**Dev/Test stage is done when:**
- Builds and runs.
- The changed behaviour is tested and the surrounding feature still passes (no regression).
- Code reviewed by the instance that didn't write it.
- Edge/error paths considered (null data, unauthenticated, locked/submitted states).

**A change ships only when both stages are done.** Neither machine self-certifies past its own stage.

## Guardrails

- **One writer per file at a time.** The clobber risk is two machines editing the same `.aspx` on the share. Flow through branches, not the live UNC path.
- **Branch is truth for code; KB is truth for conventions.** Don't rely on cross-machine memory.
- **Neither AI runs git.** Hand Russell the exact Git Bash commands with forward-slash paths (`cd /c/ClaudeCode/<repo>`).
- **Independent check stays independent.** Don't let the authoring machine also be the sole reviewer of its own work.
- **Write the lesson down.** Anything non-obvious that bit a handoff → a `gotchas/` entry, so the *other* machine (which wasn't there) learns it too.

## Gotchas (link list)

- [`gotchas/2026-05-06-host-vs-bash-fs-sync.md`](../gotchas/2026-05-06-host-vs-bash-fs-sync.md) — host vs bash filesystem desync; relevant when a machine works over the mount.
- *(add handoff-specific gotchas here as they surface)*

## Diagnostic ladder

When a handoff goes wrong, check in order — first failure is your bug:

1. **Are both machines on the same branch/commit?** Drift almost always traces to one box working off stale code.
2. **Did the same file get edited on both sides?** Check the diff for clobbered work.
3. **Did Design rename/remove a control Dev's codebehind still references?** Build error or null at runtime.
4. **Was a "done" box actually met, or assumed?** Re-run the definition-of-done for the stage that owns the symptom.
5. **Is the convention written down?** If two instances disagree on a boundary, the KB is missing an entry — add it.
