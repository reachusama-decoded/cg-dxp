---
name: dplc-discovery
description: >-
  Phase 2 Discovery -- sub-orchestrator of dplc-design-stage. Runs data discovery and
  profiling first, then generates feasibility, requirements, business case, and
  effort estimates grounded in real data. Trigger phrases: "discover data",
  "Phase 2", "assess feasibility", "profile sources", "write requirements".
allowed-tools: Read Grep
metadata:
  tier: orchestrator
  lifecycle-phase: phase-2-discovery
  dependencies:
    - discover-data
    - data-profiling
    - load-confluence-context
    - product-requirements-document
    - feasibility-report
    - requirements-acceptance-criteria
    - outcome-kpi-statement
    - effort-estimate
    - business-case
    - privacy-impact-assessment
    - poc-spike-findings
  consumes:
    - demand-tracker-entry
    - consumer-use-case-map
  shared-components:
    core: []
    platforms: []
---

# Phase 2: Discovery Orchestrator

This orchestrator guides you through **Phase 2 — Discovery** of the Data Product
Lifecycle (see `rfd/0002/README.md` for the full definition).

**Phase 2 purpose:** Validate feasibility, perform detailed requirements
analysis, and confirm team capacity. This phase produces the artifacts needed
to justify entering Design. The Data Product Manager leads requirements
analysis — working with Data Owners, Data Stewards, and Data Product Creators
to define business logic, identify the right sources, and document acceptance
criteria.

**Who this is for:** A Data Product Manager or Data Product Creator with an
approved demand tracker entry from Phase 1 Triage.

**Phase 2 gate:** *Accepted, Feasible & Capacity?*
- Data Owner approved the demand tracker entry
- Source data identified, discovered, and profiled
- Technical feasibility confirmed (or risks documented with mitigations)
- Requirements and acceptance criteria documented
- Team capacity confirmed, effort sized
- Yes → Design (Phase 3)
- No Capacity → Return to Backlog
- Not Feasible → Park or Reject
- Not Accepted → Defer or Reject

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
| `discover-data` | execution | Query Unity Catalog for relevant source tables | Required |
| `data-profiling` | execution | Profile discovered tables for quality, completeness, and fitness | Required |
| `load-confluence-context` | execution | Retrieve requirements or design docs from Confluence | Optional |
| `product-requirements-document` | document | The PRD — single source of truth consolidating all discovery findings | Required |
| `feasibility-report` | document | Assess technical, data availability, and regulatory feasibility | Required |
| `requirements-acceptance-criteria` | document | Document business requirements and acceptance criteria | Required |
| `outcome-kpi-statement` | document | Define measurable outcomes and KPIs for the product | Recommended |
| `effort-estimate` | document | Size the effort referencing feasibility findings | Recommended |
| `business-case` | document | Justify the investment (cost, benefit, risk) | Optional |
| `privacy-impact-assessment` | document | Assess PII handling, retention, and regulatory obligations | Required if PII detected |
| `poc-spike-findings` | document | Document results of a proof-of-concept or spike | Optional |

Execution skills run before document skills. Do not generate artifacts until
profiling data is in hand — grounded artifacts are the point of this phase.

**How to invoke a sub-skill.** This orchestrator delegates — it does not
produce sub-skill outputs inline. For every sub-skill referenced below,
hand off by invoking the `Skill` tool with the sub-skill name (e.g.
`Skill(name="discover-data")`). Read the sub-skill's `skills/<name>/SKILL.md`
first if you need to confirm inputs, then call `Skill`. Do not inline the
work: if you find yourself writing a feasibility-report section directly
in this orchestrator's reply, stop and call the `feasibility-report`
sub-skill instead. The Phase 2 gate requires that each required artifact
came from the purpose-built skill that owns it.

---

## Sequencing

### Step 1 — Read Phase 1 artifacts

Before asking the user anything, check the conversation for prior phase
artifacts. If a `demand-tracker-entry` or `consumer-use-case-map` exists in
context, extract:
- **Product name** — use this, do not re-ask
- **Domain and classification** (sensitivity, criticality) — carry forward
- **Requestor and Data Owner** — carry forward
- **Initial consumers and use cases** — use to inform requirements

If Phase 1 artifacts are not in context, ask the user for the product name and
whether they completed Phase 1. Remind them that a demand tracker entry is
required before Discovery.

Also ask (if not already known): Which Unity Catalog catalog should be searched?
(e.g., `cspn_dev1`, `cspn_prod`). This is required for `discover-data`.

