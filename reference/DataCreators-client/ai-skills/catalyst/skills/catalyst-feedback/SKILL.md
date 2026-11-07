---
name: catalyst-feedback
description: Capture substantive feedback on an AI Catalyst skill as a GitHub issue, including rich session context (skill inputs, sub-skills run, phase, errors). Always previews the draft issue to the user before filing so they can review and redact sensitive specifics. Use when the user wants to report something that worked, something that didn't, or something that could be better. Also invoked at the end of orchestrator runs when the user volunteers a substantive reply.
---

# catalyst-feedback

File a GitHub issue on `cg-open-itg/catalyst` capturing what the user was
doing, what happened, and what they want to say about it. Always preview
before filing — users see exactly what goes public and can redact
inline.

## When to use

- User replies to an orchestrator's end-prompt with something substantive
- User says "feedback on X", "that didn't work", "this was great because..."
- User explicitly invokes `catalyst-feedback` or `/catalyst-feedback`

## Inputs

`$ARGUMENTS` may contain:
- A skill name (e.g. `dplc-discovery`, `data-contract`, `plugin`)
- `reply=<text>` — the user's verbatim reply, captured by an orchestrator

## Never include in the issue

These are hard limits. Strip / omit / summarize — never file them:

- Credentials, API tokens, OAuth bearer tokens, passwords, private keys
- Full database schemas with column-level detail
- Full artifact contents (1-line summaries only)
- File paths outside the catalyst repo
- Specific client / customer / account identifiers
- Full vendor / third-party system records

When in doubt, summarize instead of quoting. The user sees the draft and
can redact further before it's filed — but the skill shouldn't ship
anything from the above list even if it appears in conversation.

**Mechanical safeguard for the credential category:** Step 5's "Sanity
check 1" runs a regex-based scrub for token-like substrings near
credential keywords (`token`, `key`, `bearer`, `secret`, `auth`,
`password`, `credential`, `api`). Matches are auto-redacted and a
banner is shown above the preview. This is a backstop, not a
substitute for judgment.

## Sequencing

### Step 1 — Identify the target skill

If `$ARGUMENTS` names a skill, use it. Otherwise ask:

> "Which AI Catalyst skill is this feedback about? (e.g. `dplc-discovery`,
> `data-contract`, `discover-data`, or type `plugin` for feedback about
> the plugin overall.)"

If the user just ran a skill, suggest it: *"Is this about `dplc-discovery`
you just ran? (y/n)"*.

### Step 2 — Gather the user's words

**If `reply=<text>` is in `$ARGUMENTS`** (fast path from an orchestrator):
use that text as the user's feedback. Skip to Step 3.

**Otherwise** ask two optional prompts, in order:
1. "What worked well?" (optional)
2. "What didn't work, or what would make it better?" (optional)

If both are empty → don't file, tell the user:
> "No content to log. If something comes up later, say `feedback` and I'll
> capture it then."

### Step 3 — Extract session context from the conversation

Review the conversation so far. Extract the following, summarized tightly
and respecting the "Never include" list above.

**The Context section in the issue body is MANDATORY.** Never omit it,
even for direct `/catalyst-feedback` invocations with thin conversation.
If a specific field can't be populated, use an honest placeholder like
*"not available (direct invocation)"* or *"none recorded"* — do not drop
the field, and do not drop the whole section. The team reads these
issues in bulk; a consistent section shape matters more than a short
body.

Fields to populate:

- **Invocation input** — what the user typed when they started the skill,
  paraphrased if sensitive (1–2 lines).
  - For orchestrator fast path (`reply=<text>`): the arguments the user
    gave when invoking the orchestrator, e.g. *"customer positions data
    product for IPT team"*.
  - For direct `/catalyst-feedback`: the user's opening statement, e.g.
    *"Feedback on dplc-discovery about repeated catalog prompts"*.
  - If genuinely unknown: *"not available"*.

- **Progress** — what the skill had accomplished at the point of
  feedback:
  - For orchestrators: list each sub-skill with a 1-line outcome (e.g.
    `discover-data: 12 tables found`,
    `data-profiling: completed on 3 tables, 2 skipped due to access`).
    Include the current step number and total (e.g. `Step 3 of 4 —
    Feasibility Report`).
  - For direct invocations of a single skill: *"not available (direct
    invocation — skill not observed running)"*.

