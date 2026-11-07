# Lift-and-Shift Flow

When retrofitting an existing DAG to RFD 0011 standards, `/generate-dag`
runs in `lift-and-shift` mode. The output goes to a **non-runtime
location** so the original DAG is never clobbered and Airflow's DAG
scanner can't pick up the proposal.

## Output location

```
workspace/dag-proposals/data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag-factory.yml
```

This mirrors the canonical runtime layout (see
`skills/scaffold-repo-structure/references/repo-structure.md`) under the
`workspace/` prefix. Filenames carry no version or RFD numbers — runtime
artifact paths must be free of such leakage.

## Flow

### Step 1: Read the existing DAG

```bash
cat data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag-factory.yml
# OR
cat data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag.yaml
```

Identify the existing format (dag-factory vs astro-blueprints vs raw Python DAG).

### Step 2: Map existing fields to RFD 0011 equivalents

For each existing field, decide:
- **Preserve** (already RFD-0011-compliant)
- **Augment** (add missing required field)
- **Replace** (existing field is incorrect or deprecated)

Common mappings:

| Existing | RFD 0011 equivalent | Action |
|---|---|---|
| Polling sensor (`dag_exec_check`) on upstream | Asset trigger | REPLACE — add `# TODO: migrate to Asset-driven` comment |
| Hard-coded job name | Templated via `var.value.databricks_job_prefix` | REPLACE |
| Missing MDS tags | Required tag set | AUGMENT — annotate with `# ADDED by /generate-dag` |
| `on_failure_callback: pagerduty.callback` | (none — Datadog alerting is platform-side) | REMOVE — no DAG-level alerting callback; PagerDuty is an anti-goal |
| Watermark-table pattern | Partition-keyed write | REPLACE — add `# REPLACED: watermark pattern rejected per RFD 0011` |
| `PythonOperator` with calculations | `DatabricksRunNowOperator` | REPLACE |
| `BashOperator` shelling to `dbt run` | `DatabricksRunNowOperator` referencing bundle job | REPLACE |

### Step 3: Emit proposal to workspace

```bash
mkdir -p workspace/dag-proposals/data_products/<product>/datasets/<dataset>/airflow/
# Write the proposed DAG content to:
# workspace/dag-proposals/data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag-factory.yml
```

The proposed file uses the same filename as the original (no suffix), just
under `workspace/dag-proposals/` instead of `data_products/`.

### Step 4: Emit a summary diff

Print to stdout:

```
/generate-dag lift-and-shift summary
====================================
Source: data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag-factory.yml
Proposal: workspace/dag-proposals/data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag-factory.yml

Changes:
  + Added 5 MDS tags (owner, business_function, data_domain, data_classification, app_id)
  + Added on_success_log_databricks_url callback
  ! Replaced dag_exec_check polling with Asset trigger (TODO: migrate)
  ! Removed PagerDuty callback (Datadog alerting is platform-side; no DAG-level callback)
  = Preserved schedule, owner, retries

Next step: diff the two files and merge manually when ready:
  diff -u data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag-factory.yml \
          workspace/dag-proposals/data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag-factory.yml
```

### Step 5: User reviews + adopts

User decides which changes to take, edits the runtime file by hand or copies
the proposal over. Skill does NOT auto-merge.

## Why this approach

- Original DAGs are running in production; auto-overwriting them is unacceptable.
- The user is the final arbiter — some lift-and-shift mappings (e.g., changing
  the trigger model) have operational consequences the team must accept.
- Filename-suffix approaches (`-rfd0011.dag-factory.yml`) leak version info
  into runtime artifact names, which the user explicitly rejected.
- Separate location (`workspace/dag-proposals/`) keeps the proposal out of
  Airflow's DAG scanner so it can't accidentally deploy.

## Bulk migration (out of scope)

Whether `/generate-dag` should handle the full `edo-ig-data-products` DAG
catalog (50+ DAGs) in one pass is tracked as **OQ-4**. For now: one dataset
at a time. Bulk migration would be a separate skill (`/retrofit-dag` or
`/migrate-dag`).
