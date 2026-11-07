#!/usr/bin/env bash
# Git phase 2 live journey against CONMHAB_capgroup/dc-git-training, following the learner README.
set -euo pipefail
REPO=CONMHAB_capgroup/dc-git-training
W=/workspaces/edo-training-data-products/.local/live/20261005T141153Z/journeys/reconstruction/git-phase-two-proficient
# gh as credential helper for this process only; no global Git config.
export GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=credential.https://github.com.helper GIT_CONFIG_VALUE_0= \
  GIT_CONFIG_KEY_1=credential.https://github.com.helper GIT_CONFIG_VALUE_1='!gh auth git-credential'
OWNER=$(gh api user --jq .login); ID=$(gh api user --jq .id)
export GIT_AUTHOR_NAME=$OWNER GIT_COMMITTER_NAME=$OWNER GIT_AUTHOR_EMAIL="$ID+$OWNER@users.noreply.github.com" GIT_COMMITTER_EMAIL="$ID+$OWNER@users.noreply.github.com"
BRANCH=training/conmhab-delivery-deadline
cd "$W"
echo '## git-p2-01'; gh repo clone "$REPO" lab; cd lab
git remote -v; git branch -vv; gh auth status 2>&1 | grep -E 'account|Active'
echo '## git-p2-02'; git switch -c "$BRANCH"
sed -i 's/^Delivery: daily$/Delivery: daily before 09:00 UTC/' contract.md
git diff; git commit -am "Contract: delivery deadline is 09:00 UTC"; git push -u origin "$BRANCH"
PR=$(gh pr create --repo "$REPO" --base main --head "$BRANCH" --title "Clarify holdings delivery deadline and timezone" \
  --body "Before: \`Delivery: daily\` gave no deadline or timezone. After: daily before 09:00 UTC. Checked: \`git diff main\` touches only contract.md's Delivery line.")
echo "PR=$PR"; gh pr diff "$PR"
echo '## git-p2-04 upstream (colleague edit on main through the API)'
SHA=$(gh api "repos/$REPO/contents/contract.md?ref=main" --jq .sha)
printf '# Holdings contract\n\nOwner: Training team\nGrain: one row per fund and instrument\nCurrency: USD\nDelivery: daily\nInput classification: internal\n' | base64 -w0 > /tmp/upstream.b64
gh api -X PUT "repos/$REPO/contents/contract.md" -f message="Contract: add input classification" -f branch=main -f sha="$SHA" -f content="$(cat /tmp/upstream.b64)" --jq .commit.sha
echo '## git-p2-03 revision (review scenario: escalation contact and timezone)'
printf 'Escalation: Training support\n' >> contract.md
git commit -am "Contract: name the late-feed escalation contact (review response)"; git push
echo '## git-p2-04 integrate'
git fetch origin; git log --left-right --oneline HEAD...origin/main
git merge origin/main -m "Merge origin/main: keep classification and delivery/escalation" || {
  git diff
  printf '# Holdings contract\n\nOwner: Training team\nGrain: one row per fund and instrument\nCurrency: USD\nDelivery: daily before 09:00 UTC\nInput classification: internal\nEscalation: Training support\n' > contract.md
  git add contract.md; git commit --no-edit; }
git merge-base --is-ancestor origin/main HEAD && echo 'upstream is an ancestor of HEAD'
git push; cat contract.md
echo '## git-p2-05'
gh pr view "$PR" --json url,state,mergeable,reviewDecision,commits,reviews --jq '{url,state,mergeable,reviewDecision,commits:(.commits|length),reviews:(.reviews|length)}'
gh pr checks "$PR" || echo "gh pr checks exit $? (no CI configured in the sandbox)"
git status -sb; echo "$PR" > "$W/pr-url.txt"