- **Errors surfaced** — any error messages the user actually saw. Copy
  verbatim but truncate long stack traces to the first relevant line.
  If no errors: *"none"*. Never omit the field.

- **Plugin version** — read from `plugins/ai-catalyst/plugin.json` key
  `version`. Always present.

When in doubt between "summarize" and "omit," summarize. The user gets
to review and redact in Step 6.

### Step 4 — Classify

Based on the user's words (from Step 2):

| "What worked" / reply tone | "What didn't" / problem described | Label |
|---|---|---|
| only positive | empty | `feedback-win` |
| empty | only negative / problem | `feedback-gap` |
| both present | both present | `feedback-mixed` |

For a fast-path `reply=<text>`, use judgment to classify the full reply.
If ambiguous, default to `feedback-mixed`.

### Step 5 — Compose the draft

**Title:** `[feedback] <skill> — <first 6 words of the substantive content>`

Use the *"What didn't"* content for `feedback-gap` and `feedback-mixed`;
use *"What worked"* for `feedback-win`.

**Body — the Context section is mandatory; each of its three bullets is
mandatory. Only the What-worked / What-didn't sections may be omitted
when empty. Never produce a body without a Context section.**

```markdown
## Feedback for `<skill>`

**Plugin version:** <version>

### Context
- **Invoked with:** <invocation input, or "not available" placeholder>
- **Progress:** <sub-skills that ran + current step, or "not available (direct invocation)" placeholder>
- **Errors surfaced:** <verbatim error message(s), or "none">

### What worked
<content — omit this section entirely if the field was empty>

### What didn't / could be better
<content — omit this section entirely if the field was empty>

---

*Auto-filed by the `catalyst-feedback` skill. Close this issue when
reviewed, or relabel to turn it into actionable work.*
```

**Sanity check 1 — token/credential scrub (mandatory before preview):**

Scan the entire composed body — every section, including Context, What
worked, and What didn't — for **token-like substrings**:

- A token-like substring is any contiguous run of **20 or more characters
  matching `[A-Za-z0-9_]`** (alphanumerics + underscores).
- For each candidate, check whether any of these keywords appears
  **within 30 characters** before or after, case-insensitive:

  ```
  token, key, bearer, secret, auth, authorization,
  password, passwd, pwd, credential, api, apikey, api_key
  ```

- If any of those keywords is in the 30-char window, the candidate is
  treated as a likely credential. **Replace the candidate string in
  place** with the literal text:

  `<REDACTED: token-like string near "<matched-keyword>">`

  Use the actual matched keyword in the replacement so the user knows
  why we redacted. Keep the rest of the line intact.

- If no nearby keyword, leave the substring alone — the scrub is
  intentionally narrow to avoid false positives on long product/table
  names that don't sit near credential terminology.

Track how many redactions you made. If the count is **> 0**, prepend the
**preview** (Step 6) with this banner — but **do not** put the banner
into the issue body itself:

> ⚠ **Auto-redacted N token-like string(s)** near credential keywords.
> Review the redactions and the rest of the body carefully before
> filing. If you see anything else that looks sensitive, reply
> `edit <request>` instead of `file`.

This is a basic mechanical safeguard — not exhaustive. The preview step
is still the primary line of defence; the user is the final reviewer.

**Sanity check 2 — Context section present:** Does the body you just
composed include a `### Context` header followed by three bullets
(Invoked with, Progress,
Errors surfaced), each with a value or an honest placeholder? If not,
re-compose — the Context section is non-negotiable.

### Step 6 — Preview and await confirmation

**This step is mandatory and non-skippable.** Never call `gh issue
create` (Step 8) without first showing the preview and receiving an
explicit `file` response. This applies to:

- Interactive invocations (two-question flow)
- Fast-path invocations (`reply=<text>` from an orchestrator)
- Every edit-regenerate cycle

No exceptions. The team relies on users having seen and approved
exactly what gets posted.

