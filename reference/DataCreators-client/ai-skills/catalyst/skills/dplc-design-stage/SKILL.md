---
name: dplc-design-stage
description: >-
  Run the Design stage of the data product lifecycle -- from initial demand
  through design. Use when starting a new data product or adding a major
  feature. Trigger phrases: "define a data product", "new data product",
  "start the lifecycle", "run Define", "take me through Define".
allowed-tools: Read Grep
metadata:
  tier: orchestrator
  lifecycle-phase: cross-cutting
  dependencies:
    - dplc-prereq
    - dplc-triage
    - dplc-discovery
    - dplc-design
  consumes: []
  shared-components:
    core: []
    platforms: []
---

# Define Stage Orchestrator

Run all four phases of the **Define** stage in sequence:

| Phase | Orchestrator | Purpose |
|:------|:-------------|:--------|
| Phase 0 | `dplc-prereq` | Verify roles, infrastructure, and organizational readiness |
| Phase 1 | `dplc-triage` | Capture demand, check for duplicates, classify, map consumers |
| Phase 2 | `dplc-discovery` | Discover data, profile sources, assess feasibility, document requirements |
| Phase 3 | `dplc-design` | Define data contract, data model, transformation spec, architecture |

Each phase is a sub-orchestrator with its own detailed sequencing. This
orchestrator manages the phase-to-phase flow and gate checks.

---

## Skills Invoked

This orchestrator is a **delegating** stage orchestrator. It does
**not** invoke Phase 0/1/2/3 leaf skills (`phase-zero-checklist`,
`marketplace-search`, `discover-data`, `data-modeling`, `data-contract`,
etc.) directly -- those are owned by the per-phase sub-orchestrators.
Invoke each sub-orchestrator via the `Skill` tool (or by reading
`skills/<name>/SKILL.md` if the harness has not yet registered the
skill) -- never duplicate the phase sub-orchestrator's work in this
stage orchestrator. Never invoke this orchestrator (`dplc-design-stage`)
from inside itself; the slash command names the stage you are already
running.

| Sub-orchestrator | Phase | Required? |
|:-----------------|:------|:----------|
| `dplc-prereq` | Phase 0 -- Prereq | **Required -- always invoke** |
| `dplc-triage` | Phase 1 -- Triage | **Required -- always invoke** |
| `dplc-discovery` | Phase 2 -- Discovery | **Required -- always invoke** |
| `dplc-design` | Phase 3 -- Design | **Required -- always invoke** |

**Delegation rule:** for each phase, route through the phase
sub-orchestrator via the `Skill` tool (slash-command equivalents:
`/dplc-prereq`, `/dplc-triage`, `/dplc-discovery`, `/dplc-design`).
Do **not** invoke leaf skills directly from this orchestrator -- they
live one layer deeper, owned by the phase sub-orchestrator.

