# `DBX-WASTE-*` — In-Skill Index

The **canonical home** for DBX-WASTE-* rule definitions, thresholds,
detection logic, and worked examples is:

[`../../../rfd/0008/databricks/waste.md`](../../../rfd/0008/databricks/waste.md)

This file is now a slim pointer for skill maintainers. **Do not read
thresholds off this page.** If you are debugging or changing detection
logic, follow the link above; the RFD doc is authoritative and is the
source the `standards.yaml` `source:` pointers resolve against
(`databricks/waste.md#dbx-waste-NNN`).

If a threshold here disagrees with the RFD doc, the RFD doc wins. If a
threshold in `scripts/evaluate_findings.py` disagrees with the RFD doc,
that's a bug — fix the code (or the RFD if the code is intentional and
the doc is stale).

## Rule index

| Rule | Title | Severity |
|---|---|---|
| `DBX-WASTE-001` | Job cluster oversized vs. peak observed workers | `warning` |
| `DBX-WASTE-002` | Autoscale floor never relaxes | `warning` |
| `DBX-WASTE-003` | Long idle gaps between tasks within a job run | `info` |
| `DBX-WASTE-004` | dbt threads vs. cluster cores mismatch | `warning` |
| `DBX-WASTE-005` | Materialization heavier than usage justifies | `info` |
| `DBX-WASTE-006` | Incremental candidate still doing full refresh — **withdrawn** | `info` |
| `DBX-WASTE-007` | Spark config overrides likely stale or misconfigured | `warning` |
| `DBX-WASTE-008` | SQL warehouse oversized vs. query history | `warning` |
| `DBX-WASTE-009` | SQL warehouse under-provisioned (queueing) | `warning` |
| `DBX-WASTE-010` | dbt target points at all-purpose cluster for scheduled runs | `error` |

## Skill-implementation notes

These don't belong in the RFD doc but matter for anyone editing the
optimize-compute skill itself:

- **`DBX-WASTE-006` implementation removed.** The rule ID is reserved
  per RFD 0008's stable-ID policy and will not be reused. The
  evaluator does not emit it; the RFD doc retains the rule definition
  for the historical record only.
- **Cores resolution catalog.** `DBX-WASTE-004`'s `cores_per_worker`
  lookup is encoded in `NODE_TYPE_CORES` inside
  `scripts/evaluate_findings.py`. Unknown node types fall back to
  `DEFAULT_CORES_PER_WORKER = 4` and record `cores_assumed: true` in
  the finding's evidence. Caller-supplied
  `resolved_compute.cores_per_worker` overrides both — this is also
  the documented opt-in path for serverless callers (see RFD doc).
- **Warehouse event-type gating.** `DBX-WASTE-008` is gated out for
  serverless warehouses by `_gate_warehouse_events` in the evaluator.
  This is the implementation realization of the RFD's "serverless
  skip" decision.
- **Universal preconditions.** `run-history-window-days = 30`,
  `runs-per-job-cap = 200`, `min-runs-required = 10`. These are
  enforced in the evaluator and the RFD doc; see
  `run-history-signals.md` for endpoint-level rationale.

## Related skill references

- [`composition-with-adjacent-skills.md`](composition-with-adjacent-skills.md)
  — routing rules when a finding overlaps with another skill
  (node-type sizing, raw SQL, cluster lifecycle).
- [`dbt-config-audit.md`](dbt-config-audit.md) — `http_path`
  resolution logic used by `DBX-WASTE-004` and `DBX-WASTE-010`.
- [`run-history-signals.md`](run-history-signals.md) — endpoint
  inventory and per-rule data sourcing.
