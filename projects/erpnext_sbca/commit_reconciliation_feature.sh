#!/usr/bin/env bash
#
# commit_reconciliation_feature.sh
# --------------------------------
# Stages and commits ONLY the Sage payment-reconciliation work across the two
# repos. It deliberately uses explicit per-file `git add` -- it never runs
# `git add -A` / `git add .` -- so the many unrelated pre-existing modified
# files in Erpnext-Sbca and CoWork_Helper are left untouched for you to handle
# separately.
#
# Usage (in Git Bash):
#   bash commit_reconciliation_feature.sh           # stage + commit
#   DRY_RUN=1 bash commit_reconciliation_feature.sh # stage + show, do NOT commit
#
# It does NOT push. Push commands are printed at the end for you to run when
# ready (the app code is safe to deploy -- the toggle defaults OFF).
#
# Override the base path if your checkout is not under C:\ClaudeCode :
#   BASE=/d/work bash commit_reconciliation_feature.sh
#
set -euo pipefail

BASE="${BASE:-/c/ClaudeCode}"
DRY_RUN="${DRY_RUN:-0}"

SBCA_REPO="$BASE/Erpnext-Sbca"
HELPER_REPO="$BASE/CoWork_Helper"

# --- files belonging to this feature, relative to each repo root --------------

SBCA_FILES=(
  "erpnext_sbca/API/reconciliation.py"
  "erpnext_sbca/erpnext_sbca/doctype/sage_reconciliation_log/__init__.py"
  "erpnext_sbca/erpnext_sbca/doctype/sage_reconciliation_log/sage_reconciliation_log.py"
  "erpnext_sbca/erpnext_sbca/doctype/sage_reconciliation_log/sage_reconciliation_log.json"
  "erpnext_sbca/API/journal_entry.py"
  "erpnext_sbca/erpnext_sbca/doctype/erpnext_sbca_settings/erpnext_sbca_settings.json"
  "erpnext_sbca/hooks.py"
)

HELPER_FILES=(
  "projects/erpnext_sbca/Pharoh_Reconciliation_Endpoint_Prompt.txt"
  "projects/erpnext_sbca/Sage_ERPNext_Accounting_Sync_Guide.docx"
  "gotchas/2026-05-14-cowork-edit-tool-flips-lf-to-crlf.md"
)

SBCA_MSG="feat(reconciliation): scheduled monthly Sage AR/AP balance reconciliation

- API/reconciliation.py: daily scheduled worker. Per Company Sage
  Integration row, pulls customer/supplier closing balances from Pharoh,
  computes delta vs ERPNext outstanding, and posts one reconciliation
  Journal Entry per party between the party control account and the
  'Sage Payments Clearing' account. Idempotent via Sage Reconciliation
  Log; per-party errors are logged and skipped.
- doctype/sage_reconciliation_log: new log DocType (company / party /
  period / delta / journal / status) -- also serves as the idempotent guard.
- erpnext_sbca_settings.json: new 'Run Reconciliation Sync' toggle plus a
  read-only 'Last Reconciliation Sync' timestamp, in the Scheduled section.
- hooks.py: register reconciliation.run_reconciliation on the daily scheduler.
- journal_entry.py: skip pushing JEs whose reference starts with
  'SAGE-RECON-' so reconciliation journals never loop back to Sage.

Gated by push_reconciliation_on_schedule; defaults OFF until Pharoh's
ReconciliationSync endpoints are live."

HELPER_MSG="docs(erpnext_sbca): reconciliation Pharoh prompt, accountant guide, gotcha

- Pharoh_Reconciliation_Endpoint_Prompt.txt: Copilot prompt for the two new
  ReconciliationSync endpoints (get-customer-balances / get-supplier-balances).
- Sage_ERPNext_Accounting_Sync_Guide.docx: accountant-facing guide, updated to
  match the shipped reconciliation behaviour.
- gotchas/2026-05-14-cowork-edit-tool-flips-lf-to-crlf.md: Edit-tool CRLF-flip
  gotcha plus confirmed host/bash truncation recurrence."

# --- helper -------------------------------------------------------------------

commit_repo () {
  local repo="$1" msg="$2"; shift 2
  local files=("$@")

  echo
  echo "=================================================================="
  echo " Repo: $repo"
  echo "=================================================================="

  if [ ! -d "$repo/.git" ]; then
    echo "  !! $repo is not a git repo -- skipping."
    return 0
  fi
  cd "$repo"

  # A stale .git/index.lock (left behind by a crashed or sandboxed git run)
  # blocks every git command in the repo. This script is a deliberate one-shot
  # commit, so if a lock is present we clear it -- but ONLY do this when you
  # are sure no other git process (a GUI, an editor's git integration, another
  # terminal) is mid-operation in this repo right now.
  if [ -f ".git/index.lock" ]; then
    echo "  ** stale .git/index.lock found -- removing it."
    echo "     (make sure no other git process is running in this repo)"
    rm -f ".git/index.lock"
  fi

  # Confirm every expected file exists before staging anything.
  local missing=0
  for f in "${files[@]}"; do
    if [ ! -e "$f" ]; then
      echo "  !! missing: $f"
      missing=1
    fi
  done
  if [ "$missing" -ne 0 ]; then
    echo "  !! one or more files missing -- skipping this repo."
    return 1
  fi

  # Stage only this feature's files.
  git add -- "${files[@]}"

  echo
  echo "  Staged for commit (this feature only):"
  git diff --cached --stat -- "${files[@]}" | sed 's/^/    /'

  echo
  echo "  Repo working tree (unrelated changes left UNSTAGED on purpose):"
  git status -s | sed 's/^/    /'

  if git diff --cached --quiet; then
    echo
    echo "  Nothing staged for this feature (already committed?) -- skipping commit."
    return 0
  fi

  if [ "$DRY_RUN" = "1" ]; then
    echo
    echo "  DRY_RUN=1 -- not committing. Re-run without DRY_RUN to commit."
    return 0
  fi

  git commit -m "$msg"
  echo
  echo "  Committed: $(git rev-parse --short HEAD) on $(git rev-parse --abbrev-ref HEAD)"
}

# --- run ----------------------------------------------------------------------

commit_repo "$SBCA_REPO"   "$SBCA_MSG"   "${SBCA_FILES[@]}"
commit_repo "$HELPER_REPO" "$HELPER_MSG" "${HELPER_FILES[@]}"

echo
echo "=================================================================="
echo " Done. Nothing has been pushed."
echo "=================================================================="
if [ "$DRY_RUN" != "1" ]; then
  echo " To push when ready:"
  echo "   cd \"$SBCA_REPO\"   && git push origin \$(git rev-parse --abbrev-ref HEAD)"
  echo "   cd \"$HELPER_REPO\" && git push origin \$(git rev-parse --abbrev-ref HEAD)"
  echo
  echo " The erpnext_sbca code is safe to deploy as-is: the"
  echo " push_reconciliation_on_schedule toggle defaults OFF, so the new"
  echo " daily job is a no-op until you switch it on per company."
fi
