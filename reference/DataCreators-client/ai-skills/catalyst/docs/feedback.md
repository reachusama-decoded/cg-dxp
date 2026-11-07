# AI Catalyst Feedback

How we capture substantive feedback on AI Catalyst skills and turn it into action.

## Principles

- **Words, not ratings.** 1–5 scores don't tell you *why*. Only words do. So the skill asks for words.
- **Silence means satisfied.** If the user has nothing to say, nothing gets filed. No noise issues.
- **Zero user setup.** Users already have `gh` authenticated (how they got Copilot). The skill just files a GitHub issue when there's something to file.
- **One channel.** Feedback lives as GitHub Issues on `cg-open-itg/catalyst` with the `feedback` label — same place as bugs and enhancements.

## How users give feedback

Feedback can be given at **any point** in a session — there's no "right time" to do it.

### Four ways to trigger it

| # | When | How |
|---|---|---|
| 1 | End of an orchestrator | Orchestrator prompts: *"Anything to flag about this run?"* |
| 2 | Mid-orchestrator (interrupt) | Type *"feedback"* or *"that didn't work"* at any step; Copilot switches to `catalyst-feedback` |
| 3 | Anytime, natural language | *"Feedback on dplc-discovery"*, *"this was frustrating"*, *"rate that"* |
| 4 | Slash command | `/catalyst-feedback` |

Ways #2–4 go through the same on-demand path. Way #1 is the prompted path.

### Prompted path — end of orchestrator

Every orchestrator (`dplc-prereq`, `dplc-triage`, `dplc-discovery`, `dplc-design`) ends with:

> *"Anything to flag about this run? Hit enter to skip, or tell me what worked / what didn't."*

- **Substantive reply** → skill captures session context, shows you a draft, files after you review
- **Silence / "ok" / emoji alone** → nothing filed, user moves on

### On-demand path (#2, #3, #4)

When invoked without a preset reply, the skill asks two optional questions:

1. *"What worked well?"* (optional)
2. *"What didn't work, or what would make it better?"* (optional)

Either or both can be skipped. If both are empty → nothing is filed. If either is filled → skill composes a draft with whatever context it can recover from the conversation, shows you a preview, files after you reply `file`.

