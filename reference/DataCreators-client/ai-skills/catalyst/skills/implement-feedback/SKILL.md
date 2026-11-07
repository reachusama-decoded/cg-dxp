---
name: implement-feedback
description: Given Jira ticket IDs (e.g. AICAT-123 AICAT-124), fetch the Story details, create a feature branch per ticket, implement the changes in skills/*/SKILL.md and companion scripts, push the branch, and open a PR against cg-open-itg/catalyst. Use when the user says "implement feedback AICAT-XXX", "work on ticket AICAT-XXX", or provides ticket IDs after triaging the Jira board.
allowed-tools: Bash(bash:*) Bash(git:*) Bash(gh:*) Read Grep Glob Edit Write
metadata:
  tier: capability
  # lifecycle-phase "none" — maintainer tooling, not a DPLC phase skill
  lifecycle-phase: none
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [jira, github]
---

# implement-feedback

Fetch Jira Story details and implement the requested changes via feature branch + PR.

## Scope

**Allowed files:**
- `skills/*/SKILL.md`
- `skills/*/scripts/*`
- `skills/*/references/*`
- `docs/feedback/feedback.md` (mark item as done)

**Not allowed (flag for human review instead):**
- Core scaffolding (`_lib/`, `core/`, `clients/`)
- CI/CD config (`.github/`, `Makefile`, `bin/`)
- Repo config (`opencode.json`, `.gitignore`, `README.md`)
- Any file outside `skills/` or `docs/`

If a ticket requires changes outside the allowed scope, comment on the Jira ticket
explaining why and skip it. Do not attempt the change.

## Prerequisites

Ensure connection to Jira is established via .env credentials

Ensure `gh` is authenticated: `gh auth status`

## Workflow

### Step 1 — Fetch ticket details

Run the fetch script for all provided ticket IDs:

```bash
bash skills/implement-feedback/scripts/fetch_tickets.sh AICAT-123 AICAT-124
```

The script writes one JSON file per ticket to `/tmp/catalyst_ticket_<ID>.json`
and prints a summary of each Story.

### Step 2 — Plan changes per ticket

For each ticket:
1. Read the Story summary, description, skill name, context, and priority from the JSON
2. Locate the relevant skill: `skills/<skill-name>/SKILL.md`
3. If the skill directory does not exist, note it and skip (do not create new skills from implement-feedback — that's a separate authoring task)
4. Read the current SKILL.md and any companion scripts
5. Determine the minimal change that addresses the Story description
6. Tell the user: "For AICAT-XXX I plan to [describe change] in skills/<skill>/SKILL.md. Proceed?"

Wait for confirmation before making any edits.

### Step 3 — Implement on a feature branch

For each approved ticket:

```bash
# Create branch
git checkout main
git pull origin main
git checkout -b feedback/AICAT-123-<slug>
```

Where `<slug>` is a 3–5 word kebab-case summary of the ticket title.

Make the targeted edits to `skills/<skill>/SKILL.md` and/or companion scripts.
Keep changes minimal and focused — one concern per commit.

```bash
git add skills/<skill>/SKILL.md
git commit -m "feedback(AICAT-123): <one-line description of change>"
git push origin feedback/AICAT-123-<slug>
```

### Step 4 — Open PR

```bash
gh pr create \
  --repo cg-open-itg/catalyst \
  --base main \
  --title "feedback(AICAT-123): <ticket summary>" \
  --body "$(cat <<'EOF'
## Summary
<one paragraph describing the change>

## Jira
https://capitalgroup.atlassian.net/browse/AICAT-123

## Changes
- skills/<skill>/SKILL.md: <what changed>

## Testing
- [ ] Skill instructions are clear and unambiguous
- [ ] No changes outside allowed scope
- [ ] Existing behaviour not broken
EOF
)"
```

Capture the PR URL from the output.

### Step 5 — Link PR back to Jira

```bash
bash skills/implement-feedback/scripts/fetch_tickets.sh link AICAT-123 "<PR URL>" "<PR title>"
```

This calls the Jira remote link API to associate the PR with the ticket.

### Step 6 — Report to human

After all tickets are processed, print:

```
Done. Summary:

  AICAT-123  feedback/AICAT-123-<slug>  PR: <url>
  AICAT-124  feedback/AICAT-124-<slug>  PR: <url>

  Skipped (out of scope):
  AICAT-125  Requires changes to _lib/ — flagged for human review.
             Jira comment added.
```

## Commit message format

```
feedback(AICAT-XXX): <imperative verb> <what>
```

Examples:
- `feedback(AICAT-123): add retry logic to dplc-discovery on catalog timeout`
- `feedback(AICAT-124): clarify Databricks CLI version requirement in install docs`

## Error handling

- Ticket not found (404) → print error, skip ticket, continue
- Skill not found in repo → skip, add Jira comment explaining
- `gh` not authenticated → stop and tell user to run `gh auth login`
- PR already exists for branch → print existing PR URL, skip creation
- Git conflicts → stop, describe conflict, ask human to resolve