If the user mentions a Confluence page with requirements or a design doc,
collect the page ID now — you will use it in Step 3.

### Step 2 — Invoke `discover-data` (Required, via `Skill` tool)

Hand off to the `discover-data` sub-skill via the `Skill` tool. Pass the
catalog name and product keywords derived from the product description and
Phase 1 context as the skill's arguments. Do not query Unity Catalog
yourself — that is what `discover-data` exists for.

Review the discovered tables with the user once `discover-data` returns:
- Are these the right source candidates?
- Are there other tables or schemas to search?
- Narrow or expand the search until the user is satisfied with the table list.

Carry the confirmed table list forward to Step 3.

### Step 3 — Optionally invoke `load-confluence-context` (Conditional)

If — and only if — the user mentioned a Confluence page in Step 1 (or at
any point), hand off to `load-confluence-context` via the `Skill` tool with the
page ID. This retrieves requirements, source system documentation, or
architecture context that will ground the feasibility report and
requirements artifact.

If no Confluence page is mentioned, skip this step — do not invoke
`load-confluence-context`.

### Step 4 — Invoke `data-profiling` (Required, via `Skill` tool)

Hand off to the `data-profiling` sub-skill via the `Skill` tool, passing the
confirmed source tables from Step 2 as input. Do not run profiling queries
inline — `data-profiling` owns the profiling workflow and emits the
structured profile report that downstream skills consume.

Once `data-profiling` returns, review the profiling results carefully:
- Flag any column with `null_rate > 0.20` on a key field as a quality concern.
- Note the date range — is historical coverage sufficient for the product?
- Check for PII indicators in column names or descriptions (e.g., SSN, DOB,
  email, name, address). If PII is detected or suspected, note it — this
  triggers the conditional `privacy-impact-assessment` in Step 9.

Carry the profiling report forward as input to all subsequent skills. In
particular, `feasibility-report` (Step 5) cannot be invoked until profiling
has produced quality metrics, date ranges, and row counts to ground it.

### Step 5 — Invoke `feasibility-report` (Required, via `Skill` tool)

Hand off to the `feasibility-report` sub-skill via the `Skill` tool. Do not
write the feasibility report inline — `feasibility-report` is the
purpose-built skill that owns this artifact.

Pass the following as context to `feasibility-report`:
- Profiling results from Step 4 (quality metrics, date ranges, row counts) —
  these are direct inputs; the feasibility report grades risks against them
- Confluence content from Step 3 (if available)
- Classification from Phase 1 (sensitivity, criticality, regulatory scope)

The feasibility report assesses: data availability, technical feasibility,
regulatory/privacy exposure, and risk. Quality concerns from profiling become
feasibility risks. The data flow is strict: profiling output feeds
feasibility inputs.

### Step 6 — Invoke `requirements-acceptance-criteria` (Required, via `Skill` tool)

Hand off to the `requirements-acceptance-criteria` sub-skill via the `Skill`
tool. This is the Data Product Manager's primary artifact and must come
from the dedicated skill, not be drafted inline here.

Pass as context to `requirements-acceptance-criteria`:
- Discovered table schemas from Step 2 (field names, types, grain)
- Consumer use cases from Phase 1 (what questions the product must answer)
- Confluence requirements content from Step 3 (if available)
- Feasibility findings from Step 5 (any constraints or risks that bound scope)

Work with the user to ensure business logic, calculation definitions, and
acceptance criteria are documented at sufficient detail to inform Design.

### Step 7 — Invoke `outcome-kpi-statement` (Recommended, via `Skill` tool)

Ask the user:

> "Do you want to define the measurable outcomes and KPIs for this product?
> This takes 5–10 minutes and helps validate success post-launch."

If yes, hand off to `outcome-kpi-statement` via the `Skill` tool. If no,
note that this artifact was skipped.

### Step 8 — Invoke `effort-estimate` (Recommended, via `Skill` tool)

Hand off to `effort-estimate` via the `Skill` tool. Pass the feasibility
report findings as context — complexity, data quality issues, and
regulatory obligations all affect effort. Ask the user to confirm the team
size and any known constraints before finalizing the estimate.

### Step 9 — Conditionally invoke `business-case`, `privacy-impact-assessment`, `poc-spike-findings`

These three skills are conditional. Each must be invoked via the `Skill`
tool **only when its condition holds**. Do **not** invoke them
unconditionally — they are not part of every Phase 2 run.

**`business-case` (Optional):** Ask the user:
> "Do you need a formal business case to justify the investment?"
- **If yes:** invoke `business-case` via the `Skill` tool.
- **If no:** skip. Record that business case was not requested.