**Acknowledge and advance — don't inline-execute.** When you invoke a
phase sub-orchestrator (`Skill(dplc-prereq)`, `Skill(dplc-triage)`,
etc.) and it returns successfully, treat the phase as complete and
advance. When the `Skill` tool returns "Unknown skill" (Catalyst
skills aren't always in the runtime registry), READ the phase
sub-orchestrator's SKILL.md **once** as your acknowledgment of
delegation -- that read IS the delegation in this harness (the
behavior-test runner counts a `Read(skills/<name>/SKILL.md)` as a
sub-skill invocation, equivalent to a successful `Skill` call). Then
advance to the next phase.

Do **not** follow the sub-orchestrator's instructions inline by
reading its leaf SKILL.md files or its leaf templates. Each phase
sub-orchestrator owns its own phase; this stage orchestrator's job is
to invoke phases in order and present gate determinations, NOT to
execute the phase's body inline. Inline-execution cascades through
every leaf in every phase and exhausts the turn budget before reaching
the last phase. The leaf inventory above is informational only.

Process exactly one phase per delegation step: invoke (or
acknowledge-via-Read), present the gate, advance. Trust the
sub-orchestrator with its leaves.

### Phase 0 -- Prereq

| Skill | Type | Purpose |
|:------|:-----|:--------|
| `phase-zero-checklist` | document | Confirm roles and infrastructure readiness |

### Phase 1 -- Triage

| Skill | Type | Purpose |
|:------|:-----|:--------|
| `marketplace-search` | execution | Check if a product already exists |
| `demand-tracker-entry` | document | Create the formal demand tracker entry |
| `consumer-use-case-map` | document | Map consumers, use cases, and SLA needs |

### Phase 2 -- Discovery

| Skill | Type | Purpose |
|:------|:-----|:--------|
| `discover-data` | capability | Query Unity Catalog for source tables |
| `data-profiling` | capability | Profile tables for quality and fitness |
| `load-confluence-context` | capability | Retrieve docs from Confluence (optional) |
| `product-requirements-document` | document | Consolidate all discovery findings into the PRD |
| `feasibility-report` | document | Assess technical and data feasibility |
| `requirements-acceptance-criteria` | document | Document requirements and acceptance criteria |
| `outcome-kpi-statement` | document | Define measurable outcomes and KPIs |
| `effort-estimate` | document | Size the effort |
| `business-case` | document | Justify the investment (optional) |
| `privacy-impact-assessment` | document | Assess PII handling (required if PII detected) |
| `poc-spike-findings` | document | Document PoC results (optional) |

### Phase 3 -- Design

| Skill | Type | Purpose |
|:------|:-----|:--------|
| `data-modeling` | capability | Generate the conceptual data model (ER diagram + Design Rationale) |
| `column-lineage` | capability | Trace column-level lineage from SQL |
| `data-contract` | document | Define schema, SLAs, quality, versioning |
| `data-model` | document | Document logical and physical models |
| `transformation-spec` | document | Specify transformation logic with lineage |
| `architecture-diagram` | document | Document pipeline architecture (new patterns) |
| `schedule-backfill-plan` | document | Define schedule and backfill approach (optional) |
| `integration-blueprint` | document | Define integration interfaces (optional) |
| `dataops-handoff-draft` | document | Draft operational handoff plan |
| `nfr-specification` | document | Specify non-functional requirements (optional) |
| `security-design` | document | Security and access control (required if restricted) |

---

## Phase Gates

Each phase has an exit gate. Do not advance to the next phase until the gate
criteria are satisfied. Present the gate determination to the user and get
explicit confirmation before proceeding.

### Gate 0 -- Ready for Triage?

- Data Owner is identified and informed
- At least one Data Product Creator has capacity
- A Data Product Manager is identified and available
- **Pass** -> Phase 1 | **Fail** -> Address blockers

### Gate 1 -- Worth Pursuing?

- Demand tracker entry created with Data Owner approval
- Consumer use case map drafted
- Preliminary classification documented (domain, sensitivity, criticality)
- **Pass** -> Phase 2 | **Defer/Reject** -> Stop with reasoning

### Gate 2 -- Accepted, Feasible & Capacity?

- Data Owner approved the demand tracker entry
- Source data identified, discovered, and profiled
- Technical feasibility confirmed (or risks documented with mitigations)
- Requirements and acceptance criteria documented
- Team capacity confirmed, effort sized
- **Pass** -> Phase 3 | **No Capacity** -> Backlog | **Not Feasible** -> Park/Reject

### Gate 3 -- Design & Contract Approved?

- Data contract defined with schema, SLAs, quality expectations, versioning
- Logical and physical data models complete and reviewed
- Transformation logic specified
- Architecture documented (if new pattern)
- Security design approved (if restricted/regulated)
- **Pass** -> Deliver stage | **Fail** -> Rework design

---

## Sequencing

### Step 1 -- Gather context and determine starting phase

Check conversation and $ARGUMENTS for product name or description. Check the
workspace for existing artifacts to determine where to start:

- No artifacts -> start at Phase 0
- `phase-zero-checklist.md` exists -> start at Phase 1
- `demand-tracker-entry.md` exists -> start at Phase 2
- `feasibility-report.md` exists -> start at Phase 3

Search in this precedence order, matching `/build-preflight` and
`/dplc-concierge`: `$DPLC_DIR`, then `./.dplc/`, then `./docs/.dplc/`, then the
repository root. This table is shared with `dplc-concierge` -- the two must agree,
or the user is told two different starting phases for the same workspace.

Tell the user where you're starting and why. Get confirmation before
proceeding.

### Step 2 -- Execute phases in order

For each phase, delegate to the per-phase sub-orchestrator via the
`Skill` tool. Do not invoke leaf skills (`phase-zero-checklist`,
`marketplace-search`, etc.) directly from this orchestrator -- the
sub-orchestrators own that.

1. **Phase 0 -- Prereq:** Delegate to **`dplc-prereq`** via the `Skill`
   tool (slash-command equivalent: `/dplc-prereq`). On gate pass, carry
   the product name and role assignments forward.
2. **Phase 1 -- Triage:** Delegate to **`dplc-triage`** via the `Skill`
   tool (`/dplc-triage`). On gate pass, carry the demand tracker entry,
   classification, and consumer use case map forward.
3. **Phase 2 -- Discovery:** Delegate to **`dplc-discovery`** via the
   `Skill` tool (`/dplc-discovery`). On gate pass, carry all discovery
   artifacts (PRD, feasibility, requirements, profiling data) forward.
4. **Phase 3 -- Design:** Delegate to **`dplc-design`** via the `Skill`
   tool (`/dplc-design`). On gate pass, summarize the Define stage
   outcome.

Between each phase, present the gate determination and pause for the
user. Do not auto-advance. The user may need to address blockers,
consult stakeholders, or defer to a later session.

### Step 3 -- Summarize Define stage

When Phase 3 is complete and the design gate is passed:

> "Define stage complete. All four phases are done:
> - Phase 0: Prerequisites confirmed
> - Phase 1: Demand tracked, consumers mapped, classified as [domain/sensitivity/criticality]
> - Phase 2: Sources profiled, feasibility confirmed, requirements documented
> - Phase 3: Data contract, data model, and transformation spec approved
>
> The product is ready for the Deliver stage. Run `/dplc-build-stage [product-name]`
> to begin Build."

---

## Notes

- Context must flow forward between phases. Never re-ask for information that
  was captured in a prior phase.
- Each sub-orchestrator handles its own detailed sequencing. This orchestrator
  manages the macro flow and gate transitions.
- For feature-level work on an existing product, phases are lighter-weight.
  Check for existing artifacts and update them rather than creating new ones.
- If a gate fails, do not proceed. The lifecycle is gated for a reason --
  skipping gates creates rework downstream.
