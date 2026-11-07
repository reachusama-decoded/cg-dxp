---
name: dplc-triage
description: >-
  Phase 1 Triage -- sub-orchestrator of dplc-design-stage. Checks if the data product
  already exists, classifies it, creates demand tracker entry and consumer use
  case map. Trigger phrases: "triage a request", "Phase 1", "log demand",
  "classify a data product", "check for duplicates".
allowed-tools: Read Grep
metadata:
  tier: orchestrator
  lifecycle-phase: phase-1-triage
  dependencies:
    - marketplace-search
    - demand-tracker-entry
    - consumer-use-case-map
  consumes:
    - phase-zero-checklist
  shared-components:
    core: []
    platforms: []
---

# Phase 1: Triage Orchestrator

This orchestrator guides you through **Phase 1 — Triage** of the Data Product
Lifecycle (see `rfd/0002/README.md` for the full definition).

**Phase 1 purpose:** Quickly determine whether the demand is worth investing in
Discovery. Triage captures the request, confirms no existing product already
meets the need, classifies the product, maps consumers, and establishes enough
scope clarity to justify the deeper Discovery work.

**Who this is for:** A Data Product Manager or Data Product Creator with an
approved Phase 0 checklist, ready to formally capture a new data product request.

**Phase 1 gate:** *Worth pursuing?*
- Demand tracker entry created with Data Owner approval
- Consumer use case map drafted
- Preliminary classification documented (domain, sensitivity, criticality)
- Yes → Discovery (Phase 2)
- No → Defer or Reject

---

## Progress Reporting

As you work through each step, report progress clearly so the user can
follow along. For each sub-skill or action:

1. **Announce** what you're about to do before doing it
2. **Report** what you found or produced after each step
3. **Show counts and specifics** — not "searched for tables" but "Searched
   caspian_prd for index-related tables — found 5 matches"
4. **Use a checklist** format so the user can see what's done and what's left:

Example:
```
- [x] Read Phase 1 artifacts (product: Index Data Product, 6 consumers mapped)
- [x] discover-data: Searched 3 catalogs, found 5 relevant tables
- [x] data-profiling: Profiled rimes_asset_universe (1.79M rows, 24 indexes)
- [ ] feasibility-report: generating...
- [ ] requirements-acceptance-criteria
- [ ] outcome-kpi-statement
- [ ] effort-estimate
```

Never run silently. The user should always know where you are.

---

## Sub-Skills Invoked

| Skill | Type | Purpose | Required? |
|:------|:-----|:--------|:----------|
| `marketplace-search` | execution | Check whether a product meeting this need already exists | Required |
| `demand-tracker-entry` | document | Create the formal demand tracker entry | Required (unless marketplace-search found an exact duplicate; see Step 2) |
| `consumer-use-case-map` | document | Map downstream consumers, use cases, access patterns, and SLA needs | Required (unless marketplace-search found an exact duplicate; see Step 2) |

This orchestrator **delegates** to the three leaves above rather than handling
triage inline. Each step below must invoke its sub-skill explicitly via the
`/<skill-name>` slash command (Claude Code's native routing) — and you must
also `Read skills/<skill-name>/SKILL.md` so the sub-skill's prompt and output
contract drive the work, not your inline interpretation. Preserve each
sub-skill's output verbatim in your final response; do not paraphrase or
merge its sections into a generic summary.

Execution skills run first so that document artifacts are grounded in real
findings rather than assumptions.

---

## Sequencing

### Step 1 — Gather product context

Check the conversation and $ARGUMENTS for a product name or description. If
Phase 0 was just completed, pull the product name from that context. If not,
ask the user:

> "What data product are you triaging? Describe what it contains and the
> business need it serves."

Also ask (if not already known): Who is the requestor? Who is the Data Owner?

### Step 2 — Invoke `/marketplace-search` (Required)

**Delegate to `marketplace-search`.** Do this in two parts:

1. `Read skills/marketplace-search/SKILL.md` to load the sub-skill's
   instructions, exit-code handling, and output contract.
2. Invoke `/marketplace-search` with the product description / keywords
   derived from Step 1. Follow the sub-skill's workflow exactly — do not
   short-circuit by running an inline grep or a generic search.

Preserve the sub-skill's output (its match list, exit code, and recommended
action) verbatim in your reply. Then apply the conditional below:

- **Exact match found** — surface the existing product, recommend the
  requestor be routed to it, and **stop here**. Do **not** invoke
  `/demand-tracker-entry` or `/consumer-use-case-map`. Report the Phase 1
  gate as *Reject (duplicate)* and skip to Step 5.
- **Partial match found** — surface the candidate(s) and ask the user
  whether their need is meaningfully different. If yes, continue to Step 3.
  If no, route to the existing product and stop (as above).
- **No match found** — continue to Step 3.

Record the marketplace search outcome — it will appear in the demand tracker
entry Triage Notes.

### Step 3 — Invoke `/demand-tracker-entry` (Required if Step 2 did not stop)

**Delegate to `demand-tracker-entry`.** Do this in two parts:

1. `Read skills/demand-tracker-entry/SKILL.md` to load the sub-skill's
   template, required fields, and approval contract.
2. Invoke `/demand-tracker-entry` with the product name/description and the
   marketplace search outcome from Step 2 as context.

Ask the user for the classification fields (Type, Priority, Sensitivity,
Criticality) — they know their product best. Reference the marketplace search
findings in the Triage Notes section.

Preserve the sub-skill's full demand-tracker-entry artifact in your reply;
do not summarize it down to a one-liner. Confirm with the user that the Data
Owner has reviewed and approved the entry before marking it complete.

### Step 4 — Invoke `/consumer-use-case-map` (Required if Step 2 did not stop)

**Delegate to `consumer-use-case-map`.** Do this in two parts:

1. `Read skills/consumer-use-case-map/SKILL.md` to load the sub-skill's
   template, the consumer/use-case/access-pattern columns, and SLA fields.
2. Invoke `/consumer-use-case-map` with the product context.

Pull the product name, domain, and requestor from the demand tracker entry
produced in Step 3 — do not re-ask. Work with the user to identify:
- Who are the initial consumers?
- What use cases do they have?
- What are their access patterns and SLA expectations?

Preserve the sub-skill's full consumer-use-case-map artifact in your reply;
do not paraphrase it into a generic bullet list.

### Step 5 — Summarize and report the gate determination

After all preceding sub-skill outputs are in your reply (verbatim, not
paraphrased), assess the gate criteria and report clearly. The gate
determination is **your** synthesis — but it must point back at the
sub-skill artifacts produced above; do not re-author them in a different
voice.

**If all gate criteria are met:**
> "Phase 1 Triage complete. The demand tracker entry is created, consumers are
> mapped, and the product is classified as [domain / sensitivity / criticality].
> The Data Owner has approved. You are ready for Phase 2 Discovery.
> Run `/dplc-discovery [product-name]` to continue."

**If the product should be deferred or rejected:**
> State the specific reason (duplicate, out of scope, no Data Owner, unclear
> demand). Recommend whether to defer (revisit later) or reject (not worth
> pursuing). Do not proceed to Discovery.

### Step 6 — Invite feedback

After the gate determination, append this one-line prompt as the final line
of your response:

> "Anything to flag about this run? Hit enter to skip, or tell me what
> worked / what didn't."

Then:
- **If the user replies with anything substantive** — a sentence, a
  reaction, a problem description, even a short "worked great": invoke
  the `catalyst-feedback` skill with `$ARGUMENTS = "dplc-triage
  reply=<their reply verbatim>"`. The skill extracts session context
  (sub-skills that ran, current phase, any errors), composes a draft
  issue, **shows the user the full draft for review**, and files after
  they confirm.
- **If the user hits enter / moves on / gives a non-substantive reply**
  (e.g. just "k", "ok", an emoji alone): do nothing. No file, no
  re-prompt. Silence means satisfied.

---

## Notes

- Classification is a Data Owner confirmation, not just a best guess. Surface
  the classification output and ask the user to confirm the Data Owner agrees
  before marking the demand tracker entry approved.
- For feature-level work on an existing product (score 0–1 on the
  product-vs-feature heuristic in the RFD), update the existing demand tracker
  entry and consumer use case map rather than creating new ones. Phases 1 and 2
  are lighter-weight for feature work.
- If the user skipped Phase 0, ask whether the Phase 0 checklist has been
  completed before proceeding. Phase 0 is a prerequisite for Phase 1.
