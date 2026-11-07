# Required Tags (RFD 0011 §6 PY-AIRFLOW-007)

Per the discussion-state `rfd/0011/README.md` §6 (PY-AIRFLOW-007), every
emitted DAG MUST carry the tag set below. Future CI gates fail deploys
missing required tags (same pattern as gauntlet).

Tags use a `key:value` string convention so the structural test
(`assert_dag_compliant`) and the on-failure callback can parse them. Airflow
stores `DAG.tags` as `list[str]`, not a mapping — `key:value` strings are
how we get back to a parseable form.

## Required set

| Tag | Purpose | Example value | Where it comes from |
|---|---|---|---|
| `l1_domain` | Primary business / data domain | `investment_operations` | Data contract `domain` field; user input as fallback |
| `l1_xmatters_group` | Primary on-call group (AD group name). Context support reads for manual xMatters escalation; nothing in the DAG pages automatically. | `edo_ig_oncall` | User input (Step 3) |
| `lifecycle_phase` | Where the DAG is in its lifecycle | `build` \| `operate` \| `decom` | User input; new DAGs default to `build` |
| `data_classification` | Confidentiality level | `public` \| `internal` \| `confidential` \| `restricted` | Data contract `classification` field. **Never silently default.** When the contract has no field: production mode stops and asks; prototype mode emits `# TODO PY-AIRFLOW-007: data_classification` and warns. Either way the value is unresolved on disk until the user confirms — the skill never picks one. |
| `criticality` | Drives whether support escalates the platform Datadog alert to an xMatters page. Context support (and Datadog's tag-based monitors) read on the alert. | `critical` \| `high` \| `standard` | User input; no default. See `/generate-dag` Step 3 prompt mapping. |

## Optional set

| Tag | Purpose | When to use |
|---|---|---|
| `l2_xmatters_group` | Tier-2 escalation group | When the team has tiered on-call (typically only `criticality:critical` DAGs) |
| `l3_xmatters_group` | Tier-3 escalation group | Same as l2 |
| `app_id` | MDS application identifier (cost / SLO attribution) | When the team is registered in MDS |
| `business_function` | Business area for cost allocation | Useful for cross-cutting reporting |

## Routing model — what the tags actually do

Failure alerting is provided by Astronomer's platform Datadog integration —
there is **no** DAG-level `on_failure_callback` (PY-AIRFLOW-008). Both the Teams
notification (Datadog→Teams) and any xMatters page are **manual** escalations
done by the support team based on the platform Datadog alert.

The tags above are:

1. **Context support reads** on the platform Datadog alert — `criticality`,
   `l1_xmatters_group`, `l2_xmatters_group`, and `l3_xmatters_group` tell support
   whether to escalate and to whom. They are also available to Datadog's
   tag-based monitors. They are context, not triggers, and are not carried by a
   DAG-emitted event.
2. **Parsed by the structural test** (`assert_dag_compliant`) to enforce
   the required set is present.
3. **Visible in the Airflow UI** for ad-hoc triage.

Nothing in DAG code calls Datadog, Teams, or xMatters. That stays out-of-band.

## How the skill discovers values

1. **From DPLC artifacts** (if present in `data_products/<product>/datasets/<dataset>/contract/<dataset>.contract.yaml`):
   - `l1_domain` ← contract `domain` or `data_domain` field
   - `data_classification` ← contract `classification` field

2. **From user input** (Step 3 of `/generate-dag`):
   - Always prompt for `l1_xmatters_group`, `criticality`, `lifecycle_phase`
   - Optional prompts for `l2_xmatters_group`, `l3_xmatters_group`,
     `app_id`, `business_function`

3. **Mode-aware enforcement**:
   - `production` mode → all required tags present; refuse to emit if any missing.
   - `prototype` mode → emit `# TODO PY-AIRFLOW-007: <tag>` for any missing required tag and warn the user. Critically: this includes `data_classification` — the skill writes the TODO marker, but it does **not** invent a default. The user resolves the TODO before promoting to production. (This reconciles the "never silently default" rule with prototype mode: prototype allows the artifact to be on disk without the resolved value, but the value is never guessed.)
   - `lift-and-shift` mode → preserve existing tags + add the required set with `# ADDED by /generate-dag` comments.

## Emitted form

Pattern A (dag-factory) — `tags` is a `list[str]`:

```yaml
tags:                                            # RFD 0011 §6 PY-AIRFLOW-007
  - "l1_domain:investment_operations"
  - "l1_xmatters_group:edo_ig_oncall"
  - "lifecycle_phase:build"
  - "data_classification:restricted"
  - "criticality:standard"
  # Optional:
  # - "l2_xmatters_group:edo_ig_oncall_l2"
  # - "app_id:cap-invest-ops-001"
```

Pattern B (astro-blueprints) — same `list[str]` shape (Airflow standard):

```yaml
tags:                                            # RFD 0011 §6 PY-AIRFLOW-007
  - "l1_domain:investment_operations"
  - "l1_xmatters_group:edo_ig_oncall"
  - "lifecycle_phase:build"
  - "data_classification:restricted"
  - "criticality:standard"
```

Pattern C (pure Python `@dag`) — `tags=[...]`:

```python
@dag(
    ...,
    tags=[
        "l1_domain:investment_operations",
        "l1_xmatters_group:edo_ig_oncall",
        "lifecycle_phase:build",
        "data_classification:restricted",
        "criticality:standard",
    ],
)
```

## Migration note (from the old tag set)

The previous version of this skill used `owner`, `business_function`,
`data_domain`, `data_classification`, `app_id` as the required set. The
discussion-state RFD 0011 §6 replaced that set with the one above. Concrete
mapping:

| Old tag | New equivalent |
|---|---|
| `owner` | Folded into `l1_xmatters_group` (the AD group name) for routing purposes; freeform owner-email lives in `default_args.owner` as before |
| `business_function` | Moved to **optional** (still useful for reporting) |
| `data_domain` | Renamed to `l1_domain` |
| `data_classification` | Unchanged |
| `app_id` | Moved to **optional** |
| — | New: `lifecycle_phase` |
| — | New: `criticality` (drives manual xMatters escalation context) |
| — | New: `l1_xmatters_group` (+ optional `l2`/`l3` escalation) |