Mid-orchestrator interruption (#2) preserves the orchestrator's state — you can return to where you were after filing, or start a new task; your call.

### Tips for writing useful feedback

The team triages issues by reading them. Feedback that names *what* and *why* gets acted on; vague feedback gets closed.

| Style | Pattern | Example |
|---|---|---|
| **Reporting a gap** | `<skill>: <what didn't work> — <reproduction or impact>` | *"dplc-discovery: data-profiling timed out on a 900M-row table without warning. Would help if it estimated row count first."* |
| **Reporting a win** | `<skill>: <what specifically worked>` (not just *"great"*) | *"data-contract: nailed the SLA section from my requirements — saved me ~30 mins."* |
| **Mixed** | `<skill>: <what worked> but <what didn't>` | *"dplc-triage: classification was fast and right for equity products but picked the wrong domain for bonds."* |
| **Pointing at a fix idea** | `<skill>: <problem> — could you <suggested fix>?` | *"data-contract: access control section was empty. Could you pull from security-design if it exists?"* |
| **Reporting an error** | `<skill>: failed with <error excerpt> — <context>` | *"discover-data: failed with 'catalog not accessible' — wasn't clear if it was a token issue or wrong catalog name."* |

What the team can't act on: *"this was confusing"*, *"didn't work"*, *"slow"* alone — without a specific *what* or *why*, no one can reproduce or fix.

### Examples of feedback issues

These are realistic prompt → resulting-issue pairs covering the common patterns. Each is exactly what the team would receive after the user reviews and types `file`.

#### Example 1 — Direct gap (the simplest pattern)

**Prompt** in Copilot Chat:
```
@workspace feedback on dplc-discovery: it was slow and kept asking for the catalog name twice even though discover-data had already found the tables
```

**Filed issue** (labels: `feedback`, `feedback-gap`):
```markdown
## Feedback for `dplc-discovery`

**Plugin version:** 1.1.0

### Context
- **Invoked with:** "feedback on dplc-discovery" (direct invocation)
- **Progress:** not available (direct invocation — skill not observed running in this session)
- **Errors surfaced:** none

### What didn't / could be better
It was slow and kept asking for the catalog name twice even though
discover-data had already found the tables.

---

*Auto-filed by the `catalyst-feedback` skill...*
```

#### Example 2 — Orchestrator end-prompt (richest context)

**Prompt** sequence:
```
@workspace run dplc-discovery for a customer positions data product
[orchestrator runs through several steps]
[at end-prompt:] data-profiling timed out on cspn_prod.cgam_position because it's a 900M-row table — would be helpful if it warned about table size first
```

**Filed issue** (labels: `feedback`, `feedback-gap`):
```markdown
## Feedback for `dplc-discovery`

**Plugin version:** 1.1.0

### Context
- **Invoked with:** "customer positions data product"
- **Progress:** Step 4 of 12 — discover-data (3 tables found in cspn_prod), data-profiling (1 of 3 tables completed, timed out on cgam_position), feasibility-report not yet started
- **Errors surfaced:** "data-profiling: timed out after 60s on cspn_prod.cgam_position (900M rows estimated)"

### What didn't / could be better
data-profiling timed out on a large table without warning the user
first. Would be helpful if it estimated row count before profiling and
warned/asked before going long.

---

*Auto-filed by the `catalyst-feedback` skill...*
```

This is the gold-standard issue: rich context, specific bug, suggested fix, real reproduction details — all auto-captured. The user only had to type the *"what didn't"* sentence; everything else came from the conversation.

#### Example 3 — Mixed (positive overall, specific friction)

**Prompt** in Copilot Chat:
```
@workspace feedback on data-contract: nailed the schema and SLA sections from my requirements but the access control section was empty and I had to fill it manually. Maybe pull from the security-design artifact if it exists?
```

**Filed issue** (labels: `feedback`, `feedback-mixed`):
```markdown
## Feedback for `data-contract`

**Plugin version:** 1.1.0

### Context
- **Invoked with:** "feedback on data-contract" (direct invocation)
- **Progress:** not available (direct invocation)
- **Errors surfaced:** none

### What worked
Nailed the schema and SLA sections from my requirements.

### What didn't / could be better
The access control section was empty and I had to fill it manually.
Maybe pull from the security-design artifact if it exists?

---

*Auto-filed by the `catalyst-feedback` skill...*
```

#### Example 4 — Win

**Prompt** in Copilot Chat:
```
@workspace feedback on dplc-prereq: the new check for an org-wide demand tracker before proceeding caught that we don't have one yet — saved me from going down the rabbit hole. Good guard.
```

**Filed issue** (labels: `feedback`, `feedback-win`):
```markdown
## Feedback for `dplc-prereq`

**Plugin version:** 1.1.0

### Context
- **Invoked with:** "feedback on dplc-prereq" (direct invocation)
- **Progress:** not available (direct invocation)
- **Errors surfaced:** none

### What worked
The new check for an org-wide demand tracker before proceeding caught
that we don't have one yet — saved me from going down the rabbit
hole. Good guard.

---

*Auto-filed by the `catalyst-feedback` skill...*
```

#### Example 5 — Credential-scrub demonstration

**Prompt** in Copilot Chat:
```
@workspace feedback on discover-data: it failed with "401 Unauthorized — Bearer ghp_abc1234567890def1234567890ghi" — looks like my token expired but the error wasn't that helpful in pointing me to fix it
```

**Banner shown above preview** (because the scrub fired):
> ⚠ Auto-redacted 1 token-like string(s) near credential keywords. Review the redactions and the rest of the body carefully before filing.

**Filed issue** (labels: `feedback`, `feedback-gap`) — note the in-place redaction:
```markdown
## Feedback for `discover-data`

**Plugin version:** 1.1.0

### Context
- **Invoked with:** "feedback on discover-data" (direct invocation)
- **Progress:** not available (direct invocation)
- **Errors surfaced:** "401 Unauthorized — Bearer <REDACTED: token-like string near \"Bearer\">"

### What didn't / could be better
It failed with "401 Unauthorized — Bearer <REDACTED: token-like
string near "Bearer">" — looks like my token expired but the error
wasn't that helpful in pointing me to fix it.

---

*Auto-filed by the `catalyst-feedback` skill...*
```

The token-shaped string was caught by the regex pass (20+ chars near *"Bearer"*) and replaced before the user even saw the preview. The user reviewed, confirmed the redactions looked right, and typed `file`.

#### Example 6 — Slash command

**Prompt** in Copilot Chat:
```
/catalyst-feedback
```

Skill responds: *"Which AI Catalyst skill is this feedback about?"*

User replies: `dplc-design`

Skill: *"What worked well?"*

User: `the lineage tracing was excellent — followed all the joins through 4 transformation layers correctly`

Skill: *"What didn't work, or what would make it better?"*

User: `[hits enter to skip]`

**Filed issue** (labels: `feedback`, `feedback-win`):
```markdown
## Feedback for `dplc-design`

**Plugin version:** 1.1.0

### Context
- **Invoked with:** /catalyst-feedback (interactive)
- **Progress:** not available (direct invocation)
- **Errors surfaced:** none

### What worked
The lineage tracing was excellent — followed all the joins through
4 transformation layers correctly.

---

*Auto-filed by the `catalyst-feedback` skill...*
```

## What the issue captures

The skill **auto-captures session context** so the team can debug — you don't have to describe what you were doing. Everything is summarized (not raw dumps), and you always see the full draft before anything ships.

### Structured body

```markdown
## Feedback for `dplc-discovery`

**Plugin version:** 1.1.0

### Context
- **Invoked with:** "customer positions data product for IPT team"
- **Progress:** discover-data (12 tables found), data-profiling (3 of 3 done), feasibility-report (draft created)
- **Errors surfaced:** none

### What worked
(omitted if empty)

### What didn't / could be better
Took 3 tries to get source profile right — had to manually specify catalog.

---

*Auto-filed by the `catalyst-feedback` skill. Close this issue when reviewed,
or relabel to turn it into actionable work.*
```

### What's captured automatically

- **Invocation** — skill / orchestrator name + the user's first input to it
- **Progress** — for orchestrators, the sub-skills that ran with 1-line outcomes (counts, statuses), plus the current step
- **Errors** — any error messages the user actually saw, verbatim (truncated if very long)
- **Plugin version** — for forensics on when a bug was introduced

### What's NOT captured (hard limits in the skill)

- Credentials, tokens, API keys
- Full database schemas with column-level detail
- Full artifact contents (1-line summaries only)
- File paths outside the catalyst repo
- Specific client / customer / account identifiers
- Full vendor / third-party records

When the skill is uncertain, it summarizes instead of quoting.

### Mechanical scrub for token-like strings

In addition to the LLM judgment guardrails above, the skill runs a
deterministic regex pass before showing the preview:

- Looks for any contiguous run of **20+ characters of `[A-Za-z0-9_]`**
- Checks whether any of these keywords appears within **30 characters**
  before or after the candidate (case-insensitive): `token`, `key`,
  `bearer`, `secret`, `auth`, `authorization`, `password`, `passwd`,
  `pwd`, `credential`, `api`, `apikey`, `api_key`
- If yes → replaces the candidate with `<REDACTED: token-like string near "<keyword>">`
- If no → leaves it alone (the proximity-to-keyword filter avoids false positives on long product/table names)

When the scrub fires, the preview is prefixed with a banner:

> ⚠ **Auto-redacted N token-like string(s)** near credential keywords. Review the redactions and the rest of the body carefully before filing.

This is a backstop, not a substitute for the preview-and-review step.

### Preview-before-file

After composing the draft, the skill **always** shows the user:

> *"Here's what I'll file. Review it — everything below goes public on the repo issue tracker. Reply `file` to send, `edit` followed by what to change, or `cancel` to discard."*

The user replies:
- `file` → files the issue as-is
- `edit <request>` — natural language, e.g. *"remove the catalog name"* or *"shorten the problem section"* → skill regenerates the draft surgically, shows it again for re-review
- `cancel` → nothing is filed

This is non-negotiable. Context-capture only works because users trust they see the final output before it goes public.

### Title format

`[feedback] <skill> — <first 6 words of the substantive content>`

Examples:
- `[feedback] dplc-discovery — took 3 tries to get source`
- `[feedback] data-contract — saved me two hours of schema`
- `[feedback] dplc-triage — classification was wrong for bond`

### Labels

Every issue gets exactly two:

- `feedback` — category
- One of:
  - `feedback-win` — only positive content (morale signal)
  - `feedback-gap` — only negative / a concrete problem (actionable)
  - `feedback-mixed` — both positive and negative in the same reply

## One-time admin setup

Before the skill works, four labels must exist on the repo. A maintainer runs this once:

```bash
gh label create feedback       --color 0075ca --description "User feedback on AI Catalyst skills"
gh label create feedback-gap   --color c5100b --description "Feedback describing a problem or something that didn't work"
gh label create feedback-win   --color 2e7d32 --description "Feedback describing something that worked well"
gh label create feedback-mixed --color e8a803 --description "Feedback with both positive and negative content"
```

Without these, `gh issue create --label` fails and the skill falls back to saving locally (see "Graceful failure" below).

## One-time user setup

**None.** If Copilot is working in VS Code, `gh` is authenticated. The skill just works.

## Review process

1. **As feedback arrives** — issues appear in the catalyst repo Issues tab, filterable by label. No external aggregation needed.

2. **Weekly (or ad-hoc)** — a maintainer opens:

   - https://github.com/cg-open-itg/catalyst/issues?q=is%3Aissue+is%3Aopen+label%3Afeedback-gap — **gaps first (these are the actionable ones)**
   - https://github.com/cg-open-itg/catalyst/issues?q=is%3Aissue+is%3Aopen+label%3Afeedback-mixed — **mixed next (real problems in the negative half)**
   - https://github.com/cg-open-itg/catalyst/issues?q=is%3Aissue+is%3Aopen+label%3Afeedback-win — **wins last (morale / validates investment)**

3. **Triage each issue** — outcomes:
   - **Close** — acknowledged, no action needed (typical for wins)
   - **Promote to Jira** — run the `process-feedback` skill to create an AICAT Story and comment the ticket link back on the issue (see "From feedback to Jira" below). This is how feedback becomes prioritized, tracked work.
   - **Relabel** — convert to `bug`, `enhancement`, or similar for GitHub-only follow-ups.
   - **Comment** — ask the reporter for more detail if the description is vague

4. **Monthly** — rough pulse check. Any skill with multiple `feedback-gap` issues in the same area is a candidate for rework or retirement.

## From feedback to Jira (the process loop)

Feedback doesn't stay in GitHub — it feeds the team's Jira backlog and loops
back to the reporter. Two skills implement this:

- **`process-feedback`** — imports the open `feedback`-labeled issues
  (`import_github_feedback.sh`), prioritizes them, and on human approval creates
  Jira Stories in project AICAT (label `Customer-satisfaction`). For each
  promoted issue it then **comments the Jira link back on the GitHub issue** and
  labels it `promoted`, so the reporter knows which ticket to follow and the same
  issue is never promoted twice.
- **`implement-feedback`** — takes the AICAT ticket IDs once triaged/ranked,
  implements the change on a branch, opens a PR against `cg-open-itg/catalyst`,
  and links the PR back to the Jira ticket.

The reporter watches the AICAT ticket for status (the comment on their issue
points them to it). No GitHub Actions are involved — a maintainer runs
`process-feedback` during the weekly triage sweep.

## CLI helpers (optional)

Maintainers who prefer the command line over the web UI:

```bash
# All open gaps — the actionable feed
gh issue list --repo cg-open-itg/catalyst --label feedback-gap --state open --limit 100

# Feedback for a specific skill (search by title)
gh issue list --repo cg-open-itg/catalyst --search "dplc-discovery in:title label:feedback"

# Close all "wins" older than 30 days (just acknowledgement, not action)
gh issue list --repo cg-open-itg/catalyst --label feedback-win --state open --json number,createdAt \
  --jq '.[] | select(.createdAt < "2026-03-24") | .number' \
  | xargs -n1 gh issue close
```

## Graceful failure

If `gh` is broken (not installed, not authenticated, offline, rate-limited, label missing), the skill saves the composed body locally to `.catalyst/feedback/<timestamp>_<skill>.md` and tells the user:

> *"Couldn't file the GitHub issue automatically. Saved locally. Paste this
> into a new issue at <https://github.com/cg-open-itg/catalyst/issues/new?labels=feedback>
> when convenient."*

No feedback is ever lost.

## Identity

Because `gh issue create` posts **as the user's GitHub account**, feedback is signed (by username), not anonymous. Deliberate trade-off for zero-config posting:

- **Pro:** Team can follow up directly with whoever filed the issue
- **Pro:** Signed feedback tends to be more substantive
- **Con:** No pseudonymity — sensitive feedback that needs anonymity has to go out-of-band (DM, email)

If truly anonymous feedback becomes important, a future version could route through a service account. Not in scope for v1.1.0.

## Intentionally deferred

- **Passive telemetry** (usage counts, error rates, abandonment) — needs enterprise privacy review. Would complement feedback nicely by answering "which skills get used at all" — but blocked on policy.
- **NPS / CSAT surveys** — single-digit samples aren't actionable
- **Copilot's built-in 👍👎 integration** — admin-access-dependent
- **Automatic forwarding to Jira / ticket systems** — **now implemented** via the `process-feedback` skill (see "From feedback to Jira" above). Promotion stays a maintainer-curated, human-reviewed step — not silent auto-forwarding.

## Why words + context over ratings

The earlier design used 1–5 ratings. We dropped that because:

- A "3/5" doesn't tell you what's wrong. You still need the comment to do anything about it.
- Rating distributions go bimodal in practice: people rate 5 if it worked, 1 if it broke. The middle is noise.
- A rating without a comment is the weakest category of feedback — we'd rather have 5 substantive comments a week than 50 drive-by ratings.
- Silence is informative: if a user moves on after the orchestrator ends, they were fine. We don't need to log that.

## Why auto-capture context (not just words)

An initial iteration asked only for the user's words and shipped those raw. That gave us scannable titles but not enough to debug: *"took 3 tries"* doesn't tell the team against which catalog, with which source shape, at which step, with what error.

Auto-capturing context (summarized, never raw, always previewed) fixes that without putting the debugging burden on the user. They give their words; the skill supplies the specifics they were already thinking about implicitly.

The preview step is what makes this safe — users see and approve exactly what's shared before it goes public.

The team's review becomes: read what people actually wrote, plus the concrete context of what they were doing. Prioritize gaps. Celebrate wins briefly. Act.
