#!/usr/bin/env bash
# Day 2 Git demo: the six steps of the anchor's Git section on a throwaway repository
# (recreated in sandbox/ every run; gitignored). Needs only `git`.
set -euo pipefail
cd "$(dirname "$0")"
step() { printf '\n\033[1;34m== %s ==\033[0m\n' "$*"; }
rm -rf sandbox && mkdir sandbox && cd sandbox
step "1. A repository and a first commit"
git init -q -b main && git config user.name 'Data Creator' && git config user.email 'creator@example.com'
printf '# EOD prices: data contract\n\nOwner: pricing data team\n' > contract.md
git add contract.md && git commit -q -m 'Add the EOD prices contract skeleton'
git log --oneline
step "2. What changed: status and diff"
printf '\n## Rules\n\n- price_gbp = price_local * fx_rate (derive)\n' >> contract.md
git status --short
git diff
step "3. A branch, and a commit on it"
git switch -c feature/sttm-rules
git add contract.md && git commit -q -m 'Add the price_gbp derive rule to the STTM'
git log --oneline --graph --all
step "4. The merge: what GitHub does when the pull request is approved"
git switch -q main && git merge --no-ff -q -m 'Merge feature/sttm-rules: the price_gbp rule' feature/sttm-rules
git log --oneline --graph
step "5. What never goes in: a secrets file, hidden by .gitignore"
printf 'DATABRICKS_TOKEN=dapi-not-a-real-token\n' > .env
git status --short
printf '.env\n' > .gitignore && git add .gitignore && git commit -q -m 'Ignore the local secrets file'
echo '--- after .gitignore:' && git status --short
step "6. Undo: restore an edit, revert a commit"
printf 'oops\n' >> contract.md && git status --short && git restore contract.md && echo '--- after restore:' && git status --short
printf 'oops\n' >> contract.md && git commit -qam 'A mistake' && git revert --no-edit HEAD >/dev/null
git log --oneline -3 && tail -1 contract.md
