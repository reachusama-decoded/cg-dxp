---
name: data-quality-controls-plan
description: |
  Derive a focused set of data-quality controls for a target table during
  Phase 3 Design. Turn data-profiling findings + business requirements into a
  small number of high-signal controls, each mapped to an EDGC DQ Rule Pattern,
  tagged with a DQ dimension, given a monitoring action (STOP / WARN / At-Rest)
  with a rationale, and expressed as a DQ Next (DQF) check so it is enforceable.
  Use when the user asks to "plan DQ controls", "propose data quality rules",
  "design data quality controls", or "DQ readiness". Feeds the data contract's
  Data Quality Rules table (§4).
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-3-design
  dependencies: []
  consumes:
    - data-profiling
    - requirements-acceptance-criteria
    - feasibility-report
  standards: []                 # EDGC DQ Rule Patterns Guidance is an external standard, not an RFD 0008 rule ID — see "Source of truth & scope" below
  shared-components:
    core: []
    platforms: []
---

# Data Quality Controls Plan

Propose a **focused, enforceable** set of data-quality controls for the target
table described in $ARGUMENTS — grounded in the EDGC DQ Rule Patterns standard,
driven by profiling evidence and business requirements, and expressed so they
can be handed to the DQ engine (DQF / DQ Next).

Use when the user asks to "plan DQ controls", "propose data quality rules",
"design data quality controls", or "DQ readiness".

## Source of truth & scope

- **Authoritative standard:** the CG Enterprise Data Governance Council (EDGC)
  **"DQ Rule Patterns Guidance"** — https://capitalgroup.atlassian.net/wiki/spaces/DGC/pages/90049068/DQ+Rule+Patterns+Guidance.
  Use its named rule patterns and the seven EDGC dimensions; do **not** invent
  rule names or dimensions.
- **Deterministic rules only.** Non-deterministic patterns (Variance, Standard
  Deviation, Regression, Time-Series checks) are Work-In-Progress in the EDGC
  standard and are **out of scope** here — note them as future if relevant.
- **Enforcement target:** every control maps to a **DQ Next (DQF) check** so the
  plan is directly implementable — this plan *feeds* DQF, it does not run checks.

## Author fewer, meaningful rules (read first)

More rules is not better. Excessive rules create noise, false positives, and
alert fatigue, and a rule that nobody acts on is pure overhead. Therefore:

- **Do not propose a rule per column by default.** Prioritise by business
  requirement, consumer expectation, criticality/regulatory exposure, and the
  quality gaps profiling actually surfaced.
- **Every proposed control must have all four of:** a named EDGC rule pattern, a
  DQ dimension, a **monitoring action** (STOP / WARN / At-Rest), and a
  **rationale** tying it to a real need. If you cannot state the action and the
  rationale, do not add the rule.
- **WARN requires a documented rationale** (per the EDGC standard: a WARN that
  does not resolve the condition needs a sound reason to exist).
- Prefer a short list of controls that will actually be monitored and acted on
  over exhaustive coverage.

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 3 — Design** |
| Precedes | Data Contract §4 (Phase 3), Data Quality Sign-Off (Phase 5), DQF check authoring |
| Depends on | Data Profiling (Phase 2), Requirements & Acceptance Criteria (Phase 2) |
| Gate | Contributes to *Design & Contract Approved?* — a baseline controls plan should exist before the contract's quality rules are finalized |

This is a **working design artifact**. The **authoritative** declaration of the
product's quality rules is the `data-contract` §4 table; once the contract is
approved, §4 — not this plan — is the source of truth.

## Instructions

1. Read the template at `templates/data-quality-controls-plan.md` for the exact
   structure, and the worked example at `references/exemplar.md` for the expected
   level of restraint and rationale — it profiles six columns and proposes five
   controls, and says why the sixth was skipped. For accountability framing (who
   owns a `STOP` alert, who signs off), see
   `references/dqms-roles-and-raci.md` — **background context only**; this skill
   does not generate a per-product RACI (see `rfd/0019` Q1).
2. Gather inputs (skip anything already provided): target table
   (`catalog.schema.table`), the columns/record sets in scope, and the business
   requirements.
3. **Use existing profiling evidence — do not re-run profiling.** Read the
   `data-profiling` / `profile-columns` output already in context. If none is
   available, mark the plan **preliminary — not data-validated**.
4. Select a **prioritised** set of controls (see *Author fewer, meaningful
   rules*). For each, fill every column of the DQ Controls table:
   - map it to a **named EDGC rule pattern** and its **DQ dimension** (catalog
     below);
   - set the **granularity** (Single-Attribute, Multi-Attribute, Record Set, or
     Cross Record Set);
   - give the **DQ Next check** (Deequ-style) that will implement it;
   - set the **action** (STOP / WARN / At-Rest) and a **rationale**;
   - set a **severity** (Critical / High / Medium / Low).
5. Honour business requirements — e.g. "client_id must never be null" → a
   Mandatory Value control at Critical with a STOP action.
