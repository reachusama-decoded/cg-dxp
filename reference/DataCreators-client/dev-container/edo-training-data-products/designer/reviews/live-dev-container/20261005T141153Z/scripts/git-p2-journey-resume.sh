#!/usr/bin/env bash
# Resume the Git phase 2 journey after PR #1 was opened (the contents call with ?ref=main returned HTML).
set -euo pipefail
export GH_PAGER=cat
REPO=CONMHAB_capgroup/dc-git-training; PR=https://github.com/CONMHAB_capgroup/dc-git-training/pull/1
W=/workspaces/edo-training-data-products/.local/live/20261005T141153Z/journeys/reconstruction/git-phase-two-proficient
export GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=credential.https://github.com.helper GIT_CONFIG_VALUE_0= \
  GIT_CONFIG_KEY_1=credential.https://github.com.helper GIT_CONFIG_VALUE_1='!gh auth git-credential'
OWNER=$(gh api user --jq .login); ID=$(gh api user --jq .id)
export GIT_AUTHOR_NAME=$OWNER GIT_COMMITTER_NAME=$OWNER GIT_AUTHOR_EMAIL="$ID+$OWNER@users.noreply.github.com" GIT_COMMITTER_EMAIL="$ID+$OWNER@users.noreply.github.com"
cd "$W/lab"
echo '## git-p2-04 upstream (colleague edit on main from a second clone; Zscaler blocks the contents API PUT)'
rm -rf "$W/colleague"; gh repo clone "$REPO" "$W/colleague"
( cd "$W/colleague" && printf 'Input classification: internal\n' >> contract.md && git commit -am "Contract: add input classification" && git push origin main && git log --oneline -1 )
echo '## git-p2-03 revision (review scenario: escalation contact and timezone)'
printf 'Escalation: Training support\n' >> contract.md
git commit -am "Contract: name the late-feed escalation contact (review response)"; git push
echo '## git-p2-04 integrate'
git fetch origin; git log --left-right --oneline HEAD...origin/main
if ! git merge origin/main -m "Merge origin/main: keep classification and delivery/escalation"; then
  git diff
  printf '# Holdings contract\n\nOwner: Training team\nGrain: one row per fund and instrument\nCurrency: USD\nDelivery: daily before 09:00 UTC\nInput classification: internal\nEscalation: Training support\n' > contract.md
  git add contract.md; git commit --no-edit
fi
git merge-base --is-ancestor origin/main HEAD && echo 'upstream is an ancestor of HEAD'
git push; cat contract.md; git log --graph --oneline --all
echo '## git-p2-05'
gh pr view "$PR" --json url,state,mergeable,reviewDecision,commits,reviews,headRefOid --jq '{url,state,mergeable,reviewDecision,headRefOid,commits:(.commits|length),reviews:(.reviews|length)}'
gh pr checks "$PR" || echo "gh pr checks exit $? (no CI configured in the sandbox)"
gh pr diff "$PR"
git status -sb; echo "$PR" > "$W/pr-url.txt"
