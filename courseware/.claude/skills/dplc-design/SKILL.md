---
name: dplc-design
description: >-
  Phase 3 Design -- sub-orchestrator of dplc-design-stage. Generates data models and
  lineage first, then produces contracts, specs, and architecture grounded in
  real schema information. Trigger phrases: "design the product", "Phase 3",
  "create a data contract", "model the data", "define the schema".
allowed-tools: Read Grep
metadata:
  tier: orchestrator
  lifecycle-phase: phase-3-design
  dependencies:
    - data-modeling
    - column-lineage
    - data-quality-controls-plan
    - data-contract
    - data-model
    - transformation-spec
    - architecture-diagram
    - schedule-backfill-plan
    - integration-blueprint
    - dataops-handoff-draft
    - nfr-specification
    - security-design
  consumes:
    - requirements-acceptance-criteria
    - feasibility-report
    - consumer-use-case-map
  shared-components:
    core: []
    platforms: []
---

# Phase 3: Design Orchestrator

This orchestrator guides you through **Phase 3 — Design** of the Data Product
Lifecycle (see `rfd/0002/README.md` for the full definition).

**Phase 3 purpose:** Define the data product's data contract, logical and
physical data model, transformation specification, and architecture before
building. The data contract is the key artifact — it codifies what consumers
can depend on: schema, SLAs, quality expectations, and versioning strategy.

**Who this is for:** A Data Product Creator or Data Product Manager with
completed Discovery artifacts (feasibility report, requirements and acceptance
criteria, consumer use case map) ready to move into design.

**Phase 3 gate:** *Design & Contract Approved?*
- Data contract defined with schema, SLAs, quality expectations, and versioning
- Logical and physical data models complete and reviewed
- Transformation logic specified (model topology, materialization decisions, and backfill strategy; field-level transformations implemented in dbt SQL during Phase 4 Build)
- Architecture documented (required when introducing a pattern not in the
  approved pattern registry)
- Security design approved by InfoSec for Restricted products or named
  regulations (SOX, DORA, GLBA, Reg S-P, GDPR, CCPA)
- Yes → Build (Phase 4)
- No → Rework (address review feedback and resubmit)

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

This orchestrator is a **delegating** sub-orchestrator. It does **not** generate
ER diagrams, lineage maps, contracts, models, or transformation specs inline.
Each sub-skill below is a separate, purpose-built skill: invoke it via the
`Skill` tool (or by reading `skills/<name>/SKILL.md` if the harness has not
yet registered the skill) — never duplicate its work in this orchestrator.

| Skill | Type | Purpose | Required? |
|:------|:-----|:--------|:----------|
| `data-modeling` | execution | Generate the conceptual data model (ER diagram + Design Rationale: grain, SCD type, materialization) | **Required — always invoke** |
| `column-lineage` | execution | Trace column-level lineage from transformation SQL | **Required when SQL transformations are known.** Skip otherwise and note in the data contract that lineage tracing is deferred until SQL is authored in Phase 4 Build. |
| `data-quality-controls-plan` | document | Propose a focused set of DQ controls from profiling + requirements (EDGC rule patterns, STOP/WARN actions, DQ Next checks); feeds contract §4 | **Required when a target table is identified** |
| `data-contract` | document | Define schema, SLAs, quality thresholds, versioning, consumer expectations | **Required — always invoke** |
| `data-model` | document | Document the conceptual model referencing the ER diagram and target schema from the data contract | **Required — always invoke** |
| `transformation-spec` | document | Specify transformation logic with lineage and source schemas | **Required — always invoke** |
| `architecture-diagram` | document | Document pipeline architecture and integration design | Required for new patterns |
| `schedule-backfill-plan` | document | Define schedule, frequency, and backfill approach | Optional |
| `integration-blueprint` | document | Define inbound and outbound integration interfaces | Optional |
| `dataops-handoff-draft` | document | Draft operational handoff plan for DataOps team | Recommended |
| `nfr-specification` | document | Specify non-functional requirements (deviations from platform defaults) | Optional |
| `security-design` | document | Document security and access control design | **Required when classification is Restricted or named-regulation in scope (SOX, DORA, GLBA, Reg S-P, GDPR, CCPA)** |

Execution skills run first. Document artifacts must be grounded in the real
data model and lineage output — not in assumptions about what the schema
might look like.