6. Produce a document matching the template exactly.

## EDGC Rule Pattern Catalog (deterministic)

Map every control to one of these. `DQ Next` names are the DQF/Deequ checks.

| DQ Dimension | EDGC Rule Pattern | Typical Granularity | DQ Next check |
|:-------------|:------------------|:--------------------|:--------------|
| **Timeliness** | Data Timeliness (currency/age within agreed SLA) | Record Set | age/currency check |
| **Completeness** | Completeness Check (record count vs expected) | Record Set | `hasApproxCountDistinct` |
| **Completeness** | Mandatory Value (not null/blank, incl. conditional) | Single / Multi-Attribute | `areAnyComplete` / `isComplete` |
| **Conformity** | Valid Value — Invalid Characters | Single Attribute | `hasPattern`, `hasDataType` |
| **Conformity** | Valid Value — Format Conformance | Single Attribute | `hasPattern` |
| **Conformity** | Valid Value — Incorrect Precision | Single Attribute | `hasMaxLength` |
| **Consistency** | Record Set–Subset Sum Check | Record Set / Cross Record Set | `hasSum` |
| **Consistency** | Cross Record Set / Table Inconsistency | Cross Record Set | custom `sql` |
| **Duplication** | Uniqueness | Record Set | `hasUniqueness` |
| **Integrity** | Referential Integrity | Cross Record Set | FK/lookup check |
| **Integrity** | Schema Validation | Cross Record Set | schema check |
| **Accuracy** | Valid Value: Domain Range | Single Attribute | `satisfies`, `sql` |
| **Accuracy** | Valid Value: Domain List | Single Attribute | `isContainedIn` |
| **Accuracy** | Conditional Value | Single / Multi-Attribute | `sql` |
| **Accuracy** | Conditional Mandatory Value | Single / Multi-Attribute | `isComplete` |
| **Accuracy** | Sum of Proportion (100% Aggregation) | Record Set | `hasSum` |

> Out of scope (EDGC WIP, non-deterministic): Variance, Standard Deviation,
> Regression, Time-Series checks. Flag as future if a need is identified.

## Monitoring actions (from the EDGC standard)

Each control runs **In-Motion** (during the pipeline) or **At-Rest** (monitoring
quiescent data). In-Motion actions:

| Action | When to use | Maps to data-contract §4 |
|:-------|:------------|:-------------------------|
| **STOP** | Failure must halt the pipeline or quarantine invalid records (root-cause, isolate, or notify→rectify→reprocess) | Action on Failure = **Block delivery** |
| **WARN** | Log and continue; analyse/trend asynchronously. **Requires a documented rationale** — a WARN that resolves nothing is overhead | Action on Failure = **Flag and deliver** |
| **At-Rest** | No proactive in-motion action is possible; monitor the data at rest instead | Recorded as monitoring, not a delivery gate |

## Mapping into `data-contract` §4

Each planned control becomes one §4 row:

| Plan field | → | Data Contract §4 field |
|:-----------|:-:|:-----------------------|
| Column(s) / Record Set | → | Column(s) |
| Rule pattern + intent (note the DQ dimension in the text) | → | Rule Description |
| Severity | → | Severity |
| Action (STOP / WARN) | → | Action on Failure (STOP → Block delivery; WARN → Flag and deliver) |

> The DQ dimension and DQ Next check are recorded in the rule description /
> notes today. Whether §4 should carry a dedicated **DQ Dimension** column is an
> open standards question — see **`rfd/0019`** (Q2) — and is intentionally
> **not** changed here.

## Quality Checks

- [ ] The plan proposes a **prioritised** set of controls, not one-per-column
- [ ] Every control maps to a **named EDGC rule pattern** and one EDGC dimension
- [ ] Every control has a **DQ Next check**, an **action**, and a **rationale**
- [ ] Every **WARN** control states why WARN (not STOP) is appropriate
- [ ] No control lacks an action (a rule nobody acts on is not added)
- [ ] Only deterministic patterns are used (non-deterministic noted as future)
- [ ] Business requirements are reflected in at least one control
- [ ] Handoff maps each control to §4 and to `data-quality-sign-off`
- [ ] Output is comparable in shape and discipline to `references/exemplar.md`

## Execution Context

- **Profiling evidence:** use `data-profiling` / `profile-columns` output already
  in context (null rates, distinct counts, ranges) — do not re-run profiling.
  If none, mark thresholds **preliminary — not data-validated**.
- **Prior artifacts:** pull product name, classification, and quality thresholds
  from `requirements-acceptance-criteria`; sensitivity from `feasibility-report`.
- **Handoff:** the approved plan feeds `data-contract` §4 (authoritative) and
  `data-quality-sign-off` (Phase 5 evidence), and the DQ Next checks feed DQF.
- **Out of scope:** Excel export (Markdown-first; if ever added, install
  `openpyxl` via the internal cgrepo PyPI mirror, not public PyPI); the DQ
  RACI/DQMS stakeholder artifact (pending the RFD decision).
