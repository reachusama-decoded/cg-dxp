---
phase: "3 - Design"
artifact: "DQ Controls Plan"
data_product: "Client Master"
target_table: "caspian_prd.curated.client_master"
date: "2026-08-05"
author: "J. Doe (DPC)"
status: "Draft"
---

# DQ Controls Plan — Client Master

> **This is an exemplar** — a worked example of the artifact this skill produces.
> Note what it does *not* do: it profiles six columns but proposes **five
> controls**, because `country_code` showed no quality gap and has no business
> or consumer requirement behind it. Coverage is not the goal; a short list of
> controls that will actually be monitored and acted on is.
>
> Standard: EDGC "DQ Rule Patterns Guidance" (DGC space, page 90049068).

## Scope

| Field | Value |
|:------|:------|
| Target table | `caspian_prd.curated.client_master` |
| Row count (at profiling) | 1,240,388 |
| Columns / record sets in scope | `client_id`, `email`, `country_code`, `aum_usd`, `advisor_id`, `updated_at` |
| Profiling date | 2026-08-03 |
| Business requirements summary | Client reporting and advisor attribution. `client_id` must never be null (stated requirement). AUM figures are consumer-facing and must tie to the book of record. Daily batch; consumers read next morning. |

## Profiling Evidence

| Column / Record Set | Type | Null Rate | Distinct | Signal / concern |
|:--------------------|:-----|----------:|---------:|:-----------------|
| `client_id` | STRING | 0.00% | 1,240,388 | Distinct == row count — behaves as the primary key |
| `aum_usd` | DECIMAL(18,2) | 0.10% | 1,120,443 | Consumer-facing metric; p99 = 12.4M, no negatives observed |
| `advisor_id` | STRING | 1.80% | 8,742 | ~22.3k rows reference an advisor absent from `advisor_dim` (orphans) |
| `updated_at` | TIMESTAMP | 0.00% | — | Daily batch; observed range 2019-01-02 → 2026-08-03, max age 18h |
| `email` | STRING | 3.20% | 1,201,050 | Null rate sits in the EDG *Acceptable* band (95–98%) — baseline gap, see Open Questions |
| `country_code` | STRING | 0.00% | 12 | Clean; all 12 values valid ISO-3166. **No control proposed** — no gap, no requirement |

## Proposed DQ Controls

| # | Data Scope (attribute / record set) | DQ Dimension | EDGC Rule Pattern | Granularity | DQ Next Check | Action (STOP / WARN / At-Rest) | Rationale | Severity | Approve & Sign-off |
|:-:|:------------------------------------|:-------------|:------------------|:------------|:--------------|:-------------------------------|:----------|:---------|:-------------------|
| 1 | `client_id` | Completeness | Mandatory Value | Single Attribute | `isComplete` | STOP | Stated business requirement — `client_id` must never be null. A null key makes the row unattributable to any client, so the batch must not ship. | Critical | Approved — A. Smith, 2026-08-05 |
| 2 | `client_id` | Duplication | Uniqueness | Record Set | `hasUniqueness` | STOP | `client_id` is the grain of the product. A duplicate silently double-counts a client in every downstream AUM figure. | Critical | Approved — A. Smith, 2026-08-05 |
| 3 | `aum_usd` | Accuracy | Sum of Proportion (100% Aggregation Check) | Record Set | `hasSum` | STOP | Total AUM must tie to the book of record. This is the consumer-facing number; publishing an untied total is a reporting incident. | Critical | Approved — P. Lee, 2026-08-05 |
| 4 | `advisor_id` → `advisor_dim` | Integrity | Referential Integrity | Cross Record Set | FK / lookup check | WARN | ~1.8% orphans exist today, largely newly onboarded advisors not yet in the dimension. **WARN, not STOP:** the condition is known, self-resolves on the next advisor load, and blocking the whole client batch over advisor lag would be disproportionate. Trend weekly; escalate to DS if it exceeds 3%. | High | Approved — A. Smith, 2026-08-05 |
| 5 | `client_master` (record set) | Timeliness | Data Timeliness | Record Set | age / currency check | WARN | Consumers read the table each morning and need same-day data. **WARN, not STOP:** a late batch is still correct data — alerting DPP to a delay is useful, halting the pipeline is not. Alert if max age > 26h. | Medium | Approved — K. Patel, 2026-08-05 |

> **Deliberately not proposed:** a format control on `email` (see Open Questions — the
> gap is completeness, not conformity, and the owner is unresolved), and any control on
> `country_code` (no observed gap, no requirement — a rule here would generate signal
> nobody has agreed to act on).
>
> Severity → default action: **Critical/High → STOP** (Block delivery);
> **Medium/Low → WARN or At-Rest** (Flag and deliver / monitor). Deterministic
> patterns only — a variance check on `aum_usd` day-over-day was considered and
> deferred (non-deterministic, EDGC WIP).

## Rules Driven by Business Requirements

| Requirement | Resulting Control(s) | EDGC Rule Pattern | Severity |
|:------------|:---------------------|:------------------|:---------|
| "`client_id` must never be null" | #1 | Mandatory Value | Critical |
| AUM must tie to the book of record | #3 | Sum of Proportion (100% Aggregation) | Critical |
| Consumers read next morning | #5 | Data Timeliness | Medium |

## Open Questions

| # | Question | Owner | Needed By |
|:-:|:---------|:------|:----------|
| 1 | `email` is 3.2% null (EDG *Acceptable* band). Is this an accepted baseline for clients who never supplied an address, or a collection gap to remediate? Answer decides whether a Mandatory Value control is added at all. | DS / DDO | Before contract approval |
| 2 | Should the `advisor_id` orphan threshold (3%) be a contract SLA, or stay a monitoring trigger? | DS | Phase 5 |

## Handoff

| Downstream | What to carry forward |
|:-----------|:----------------------|
| `data-contract` §4 (Data Quality Rules) | Controls #1–5 as DQ-001…DQ-005. STOP → *Block delivery* (#1, #2, #3); WARN → *Flag and deliver* (#4, #5). DQ dimension noted in each rule description. |
| `data-quality-sign-off` (Phase 5) | Rule IDs DQ-001…DQ-005 + expected values for validation evidence |
| DQF / DQ Next | `isComplete`, `hasUniqueness`, `hasSum`, FK lookup, age check — ready to author as enforceable rules |

### How these land in data contract §4

| Rule ID | Column(s) | Rule Description | Severity | Action on Failure |
|---------|-----------|------------------|----------|-------------------|
| DQ-001 | `client_id` | Must be non-null (Completeness) | Critical | Block delivery |
| DQ-002 | `client_id` | Must be unique — one row per client (Duplication) | Critical | Block delivery |
| DQ-003 | `aum_usd` | Total AUM must reconcile to book of record (Accuracy) | Critical | Block delivery |
| DQ-004 | `advisor_id` | Must reference an existing advisor in `advisor_dim` (Integrity) | High | Flag and deliver |
| DQ-005 | (record set) | Data no more than 26h old (Timeliness) | Medium | Flag and deliver |

## Approval

| Role | Name | Decision | Date |
|:-----|:-----|:---------|:-----|
| DPC | J. Doe | Approve | 2026-08-05 |
| DS | A. Smith | Approve | 2026-08-05 |
| DDO | P. Lee | Approve | 2026-08-05 |
