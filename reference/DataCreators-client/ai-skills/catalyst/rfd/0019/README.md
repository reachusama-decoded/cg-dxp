---
authors: NKV
state: discussion
discussion: https://github.com/cg-open-itg/catalyst/pull/415
labels: data-quality, governance, dqms, data-contract, dplc
---

# RFD 0019 Data Quality Controls in the DPLC: RACI/DQMS Accountability & Data-Contract Dimensions

## Problem

Reconciling the EDG `dq-control-planning` skill into Catalyst (AICAT-281)
shipped one uncontroversial piece — `/data-quality-controls-plan`, a Phase-3
leaf that proposes DQ controls from profiling + requirements and feeds the data
contract. Two further changes are **governance / standards decisions**, not
skill mechanics, and should be agreed before they are baked into Catalyst and
the DPLC:

1. **Should a DQ RACI / DQMS stakeholder artifact live in Catalyst and the
   DPLC** (Phase 3 Design), or does accountability mapping belong outside the
   lifecycle tooling?
2. **Should the data contract's `## 4. Data Quality Rules` table carry a
   dedicated `DQ Dimension` column** (the seven EDGC dimensions), or should the
   dimension be captured informally / deferred to the Data Contract Standard?

Per the DG working session (2026-08-04), these were explicitly routed to the
RFD process for broader discussion rather than decided unilaterally in the
reconciliation PR.

## Background

- **EDGC standard.** The CG Enterprise Data Governance Council publishes the
  [DQ Rule Patterns Guidance](https://capitalgroup.atlassian.net/wiki/spaces/DGC/pages/90049068/DQ+Rule+Patterns+Guidance):
  seven DQ dimensions (Timeliness, Completeness, Conformity, Consistency,
  Duplication, Integrity, Accuracy), named rule patterns per dimension, a
  granularity axis (single/multi-attribute, record-set, cross-record-set),
  In-Motion (STOP/WARN) vs At-Rest actions, and DQ Next (DQF) check names.
  Deterministic patterns only for now.
- **Near-term priority is the DQF transition.** Deeper DQ automation is
  deferred; the immediate goal is to support data-governance needs and feed DQF.
- **Anti-proliferation lesson.** Excess rules create noise and false positives;
  every rule needs a defined action and a rationale, and a rule nobody acts on
  is overhead. `/data-quality-controls-plan` already encodes this.
- **Current Catalyst state.** `data-contract` §4 has five columns (Rule ID,
  Column(s), Rule Description, Severity, Action on Failure);
  `data-quality-sign-off` carries a Rule Type enum; **RFD 0009 (the ODCS / Data
  Contract Standard) is referenced across the repo but not yet written.**
- **DQMS roles.** DPC (Data Product Creator), DS (Data Steward), DDO (Data
  Domain Owner), LOB DG (LOB Data Governance), DPP (Data Platform Provider /
  Data Ops).

## Proposal

### Q1 — DQ RACI / DQMS stakeholder artifact

Adopt a **DQ-scoped RACI** as a Phase-3 Design `document` leaf
(`data-quality-raci`) that maps the five DQMS roles onto the standard DQ
activities. Proposed artifact:

**Roles:** DDO, DS, DPC, DPP, LOB DG (each with 3 DQMS-aligned responsibility
bullets; LOB DG optional, defaults to `TBD` without blocking).

**Activities & default assignments** (R = Responsible, A = Accountable — exactly
one per row, C = Consulted, I = Informed):

| Activity | DPC | DS | DDO | LOB DG | DPP |
|:---------|:---:|:--:|:---:|:------:|:---:|
| Define DQ rules and thresholds | R | A | C | C | C |
| Approve DQ rules | C | A | R | C | I |
| Implement DQ checks in pipeline | R/A | C | I | I | C |
| Monitor DQ results in production | C | C | I | I | R/A |
| Triage DQ failures | C | A | I | I | R |
| Approve exceptions for failing rules | C | R | A | C | I |
| Sign off DQ for release | R | C | A | C | I |
| Communicate DQ status to consumers | R | C | A | I | C |

**Decision needed:** (a) adopt as a DQ-only DPLC artifact (recommended);
(b) adopt but widen to a Catalyst-wide stakeholder RACI (larger scope, own
initiative); or (c) do not put it in the DPLC — keep accountability mapping in
governance tooling. The drafted skill + template are ready if (a) is chosen.

### Q2 — `DQ Dimension` column in data-contract §4

Add a `DQ Dimension` column to §4, values constrained to the seven EDGC
dimensions, so the authoritative contract carries the governance tag rather than
leaving it in the (working) controls plan.

**Decision needed:** (a) add the column (aligns the contract with EDGC and DQF);
(b) keep §4 at five columns and record the dimension inside the rule description
(status quo, what the shipped skill does today); or (c) fold this into **RFD
0009** when the Data Contract Standard is written. Recommendation: decide here,
implement as part of RFD 0009 so the human contract and the ODCS
`contract.yaml` (`register-data-contract`) change together.

### Design tenets (apply regardless of Q1/Q2 outcome)

- Controls map to **named EDGC rule patterns**; **deterministic only** for now.
- Every control has a **monitoring action** (STOP / WARN / At-Rest) and a
  **rationale**; WARN requires a documented reason. Prioritise a small,
  high-signal set over exhaustive coverage.
- Each control expresses a **DQ Next (DQF) check** so the plan feeds DQF.

## Alternatives

- **Ship Q1 + Q2 in the AICAT-281 PR without an RFD** — rejected: both are
  governance/standards changes to a core artifact; the DG group asked for
  consensus first.
- **Never place a RACI in the DPLC** — viable (option 1c); accountability could
  live entirely in governance tooling. Trade-off: the DPLC loses an in-context
  accountability step at Design.
- **§4 stays five columns permanently** — viable (option 2b); dimension lives in
  the rule text and in `data-quality-sign-off`. Trade-off: no first-class,
  queryable dimension in the contract.

## Impact

- **`data-contract`** (core artifact) and **`register-data-contract`** (ODCS
  `contract.yaml`) — only if Q2(a); they must change together, ideally under
  RFD 0009.
- **`dplc-design`** — gains a RACI delegation step only if Q1(a).
- **`data-quality-controls-plan`** — already shipped and unaffected; it feeds §4
  via the rule description today and works under any outcome.
- **RFD 0009** — this RFD surfaces, and should be resolved alongside, the
  still-unwritten Data Contract Standard.
- **Migration** — minimal; no existing contracts require rework under the
  status-quo options.