**`privacy-impact-assessment` (Conditional — Required only when PII detected):**
Decide based on Step 4 profiling output and Step 5 feasibility findings:
- If profiling detected PII indicators (SSN, DOB, email, name, address,
  account number, etc.) **OR**
- The feasibility report records Sensitivity = Confidential / Restricted **OR**
- The feasibility report records regulatory exposure (GDPR, CCPA, GLBA,
  Reg S-P, SOX, DORA, HIPAA)

then invoke `privacy-impact-assessment` via the `Skill` tool. Do not skip
this for any product with PII = Yes or Unknown. The Data Owner (not the
DPM) must confirm the sensitivity classification.

If none of those triggers fire — no PII indicators, public/internal
sensitivity, no regulated scope — **skip** `privacy-impact-assessment`.
Record in the gate report that PII was not detected.

**`poc-spike-findings` (Optional):** Only if the user has actually run a
proof-of-concept or spike, invoke `poc-spike-findings` via the `Skill` tool
to capture the results. If no spike was run, skip — do not prompt the user
to run one.

### Step 10 — Invoke `product-requirements-document` (Required, via `Skill` tool)

After all other discovery artifacts are complete, hand off to
`product-requirements-document` via the `Skill` tool to consolidate
everything into the PRD — the single source of truth for this data
product. Do not assemble the PRD inline; the PRD skill owns this artifact.

The PRD should pull from all artifacts produced in this phase:
- Product info from the demand tracker entry
- Consumers and use cases from the consumer use case map
- Source data findings from discover-data and data-profiling
- Feasibility assessment from the feasibility report
- Requirements from requirements-acceptance-criteria
- KPIs from outcome-kpi-statement
- Effort from effort-estimate
- Business case (if produced)

Sections marked "Optional during Discovery" in the PRD template can be left
with a note indicating they'll be completed in the Design or Publish phase.

Save to the same output directory as other discovery artifacts.

### Step 11 — Summarize and report the gate determination

After all required artifacts are complete, assess the three gate conditions:
Accepted, Feasible, and Capacity.

**If all gate criteria are met:**
> "Phase 2 Discovery complete.
> - Sources identified: [table list]
> - Feasibility: [confirmed / risks noted]
> - Requirements and acceptance criteria: documented
> - Effort estimate: [size]
> - Capacity: confirmed
>
> You are ready for Phase 3 Design. Run `/dplc-design [product-name]` to
> continue."

**If no capacity:**
> "Discovery is complete and the product is feasible, but capacity is not
> confirmed. Return this to the backlog and revisit when a team is available.
> All artifacts have been produced and are ready when capacity opens."

**If not feasible:**
> State the specific blocker from the feasibility report (e.g., source data
> quality too poor, regulatory exposure unresolvable, technical approach not
> viable). Recommend parking or rejecting with reasoning.

**If not accepted:**
> Describe what is missing (e.g., Data Owner approval not obtained, scope
> unclear, demand tracker entry incomplete). List what must be resolved.

### Step 12 — Invite feedback

After the gate determination, append this one-line prompt as the final line
of your response:

> "Anything to flag about this run? Hit enter to skip, or tell me what
> worked / what didn't."

Then:
- **If the user replies with anything substantive** — a sentence, a
  reaction, a problem description, even a short "worked great": invoke
  the `catalyst-feedback` skill with `$ARGUMENTS = "dplc-discovery
  reply=<their reply verbatim>"`. The skill extracts session context
  (sub-skills that ran, current phase, any errors), composes a draft
  issue, **shows the user the full draft for review**, and files after
  they confirm.
- **If the user hits enter / moves on / gives a non-substantive reply**
  (e.g. just "k", "ok", an emoji alone): do nothing. No file, no
  re-prompt. Silence means satisfied.

---

## Notes

- Never generate artifacts before profiling is complete. The whole point of
  running execution skills first is that document artifacts are grounded in
  real data — not assumptions.
- For feature-level work on an existing product, check whether a
  `requirements-acceptance-criteria` artifact already exists. If so, update it
  rather than creating a new one. The existing feasibility report may also be
  reusable — confirm with the user.
- The Discovery phase is explicitly iterative. If the feasibility report reveals
  a scope problem, it is correct to loop back and refine requirements before
  proceeding. Do not rush to gate.
- Cross-reference profiling quality findings with requirements. If a required
  source column has high null rates, flag it in both the feasibility report and
  the acceptance criteria — it is a risk in both dimensions.
