# DQMS Roles & Generic DQ RACI — reference context

**Read-only background.** This file orients the author on *who is accountable*
for data-quality decisions while they plan controls. It is **reference
scaffolding, not an artifact to generate**: the skill does **not** produce a
per-product RACI, and must not fill these cells with real names.

Whether the DPLC should generate a per-product `data-quality-raci` artifact is
an open governance question — see **`rfd/0019`** (Q1). Until that is decided,
use the tables below as framing only.

## DQMS roles (glossary)

| Code | Role | One-line responsibility |
|:-----|:-----|:------------------------|
| **DDO** | Data Domain Owner | Business owner accountable for quality, integrity, and usage of data in a domain; sets DQ expectations, thresholds, and priorities. |
| **DS** | Data Steward | Defines and maintains DQ rules, metrics (DQIs), and control design at domain level; monitors DQ performance and drives remediation. |
| **DPC** | Data Product Creator | Designs and builds the data product; implements DQ controls in the pipeline and owns the technical asset through its lifecycle. |
| **DPP** | Data Platform Provider / Data Ops | Provides and runs the platforms and tooling (e.g. DQF Next) that execute DQ checks; operates alerting and first-responds to failures in production. |
| **LOB DG** | LOB Data Governance | Bridges enterprise governance (EDG) and LOB execution; ensures DQMS standards are adopted and embedded. Often unnamed early — treat as optional. |

## Generic DQ RACI (blank template)

Standard DQ activities against the five roles. **Cells are intentionally
unfilled** — this is the shape of the accountability model, not an assignment.

> R = Responsible · A = Accountable (exactly one per row) · C = Consulted · I = Informed

| # | Activity | DPC | DS | DDO | LOB DG | DPP |
|:-:|:---------|:---:|:--:|:---:|:------:|:---:|
| 1 | Define DQ rules and thresholds | | | | | |
| 2 | Approve DQ rules | | | | | |
| 3 | Implement DQ checks in pipeline | | | | | |
| 4 | Monitor DQ results in production | | | | | |
| 5 | Triage DQ failures | | | | | |
| 6 | Approve exceptions for failing rules | | | | | |
| 7 | Sign off DQ for release | | | | | |
| 8 | Communicate DQ status to consumers | | | | | |

## How to use this while planning controls

- **Severity and action are accountability decisions, not just technical ones.**
  A `STOP` action commits DPP to first-response and DS to triage — do not assign
  one without a plausible owner for the resulting alert.
- **Name approvers, not a matrix.** The plan's *Approve & Sign-off* column and
  *Approval* table capture the specific DS / DDO who signed off on each control.
  That is the extent of accountability this skill records.
- If a product genuinely needs a full per-product RACI today, produce it outside
  this skill and reference it — do not extend the controls plan to cover it.