**Delegation rule:** for every sub-skill listed above that applies to this
run, you **must** route through the dedicated skill (`/data-modeling`,
`/column-lineage`, `/data-contract`, `/data-model`, `/transformation-spec`,
etc.). Do **not** write the artifact body yourself in this orchestrator.
Inline generation defeats the purpose of the lifecycle — Phase 3 is a
composition of sub-skills, not a monolith.

---

## Sequencing

### Step 1 — Read Phase 2 artifacts

Before asking the user anything, check the conversation for prior phase
artifacts. Extract from context if available:

From `requirements-acceptance-criteria`:
- Business requirements and calculation definitions
- Acceptance criteria and quality thresholds
- Source systems and business logic

From `feasibility-report`:
- Confirmed source tables and profiling findings
- Technical risks and constraints
- Data sensitivity and regulatory exposure (drives security-design necessity)

From `consumer-use-case-map`:
- Consumer teams and their use cases
- Access patterns and SLA expectations
- Volume and freshness requirements

Do not re-ask for information that is already in context. Carry forward the
product name, classification (sensitivity/criticality), and consumer details
from Phases 1 and 2.

If Phase 2 artifacts are not in context, ask the user to provide requirements
and the list of source tables. Remind them that a completed feasibility report
and requirements artifact are expected inputs for Design.

Ask the user: "Do you have transformation SQL available? If so, please share it
or a file path — this enables column-level lineage tracing." The answer
gates Step 3 below: if SQL is known, invoke `/column-lineage`; if not,
skip it and note in the data contract that lineage tracing is deferred
until SQL is authored in Phase 4 Build.

### Step 2 — Invoke `/data-modeling` (Required, always)

**Delegate to the `data-modeling` sub-skill.** Use the `Skill` tool with
`skill: data-modeling` (slash-command equivalent: `/data-modeling`). Do not
hand-write DDL or draw an ER diagram in this orchestrator — that is exactly
what `data-modeling` exists to do.

Pass as input:
- Business requirements and acceptance criteria from Phase 2
- Source table list and profiling findings (grain, column names, types,
  quality issues)
- Consumer use cases and access patterns (inform materialization strategy)
- Any SQL the user provided

The skill produces:
- A Mermaid ER diagram of the target model
- A Design Rationale paragraph explaining grain, SCD type, and materialization decisions

Target schema (DDL) is owned by the data contract (RFD 0009); field-level
source-to-target transformations live in dbt SQL during Phase 4 Build.

Review the model output with the user before proceeding. Confirm:
- Is the grain correct?
- Are the SCD type and materialization strategy right?
- Are naming conventions consistent with the team's standards?

Carry the ER diagram and Design Rationale forward to the document skills.

### Step 3 — Invoke `/column-lineage` (conditional on SQL availability)

Check the answer from Step 1:

- **If SQL transformations are known** (the user supplied SQL inline,
  pointed to a file, or it is already in conversation context):
  **delegate to the `column-lineage` sub-skill.** Use the `Skill` tool
  with `skill: column-lineage` (slash-command equivalent:
  `/column-lineage`). Pass as input the SQL itself plus the target
  schema from the data contract (`contract/contract.yaml`, RFD 0009).
  The skill produces a
  column-level lineage map (source column → target column), a Mermaid
  lineage flowchart, and optionally OpenLineage JSON. Carry the lineage
  output forward to Steps 4 and 6.

- **If SQL is not yet known:** skip `/column-lineage` entirely. Do not
  invoke the sub-skill. Instead, when authoring the data contract in
  Step 4, note explicitly that column-level lineage tracing is deferred
  until SQL is authored in Phase 4 Build. The transformation spec in
  Step 6 should likewise flag the deferral.

This is the same shape as the security-design gate in Step 9: the
orchestrator decides whether to invoke based on a precondition (SQL
known here, Restricted/regulated there) — it does not flatten the
decision into an always-invoke.

### Step 4 — Data quality controls, then the contract: `/data-quality-controls-plan`, `/data-contract`

Propose the product's data-quality controls **before** finalizing the contract,
then codify them into it. Delegate to each sub-skill — do not draft either
artifact inline. (This step groups two related delegations, the same way Steps
8–9 group theirs.)

