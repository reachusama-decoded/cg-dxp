---
name: process-feedback
description: Turn captured AI Catalyst feedback into prioritized Jira work. Imports the catalyst-feedback GitHub issues (or reads docs/feedback/feedback.md), sorts items by priority (HIGH/MED/LOW), shows the sorted list for human review, creates Jira Stories in project AICAT (label Customer-satisfaction), and comments the Jira link back on each source issue so the reporter can follow status. Use when the user says "process feedback", "create jira tickets from feedback", or "sort the feedback file".
allowed-tools: Bash(bash:*) Bash(gh:*) Bash(jq:*) Bash(python3:*) Read
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

# process-feedback

The intake stage of the AI Catalyst feedback loop:

```
catalyst-feedback        process-feedback                                  implement-feedback
(GitHub issues)   --->   import -> prioritize -> human review -> create    --->  build + PR
                         Stories, then comment the Jira link back on the
                         originating GitHub issue (status-back)
```

It connects *captured* feedback (the GitHub issues filed by `catalyst-feedback`)
to the *work* surface (Jira AICAT), and closes the loop back to the reporter so
they know which ticket to watch. Hand-curated items in
`docs/feedback/feedback.md` are also supported as a source.

## Prerequisites

- Jira connection via `.env` (`JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`).
- `gh` authenticated (`gh auth status`) — for importing issues and the status-back step.
- `jq` and `python3` on PATH (`jq --version`).
- **One-time:** create the dedup label so promoted issues aren't re-imported:
  ```bash
  gh label create promoted --color 5319e7 \
    --description "Feedback promoted to a Jira ticket" --repo cg-open-itg/catalyst
  ```

## Workflow

### Step 0 — Import captured feedback from GitHub (front bridge)

Pull the open `feedback`-labeled issues filed by the `catalyst-feedback` skill
into the pipeline:

```bash
bash skills/process-feedback/scripts/import_github_feedback.sh
```

This writes `/tmp/catalyst_github_feedback.md` in the feedback schema, carrying
each item's source `github-issue` and `github-url`. It **skips** issues already
labeled `promoted` (deduped) and pure `feedback-win` issues (morale, not work —
pass `--include-wins` to include them).

Skip this step if you're processing only the hand-curated
`docs/feedback/feedback.md`.

### Step 1 — Parse and sort

```bash
bash skills/process-feedback/scripts/parse_feedback.sh /tmp/catalyst_github_feedback.md
```

(Use `docs/feedback/feedback.md` instead to process hand-curated items.)

Outputs a JSON array sorted HIGH → MED → LOW to
`/tmp/catalyst_feedback_sorted.json`, and prints a summary grouped by priority
tier (GitHub-sourced items show their `github: #NN`).

### Step 2 — Display sorted list to human

Present the sorted list:

```
=== HIGH PRIORITY (N items) ===
1. [existing-skill-improvements] <title>
   skill: <skill>  reported-by: <handle>  github: #<n>
   <first line of description>
...
```

Then ask:
> "Review the sorted list above. Reply `create` to create Jira Stories for all items,
> or list specific numbers to create a subset (e.g. `1 3 5`), or `cancel` to exit."

### Step 3 — Create Jira Stories on approval

Optionally preview first with `--dry-run` (makes no Jira or GitHub changes):

```bash
bash skills/process-feedback/scripts/create_jira_stories.sh --dry-run /tmp/catalyst_feedback_sorted.json
```

When the human approves, create for real:

```bash
bash skills/process-feedback/scripts/create_jira_stories.sh /tmp/catalyst_feedback_sorted.json
# subset:
bash skills/process-feedback/scripts/create_jira_stories.sh /tmp/catalyst_feedback_sorted.json 1 3 5
```

For each created Story that came from a GitHub issue, the script also runs the
**status-back bridge**: it comments the Jira link on the originating issue, adds
the `promoted` label (dedup), and adds a Jira → GitHub remote link. The reporter
follows the AICAT ticket from there.

### Step 4 — Report results

```
Created:
  AICAT-XXX  [HIGH] <title>
             https://capitalgroup.atlassian.net/browse/AICAT-XXX
             -> reporter notified on cg-open-itg/catalyst#<n>
```

Then:
> "Stories created and reporters notified on their GitHub issues. Triage/rank at
> https://capitalgroup.atlassian.net/jira/software/c/projects/AICAT/boards/14045 .
> When ready, call `implement-feedback AICAT-XXX AICAT-YYY` with the ticket IDs to address."

## Priority rules reference

**Baseline by context field:**
| context | baseline |
|---|---|
| platform-architecture-improvements | HIGH |
| existing-skill-improvements | MED |
| onboarding-installation-improvements | MED |
| new-skill-requests | LOW |
| feedback-process-improvements | LOW |

GitHub-imported items default to `existing-skill-improvements` (MED); the
keyword upgrades below and the human review gate adjust the tier.

**Keyword upgrades** (title + context field, case-insensitive, only upgrade never downgrade):
- → HIGH: broken, fails, error, crash, blocked, critical, wrong, incorrect, missing, timeout, regression, failing
- → MED: slow, confusing, unclear, inconsistent, unexpected, difficult, improve, fix, incomplete, misleading
- → LOW: enhancement, suggestion, would be nice, consider, minor, cosmetic, style, future, wish

## Error handling

- `.env` missing/incomplete → the create script prints which vars are missing and exits before any API call (live runs only; `--dry-run` previews without creds).
- `gh` not authenticated → import fails fast; if it drops mid-run, the create script skips status-back but still creates the Story (and tells you).
- A Jira POST fails → print the error, skip that item, continue, report failures at the end.
- Feedback file not found → the parse script prints the expected path and exits.
- `promoted` label missing → status-back logs a one-line hint to create it; the Story is still created and the issue still commented.