Show the user the full draft, unambiguously separated so they can scan
it. Format:

> *"Here's what I'll file. Review it — everything below goes public on
> the repo issue tracker. Reply `file` to send, `edit` followed by what
> to change, or `cancel` to discard."*
>
> ```
> Title: [feedback] dplc-discovery — took 3 tries to get source
> Labels: feedback, feedback-gap
>
> ## Feedback for `dplc-discovery`
>
> **Plugin version:** 1.1.0
>
> ### Context
> - Invoked with: "customer positions data product for IPT team"
> - Progress: Orchestrator ran discover-data (12 tables found in cspn_dev1.client_positions),
>   data-profiling (completed on 3 tables), feasibility-report (draft created)
> - Errors surfaced: none
>
> ### What didn't / could be better
> Took 3 tries to get source profile right — had to manually specify catalog
> even though discover-data had already found the tables.
>
> ---
> *Auto-filed by the `catalyst-feedback` skill...*
> ```

Wait for the user's response.

### Step 7 — Handle the response

- **`file`** (or any of: "yes", "yep", "yeah", "ok", "okay", "send",
  "submit", "go", "ship it", "looks good", "lgtm", "👍"): proceed to
  Step 8
- **`edit <request>`** (e.g. *"remove the catalog name"*, *"don't mention
  the team"*, *"shorten the problem section"*): interpret the request
  surgically — change only what they asked for, preserve everything else.
  Regenerate the draft and return to Step 6.
- **`cancel`** (or "no", "nope", "stop", "discard", "abort", "nvm",
  "nevermind"): discard, say *"Got it, nothing filed."* End.

If the response is ambiguous — not clearly a confirm, an edit, or a
cancel — ask once: *"Is that a 'file it,' 'edit X,' or 'cancel'?"* Then
apply the clarification.

For edits: be conservative. If the user says "remove the catalog name,"
remove just the specific catalog identifier, not all mentions of catalogs.
If the user says "drop the whole context section," remove the entire
section. When in doubt about the scope of an edit, ask: *"You want me to
remove X, or everything mentioning Y?"*

### Step 8 — File the issue

Write the composed body to a temp file and run `gh`, **capturing stdout**
so the success check in Step 9 can verify the URL:

```bash
BODY_FILE=$(mktemp)
cat > "$BODY_FILE" <<'BODY'
<the approved body>
BODY

ISSUE_URL=$(gh issue create \
  --repo cg-open-itg/catalyst \
  --title "$TITLE" \
  --body-file "$BODY_FILE" \
  --label feedback \
  --label "<feedback-win|feedback-gap|feedback-mixed>" 2>&1)
GH_EXIT=$?

rm "$BODY_FILE"
```

Use `--body-file` (not `--body`) to avoid shell-escaping issues when the
content contains quotes, newlines, or special characters.

### Step 9 — Verify success before reporting

Do not report "filed" on trust. Verify that:

1. `$GH_EXIT` is `0`, AND
2. `$ISSUE_URL` matches the pattern
   `https://github.com/cg-open-itg/catalyst/issues/\d+`

If both conditions hold, show the user:

> "Filed as <ISSUE_URL>. Thanks."

If either condition fails (non-zero exit, empty output, garbled output
from terminal pollution, a rate-limit message, etc.), **do not claim the
issue was filed.** Fall through to Step 10 (graceful failure). The
terminal-pollution scenario — where a concurrent process dumps output
into the shared shell and `gh`'s URL gets lost in the noise — is a real
failure mode; the verification step is what protects against false
positives.

Do not elaborate. Do not re-prompt. Do not suggest other skills.

### Step 10 — Graceful failure

If `gh issue create` fails (not installed, not authenticated, offline,
label missing, rate-limited):

1. Show the error briefly.
2. Save the approved body to `.catalyst/feedback/<ISO-timestamp>_<skill>.md`
   so nothing is lost.
3. Tell the user:
   > "Couldn't file the GitHub issue automatically. Saved locally at
   > `<path>`. Paste this into a new issue at
   > <https://github.com/cg-open-itg/catalyst/issues/new?labels=feedback>
   > when convenient."

## Labels

Every issue gets exactly two:

- `feedback` — category
- `feedback-win` | `feedback-gap` | `feedback-mixed` — classification

**One-time admin setup creates these labels** — see `docs/feedback.md`.

## Notes

- **Preview is always on.** The user sees the full draft before anything
  goes to GitHub. No silent submissions. This is deliberate — context
  capture only works if users trust that they control what ships.
- **Context is a summary, not a transcript.** Don't dump the full
  conversation into the issue. Extract the structured pieces (invocation,
  sub-skills, errors) — skip raw artifact contents.
- **Identity is signed.** `gh issue create` posts as the user's GitHub
  account. Trade-off for zero-config filing; users who need anonymity
  need to use an out-of-band channel.
- **Silence still means satisfied.** If the user hits enter / moves on /
  gives a non-substantive reply ("k", "ok", lone emoji), don't file
  anything. No default issue for the absence of feedback.

## Sample invocations (few-shot guidance)

These illustrate expected input → output shape. Use them as anchors when
composing your own drafts.

### Example A — orchestrator end-prompt, gap

**User to orchestrator dplc-discovery (after running through 4 steps):**
> data-profiling timed out on cspn_prod.cgam_position because it's a
> 900M-row table — would be helpful if it warned about table size first

**Orchestrator invokes:** `catalyst-feedback dplc-discovery reply=<that text>`

**Composed body** (passes both sanity checks, no scrub fires):
```markdown
## Feedback for `dplc-discovery`

**Plugin version:** 1.1.0

### Context
- **Invoked with:** "customer positions data product"
- **Progress:** Step 4 of 12 — discover-data (3 tables found in cspn_prod), data-profiling (1 of 3 completed, timed out on cgam_position), feasibility-report not yet started
- **Errors surfaced:** "data-profiling: timed out after 60s on cspn_prod.cgam_position (900M rows estimated)"

### What didn't / could be better
data-profiling timed out on a large table without warning the user first.
Would be helpful if it estimated row count before profiling and warned/asked
before going long.

---

*Auto-filed by the `catalyst-feedback` skill...*
```

**Title:** `[feedback] dplc-discovery — data-profiling timed out on cspn_prod`

**Labels:** `feedback`, `feedback-gap`

### Example B — direct invocation with credential, scrub fires

**User:** *"feedback on discover-data — failed with 'Bearer ghp_abc1234567890def1234567890ghi' — token expired"*

**Composed body** (after scrub):
```markdown
## Feedback for `discover-data`

**Plugin version:** 1.1.0

### Context
- **Invoked with:** "feedback on discover-data" (direct invocation)
- **Progress:** not available (direct invocation)
- **Errors surfaced:** "Bearer <REDACTED: token-like string near \"Bearer\">"

### What didn't / could be better
Failed with "Bearer <REDACTED: token-like string near "Bearer">" —
token expired.

---
```

**Banner before preview:**
> ⚠ Auto-redacted 1 token-like string(s) near credential keywords. Review the redactions and the rest of the body carefully before filing.

**Title:** `[feedback] discover-data — failed with Bearer redacted token`

**Labels:** `feedback`, `feedback-gap`

### Example C — slash command, win-only

**User:** `/catalyst-feedback`

**Skill:** *"Which AI Catalyst skill is this feedback about?"*
**User:** `dplc-design`
**Skill:** *"What worked well?"*
**User:** `lineage tracing was excellent — followed joins through 4 transformation layers correctly`
**Skill:** *"What didn't work, or what would make it better?"*
**User:** *(hits enter)*

**Composed body:**
```markdown
## Feedback for `dplc-design`

**Plugin version:** 1.1.0

### Context
- **Invoked with:** /catalyst-feedback (interactive)
- **Progress:** not available (direct invocation)
- **Errors surfaced:** none

### What worked
Lineage tracing was excellent — followed joins through 4 transformation
layers correctly.

---
```

**Title:** `[feedback] dplc-design — lineage tracing was excellent followed joins`

**Labels:** `feedback`, `feedback-win`

(*"What didn't"* section omitted because the user skipped that question.)