**Step 4a — `/data-quality-controls-plan` (Required when a target table is identified).**
Use the `Skill` tool with `skill: data-quality-controls-plan`. Turns the
`data-profiling` findings from Discovery + business requirements into a focused
set of controls, each mapped to an EDGC DQ Rule Pattern with a monitoring action
(STOP / WARN / At-Rest) and a DQ Next (DQF) check. Pass the profiling output and
business requirements. Prefer a small, high-signal set — not one rule per
column. If profiling was not run, the plan is *preliminary — not data-validated*.

**Step 4b — `/data-contract` (Required, always).** Use the `Skill` tool with
`skill: data-contract` (slash-command equivalent: `/data-contract`). Do not
draft the contract body inline — `data-contract` owns the structure, sections,
and required fields.

Pass as input:
- ER diagram and Design Rationale from Step 2 (target model shape, grain, SCD type, materialization)
- Schema details (field names, types, constraints) — the contract is the
  authoritative declaration here; this step authors that declaration
- Lineage output from Step 3 if SQL was known; otherwise a note that
  lineage tracing is deferred to Phase 4 Build
- **The approved DQ Controls Plan from Step 4a** — its controls are codified into
  the contract's **§4 Data Quality Rules**, which becomes the single source of
  truth (carry Column(s), rule description, Severity, Action on Failure). Do not
  re-derive rules or re-run profiling.
- Consumer SLA expectations from Phase 1 consumer use case map
- Quality thresholds from Phase 2 acceptance criteria
- Classification (sensitivity, criticality) from Phase 1

The data contract is the most important artifact in Phase 3. The sub-skill
ensures it covers:
- Schema with all output columns, types, nullability, and descriptions
- SLAs: freshness, availability, and latency
- Quality expectations: thresholds for each quality dimension
- Versioning strategy: how breaking and non-breaking changes are handled
- Consumer access: which teams are permitted consumers

### Step 5 — Invoke `/data-model` (Required, always)

**Delegate to the `data-model` sub-skill.** Use the `Skill` tool with
`skill: data-model` (slash-command equivalent: `/data-model`).

Reference the ER diagram and Design Rationale from Step 2, plus the target
schema declared in the data contract (Step 4). The document skill produces a
structured data model artifact covering the conceptual model. Do not
re-generate the model from scratch — use the execution skill output as the
authoritative source and document it.

### Step 6 — Invoke `/transformation-spec` (Required, always)

**Delegate to the `transformation-spec` sub-skill.** Use the `Skill` tool
with `skill: transformation-spec` (slash-command equivalent:
`/transformation-spec`).

Pass as input:
- Column lineage from Step 3 if SQL was known and `/column-lineage`
  produced output; otherwise the deferral statement (lineage tracing
  moves to Phase 4 Build)
- Source schemas from Phase 2 discovery
- Source-to-target mapping from the data-modeling output
- Business logic and calculation definitions from Phase 2 requirements

The transformation spec documents how source data becomes the target model:
field-by-field mapping, filter logic, join conditions, and derived field
calculations.

### Step 7 — Invoke `/architecture-diagram` (conditional)

Determine whether an architecture review is required:

- **Required:** The product introduces a pipeline pattern that is not in the
  organization's approved pattern registry. Ask the user: "Does this product
  use an approved architecture pattern from the registry?"
- **Not required:** The product implements an approved pattern. In this case,
  note in the summary that architecture review was not required.

If required (or if the user is unsure), **delegate to the
`architecture-diagram` sub-skill** (`Skill` tool with `skill:
architecture-diagram`, slash-command `/architecture-diagram`). Pass the
integration interfaces (sources, consumers, pipeline orchestration approach)
from the conversation context. Do not draw the diagram inline.

### Step 8 — Invoke `/schedule-backfill-plan` and `/integration-blueprint` (conditional)

**Schedule/backfill plan (Optional):** Ask the user: "Is the schedule or
backfill approach non-trivial — for example, multiple frequencies, complex
dependency chains, or large historical backfills?" If yes, delegate to the
`schedule-backfill-plan` sub-skill (`/schedule-backfill-plan`). If schedule
is straightforward, skip.

**Integration blueprint (Optional):** If the product has multiple source
systems or multiple consumer teams, delegate to the `integration-blueprint`
sub-skill (`/integration-blueprint`) to document inbound and outbound
interfaces. For simple single-source, single-consumer products, this may be
captured adequately in the transformation spec.

