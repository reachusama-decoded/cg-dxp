---
phase: "3 - Design"
artifact: "DQ Controls Plan"
data_product: "[Product Name]"
target_table: "[catalog.schema.table]"
date: "YYYY-MM-DD"
author: "[DPC name]"
status: "Draft | Approved"
---

# DQ Controls Plan — [Product Name]

> A **focused, enforceable** set of data-quality controls. Every control maps to
> an EDGC DQ Rule Pattern, has a monitoring action + rationale, and a DQ Next
> (DQF) check. Prioritised, not exhaustive — a rule nobody acts on is not added.
> Approved controls are codified into **data contract §4**, which is the
> authoritative source of truth. Deterministic patterns only.
>
> Standard: EDGC "DQ Rule Patterns Guidance" (DGC space, page 90049068).

## Scope

| Field | Value |
|:------|:------|
| Target table | `[catalog.schema.table]` |
| Row count (at profiling) | |
| Columns / record sets in scope | |
| Profiling date | |
| Business requirements summary | |

## Profiling Evidence

The quality signals used to justify the controls below (from `data-profiling` /
`profile-columns`; do not re-run profiling). List only what informs a control.

| Column / Record Set | Type | Null Rate | Distinct | Signal / concern |
|:--------------------|:-----|----------:|---------:|:-----------------|
| | | | | |

## Proposed DQ Controls

One row per proposed control — prioritised by business need, criticality, and
real profiling gaps. Every row needs a rule pattern, action, and rationale.

| # | Data Scope (attribute / record set) | DQ Dimension | EDGC Rule Pattern | Granularity | DQ Next Check | Action (STOP / WARN / At-Rest) | Rationale | Severity | Approve & Sign-off |
|:-:|:------------------------------------|:-------------|:------------------|:------------|:--------------|:-------------------------------|:----------|:---------|:-------------------|
| 1 | | Accuracy / Completeness / Conformity / Consistency / Duplication / Integrity / Timeliness | (named EDGC pattern) | Single / Multi-Attribute / Record Set / Cross Record Set | (e.g. `hasUniqueness`) | STOP / WARN / At-Rest | (why this rule + why this action; WARN needs a sound reason) | Critical / High / Medium / Low | Approved / Rejected — [DS or DDO, date] |

> Severity → default action: **Critical/High → STOP** (Block delivery);
> **Medium/Low → WARN or At-Rest** (Flag and deliver / monitor). EDG DQMS bands
> (Good ≥98% · Acceptable 95–98% · Unacceptable <95%) may set pass-rate
> thresholds where a rule is measured as a rate; the Data Steward may tighten.

## Rules Driven by Business Requirements

| Requirement | Resulting Control(s) | EDGC Rule Pattern | Severity |
|:------------|:---------------------|:------------------|:---------|
| | | | |

## Open Questions

| # | Question | Owner | Needed By |
|:-:|:---------|:------|:----------|
| 1 | | | |

## Handoff

| Downstream | What to carry forward |
|:-----------|:----------------------|
| `data-contract` §4 (Data Quality Rules) | Column(s), rule description (note the DQ dimension), Severity, Action on Failure (STOP → Block delivery; WARN → Flag and deliver) — becomes the authoritative source of truth |
| `data-quality-sign-off` (Phase 5) | Rule IDs + expected values for validation evidence |
| DQF / DQ Next | The DQ Next check per control, ready to author as an enforceable rule |

## Approval

| Role | Name | Decision | Date |
|:-----|:-----|:---------|:-----|
| DPC | | Approve / Reject | |
| DS | | Approve / Reject | |
| DDO | | Approve / Reject | |