### Step 9 — Conditionally invoke `/nfr-specification`, `/security-design`, `/dataops-handoff-draft`

**NFR specification (Optional):** Standard platform NFRs apply by default.
Delegate to `nfr-specification` (`/nfr-specification`) only if this product
has non-standard requirements — for example, sub-second latency, extreme
scale, multi-region DR, or specific cost budget constraints. Ask the user:
"Are there NFRs that deviate from your platform's defaults?" If yes,
invoke the sub-skill. If no, skip.

**Security design (Required only when Restricted or regulated; conditional
otherwise):** Check the classification from Phase 1.
- **Invoke** `/security-design` (delegate to the `security-design`
  sub-skill via the `Skill` tool) **only if** the product is classified
  Restricted or above, **or** it is subject to a named regulation (SOX,
  DORA, GLBA, Reg S-P, GDPR, CCPA). In that case it is mandatory — InfoSec
  must approve before the phase gate can pass.
- **Skip** for all other products. Do not invoke `security-design` for
  Public, Internal, or Confidential products without a named regulation;
  security design is optional and the orchestrator must not force-call it.

**DataOps handoff draft (Recommended):** Delegate to `dataops-handoff-draft`
(`/dataops-handoff-draft`) to produce the initial operational handoff plan.
This document is finalized at the end of Build, but drafting it during
Design forces the team to think through runbooks, escalation paths, and
support tiers before the product is built. Ask the user: "Do you want to
draft the DataOps handoff plan now?" Recommend doing so, especially for
High or Critical criticality products.

### Step 10 — Summarize and report the gate determination

After all required artifacts are complete, assess the gate criteria and report.

**If all gate criteria are met:**
> "Phase 3 Design complete.
> - Data contract: defined (schema, SLAs, quality thresholds, versioning)
> - Data model: logical and physical models documented
> - Transformation spec: model topology, materialization decisions, and backfill strategy documented (field-level transformations are implemented in dbt SQL during Phase 4 Build)
> - Architecture: [approved pattern / new pattern reviewed]
> - Security design: [approved / not required]
>
> The design is ready for technical review by your technical leads and the data
> architect (if a new pattern was introduced). Once review sign-off is obtained,
> proceed to Phase 4 Build."

**If gaps remain:**
> List each gap specifically:
> - Missing artifacts (which ones and why they are required)
> - Unresolved design questions (e.g., grain not confirmed, SLA not agreed)
> - Required approvals not yet obtained (e.g., InfoSec review pending for
>   Restricted product)
>
> Recommend what must be resolved before the gate can be passed. The lifecycle
> is iterative — it is correct to loop back to Discovery if design reveals
> scope gaps.

### Step 11 — Invite feedback

After the gate determination, append this one-line prompt as the final line
of your response:

> "Anything to flag about this run? Hit enter to skip, or tell me what
> worked / what didn't."

Then:
- **If the user replies with anything substantive** — a sentence, a
  reaction, a problem description, even a short "worked great": invoke
  the `catalyst-feedback` skill with `$ARGUMENTS = "dplc-design
  reply=<their reply verbatim>"`. The skill extracts session context
  (sub-skills that ran, current phase, any errors), composes a draft
  issue, **shows the user the full draft for review**, and files after
  they confirm.
- **If the user hits enter / moves on / gives a non-substantive reply**
  (e.g. just "k", "ok", an emoji alone): do nothing. No file, no
  re-prompt. Silence means satisfied.

---

## Notes

- The data contract is the cornerstone of Phase 3. If the model is still
  changing, the contract should not be finalized — sequence model first,
  contract second.
- Column lineage enriches the transformation spec significantly. If SQL is not
  available during Design, flag that lineage tracing during Build is expected.
- Architecture review is required only for new patterns. Do not send every
  product through architecture review — it creates bottlenecks and discourages
  adoption.
- Security design is a hard gate for Restricted or regulated products. Do not
  skip it and assume InfoSec will review later — later often means Build, which
  is too late to redesign access controls.
- For feature-level work on an existing product, check whether a data contract
  already exists. If so, produce a contract diff or version update rather than
  a new contract. Schema changes should be assessed for backward compatibility
  before proceeding.
