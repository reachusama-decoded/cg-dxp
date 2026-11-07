---
name: configure-sql-warehouse
description: |
  Provisions or reuses a Databricks serverless SQL warehouse for dbt workloads, scaffolds a
  compute DAB (separate lifecycle from the pipeline DAB), wires http_path and warehouse_id into
  profiles.yml and variables_{env}.yml, and documents the sizing decision. Use when setting up
  the SQL compute layer for a new data product or team scope, before running dbt against
  Databricks.
  Trigger phrases: "configure SQL warehouse", "set up serverless warehouse", "provision warehouse for dbt", "wire warehouse to profiles.yml".
allowed-tools: Read Bash Write Edit
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  dependencies: [databricks-dbsql, databricks-execution-compute]
  consumes: [nfr-specification]
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    # Canonical (RFD 0012 cross-ref)
    - DBX-SEC-002              # OAuth-only profile snippets (SP-owned objects)
    # Cross-ref pending RFD 0008 enumeration
    - DBX-UC-001               # Catalog vars per environment
    # Proposed (PR 94 prose → IDs, awaiting RFD 0008)
    - DBX-COMPUTE-001          # Serverless or PRO warehouse; no CLASSIC
    - DBX-COMPUTE-002          # Channel pinned explicitly
    - DBX-COMPUTE-004          # Auto-stop configured; never disabled
    - DBX-COMPUTE-005          # Channel = CURRENT (or PREVIEW + rollback)
    - DBX-COMPUTE-006          # Cluster policy applied via compute_policy_id
    - DBX-WORKFLOW-001         # Pipeline DAB and compute DAB are separate bundles
    - DBX-WORKFLOW-003         # Pipeline DAB references persistent compute by var only
---

# Configure SQL Warehouse

Provision or reuse a Databricks serverless SQL warehouse, wire it into your dbt project, and
document the sizing decision. This skill creates the **compute DAB** — a separate lifecycle file
from the pipeline DAB so warehouse definitions are not duplicated or inlined.

> **Depends on:** Read `skills/databricks-dbsql/SKILL.md` for warehouse API reference and
> `skills/databricks-execution-compute/SKILL.md` for cluster policy context. Read
> `skills/dbt-best-practices/references/sql-warehouse-sizing.md` before setting any size.

---

## Step 1 — Establish scope and naming

Ask the user:

> "What scope should this warehouse serve?
>
> - **per-product** — one warehouse per data product (most isolation, most cost)
> - **per-team** — one warehouse shared across a team's products (default recommendation for dev)
> - **per-workload** — separate warehouses for scheduled-batch vs interactive-BI
> - **per-env** — one warehouse per environment tier (dev / qa / prd), shared across all products
>
> What name should identify this scope? (e.g. `core-data`, `pricing-team`, `analytics-batch`)"

Once the user answers, derive:

- `<scope-name>` — the string they provide (e.g. `pricing-team`)
- `<compute-dab>` — `<scope-name>-compute.databricks.yml` (default; confirm with user)

Store both in `.catalyst-build.yml`:

```yaml
# .catalyst-build.yml (add or update)
compute_scope: per-team          # or per-product / per-workload / per-env
compute_dab_name: pricing-team-compute.databricks.yml
```

**Why a separate compute DAB?** The pipeline DAB (e.g. `databricks.yml` + job YAML files) is
deployed on every code change. The warehouse definition is a long-lived, shared infrastructure
resource. Keeping them in separate files means:

- Warehouse settings (size, auto-stop, policy) don't get accidentally overwritten by a pipeline
  deploy.
- Teams can manage warehouse lifecycle independently from data product releases.
- `/setup-databricks-asset-bundle` references the warehouse by `${var.warehouse_id}` from
  `variables_<env>.yml` — never by inlining the resource.

---

## Step 2 — Check for an existing warehouse

Before creating anything, list the available serverless SQL warehouses in the workspace:

```python
# skills/clients/databricks_tools_core/sql/sql.py
from databricks_tools_core.sql import list_warehouses

warehouses = list_warehouses()
for wh in warehouses:
    print(wh["id"], wh["name"], wh["state"], wh["cluster_size"])
```

Look for a warehouse whose name matches the scope (e.g. contains `pricing-team` or the product
name). If a match is found, present it to the user:

> "Found an existing warehouse: **pricing-team-dbt** (`Small`, id: `abc-123`, state: `RUNNING`).
>
> Options:
> - **Reuse** — write its ID to `variables_<env>.yml#sql_warehouse_id` and skip scaffolding.
> - **Create new** — scaffold a new warehouse definition in the compute DAB.
>
> Which do you prefer?"

If the user chooses **Reuse**, go directly to Step 5 (wire references) with the discovered
`warehouse_id` and `http_path`. Skip Steps 3–4.

---

## Step 3 — Scaffold the compute DAB (new warehouse)

Create `<scope-name>-compute.databricks.yml` at the repo root (or wherever `databricks.yml` lives).

Apply sizing from `skills/dbt-best-practices/references/sql-warehouse-sizing.md`:

| Environment | Workload shape | Starting size | Auto-stop | Channel |
|---|---|---|---|---|
| Production — scheduled dbt run | single connection, batch | Small | 10 min | CURRENT |
| Production — interactive / BI | high concurrency | Medium | 30 min | CURRENT |
| Dev | single developer | X-Small | 30 min | CURRENT |
| Sandbox | exploratory | 2X-Small | 5 min | CURRENT |

**Concrete example** (team-scoped, dev environment):

```yaml
# pricing-team-compute.databricks.yml
#
# COMPUTE DAB — separate lifecycle from pipeline DAB
# Deploy independently: databricks bundle deploy --target=dev --config=pricing-team-compute.databricks.yml
#
# Warehouse definitions live here, NOT in databricks.yml (pipeline DAB).
# Reference warehouses from jobs via ${var.warehouse_id} in variables_<env>.yml.

bundle:
  name: pricing-team-compute

include:
  - variables_dev.yml
  - variables_qa.yml
  - variables_prd.yml

targets:
  dev:
    mode: development
    workspace:
      host: ${workspace.host}

  qa:
    workspace:
      host: ${workspace.host}

  prd:
    mode: production
    workspace:
      host: ${workspace.host}

resources:
  sql_warehouses:
    pricing_team_dbt_dev:
      name: pricing-team-dbt-dev
      cluster_size: X-Small       # dev — single developer iteration
      auto_stop_mins: 30
      channel:
        name: CURRENT             # DBX-COMPUTE-002: pin channel explicitly
      warehouse_type: PRO         # valid values: PRO (recommended) or CLASSIC; never CLASSIC for new work
      enable_serverless_compute: true   # together with PRO, this declares a serverless SQL warehouse
      compute_policy_id: ${var.compute_policy_id}   # platform-team guardrail (Step 4)
      tags:
        scope: pricing-team
        env: dev
        managed_by: catalyst-build

    pricing_team_dbt_prd:
      name: pricing-team-dbt-prd
      cluster_size: Small         # production — single-connection dbt batch
      auto_stop_mins: 10
      channel:
        name: CURRENT
      warehouse_type: PRO
      enable_serverless_compute: true
      compute_policy_id: ${var.compute_policy_id}
      tags:
        scope: pricing-team
        env: prd
        managed_by: catalyst-build
```

> **DBX-COMPUTE-001**: Always use serverless or PRO warehouse type; never CLASSIC for new data
> products.
>
> **DBX-COMPUTE-004**: Auto-stop must be configured. Never leave auto-stop disabled. Default 10
> minutes for production, 30 minutes for dev.
>
> **DBX-COMPUTE-005**: Pin the channel explicitly to `CURRENT` for production. Use `PREVIEW`
> only with a documented rollback plan.
>
> **DBX-COMPUTE-006**: Apply a cluster policy (`compute_policy_id`) to every warehouse so
> platform-team guardrails (budget, instance type, region) are enforced.

---

## Step 4 — Apply cluster policy compliance

The platform team provides a `compute_policy_id` that enforces:

- Approved instance types (team does NOT pick)
- Budget caps per warehouse (team does NOT pick)
- Region constraints (team does NOT pick)

The team configures **within** the policy:

- T-shirt size (`cluster_size`)
- Auto-stop interval (`auto_stop_mins`)
- Max cluster count (for concurrency scaling; default 1 for dbt batch)

Ask the user:

> "What is your platform team's `compute_policy_id` for SQL warehouses?
> (Find it in Databricks → Compute → Policies, or ask your platform team.)"

Write the policy ID to each `variables_<env>.yml`:

```yaml
# variables_dev.yml (add)
variables:
  compute_policy_id:
    default: "AAAA1111-bbbb-cccc-dddd-eeee22223333"
```

```yaml
# variables_prd.yml (add)
variables:
  compute_policy_id:
    default: "FFFF5555-gggg-hhhh-iiii-jjjj66667777"
```

If the user does not yet have a policy ID, emit a warning and leave a placeholder:

```yaml
  compute_policy_id:
    default: "REPLACE_WITH_PLATFORM_POLICY_ID"   # TODO: get from platform team
```

---

## Step 5 — Wire references (profiles.yml + variables_<env>.yml)

After provisioning (or discovering) the warehouse, collect:

- `warehouse_id` — the warehouse resource ID (from list or after deploy)
- `http_path` — e.g. `/sql/1.0/warehouses/<warehouse_id>`

Write both into the dbt connection layer AND the bundle variable layer:

### profiles.yml

```yaml
# profiles.yml — dbt connection profile
# Per SQL-DBSQL-001 + DBX-SEC-002: OAuth M2M (service principal) is the standard auth.
# See /setup-dbt-project for the SP-PAT commented fallback and detection example.
pricing_team:
  target: dev
  outputs:
    dev:
      type: databricks
      host: "{{ env_var('DBX_HOST_DEV') }}"                  # SQL-DBSQL-007
      http_path: /sql/1.0/warehouses/abc1234567890def        # dev warehouse — wired by /configure-sql-warehouse
      auth_type: oauth                                        # SQL-DBSQL-001 + DBX-SEC-002
      client_id: "{{ env_var('DBX_CLIENT_ID') }}"             # service principal
      client_secret: "{{ env_var('DBX_CLIENT_SECRET') }}"
      catalog: "{{ env_var('DBT_CATALOG', 'sandbox') }}"     # DBX-UC-001
      schema: "{{ env_var('DBT_SCHEMA', 'pricing_team_dev') }}"
      threads: 4

    prd:
      type: databricks
      host: "{{ env_var('DBX_HOST_PRD') }}"
      http_path: /sql/1.0/warehouses/xyz9876543210abc        # prd warehouse
      auth_type: oauth
      client_id: "{{ env_var('DBX_CLIENT_ID') }}"
      client_secret: "{{ env_var('DBX_CLIENT_SECRET') }}"
      catalog: "{{ env_var('DBT_CATALOG') }}"
      schema: "{{ env_var('DBT_SCHEMA') }}"
      threads: 4
```

### variables_<env>.yml

```yaml
# variables_dev.yml (add warehouse vars)
variables:
  sql_warehouse_id:
    default: "abc1234567890def"
  sql_http_path:
    default: "/sql/1.0/warehouses/abc1234567890def"
  compute_policy_id:
    default: "AAAA1111-bbbb-cccc-dddd-eeee22223333"
```

```yaml
# variables_prd.yml (add warehouse vars)
variables:
  sql_warehouse_id:
    default: "xyz9876543210abc"
  sql_http_path:
    default: "/sql/1.0/warehouses/xyz9876543210abc"
  compute_policy_id:
    default: "FFFF5555-gggg-hhhh-iiii-jjjj66667777"
```

**Do NOT inline the warehouse resource definition in `databricks.yml`** (the pipeline DAB). Jobs
reference the warehouse by variable:

```yaml
# In a job YAML (pipeline DAB) — correct pattern
tasks:
  - task_key: dbt_run
    spark_python_task:
      python_file: data_products/pricing/dbt_wrapper.py
      parameters: ["run"]
    existing_cluster_id: ${var.warehouse_id}   # references variable, not inline resource
```

---

## Step 6 — Document the sizing decision

Update `.catalyst-build.yml` with the sizing rationale:

```yaml
# .catalyst-build.yml
warehouse_sizing_rationale:
  scope: pricing-team
  workload_shape: "single-connection dbt batch (scheduled, no concurrency)"
  dev_size: X-Small
  prd_size: Small
  starting_point_rationale: >
    Catalyst recommended starting point for scheduled dbt batch: Small (prd) / X-Small (dev).
    Single connection, sequential queries — IWM concurrency headroom not needed.
    Starting small per sql-warehouse-sizing.md guidance for single-connection workloads.
  up_scale_signals:
    - "bytes_spilled_to_disk in query profile (size up one level)"
    - "cold-run wall time exceeds SLA by >20% after 3 measurements"
  down_scale_signals:
    - "utilization < 20% for 15+ consecutive minutes"
  benchmarked: false   # set to true after running production-shape representative queries
  channel: CURRENT
  auto_stop_prd_mins: 10
  auto_stop_dev_mins: 30
```

Then emit this reminder to the user:

> **After your first production run**, open the warehouse monitoring page in Databricks and check:
>
> - **Bytes spilled to disk** in a representative query profile → if present, size up one level.
> - **Peak Queued Queries** consistently > 0 → size up OR increase max-cluster-count.
> - **Utilization low for 15+ minutes** → size down (or let the serverless autoscaler handle it).
>
> Update `warehouse_sizing_rationale.benchmarked: true` once you've validated against
> production-shape data. Set `benchmarked_at` and `final_size`.

---

## Checklist

Before calling this skill complete, verify:

- [ ] `compute_scope` and `compute_dab_name` written to `.catalyst-build.yml`
- [ ] Existing warehouse checked via `list_warehouses()` — reuse offered if found
- [ ] `<scope-name>-compute.databricks.yml` scaffolded (or reuse confirmed)
- [ ] `cluster_size`, `auto_stop_mins`, and `channel: CURRENT` set per environment
- [ ] `compute_policy_id` populated from platform team (or placeholder with TODO)
- [ ] `warehouse_id` + `http_path` written to `profiles.yml` for all targets
- [ ] `sql_warehouse_id` + `sql_http_path` written to `variables_<env>.yml` for all envs
- [ ] Warehouse resource NOT inlined in pipeline DAB (`databricks.yml`)
- [ ] `warehouse_sizing_rationale` block written to `.catalyst-build.yml`

---

## Standards enforced

### Canonical (RFD 0012 cross-ref)

| Rule | What it requires |
|---|---|
| DBX-SEC-002 | Profile snippets use OAuth M2M (SP-owned objects); see `/setup-dbt-project` for SP-PAT fallback pattern |

### Cross-ref pending RFD 0008 enumeration

| Rule | What it requires |
|---|---|
| DBX-UC-001 | Catalog variables resolved per environment |

### Proposed (PR 94 prose → IDs; awaiting RFD 0008)

| Rule | What it requires |
|---|---|
| DBX-COMPUTE-001 | Serverless or PRO warehouse type; no CLASSIC for new products |
| DBX-COMPUTE-002 | Warehouse channel pinned explicitly (not auto-resolved) |
| DBX-COMPUTE-004 | Auto-stop configured on every warehouse; never disabled |
| DBX-COMPUTE-005 | Channel pinned to `CURRENT` (or `PREVIEW` with rollback plan) |
| DBX-COMPUTE-006 | Cluster policy applied via `compute_policy_id`; platform-team guardrails enforced |
| DBX-WORKFLOW-001 | Pipeline DAB and compute DAB are separate bundles (lifecycle separation — load-bearing) |
| DBX-WORKFLOW-003 | Pipeline DAB references persistent compute by `${var.warehouse_id}`; never declares it inline |

---

## Reference files

| File | When to read |
|---|---|
| `skills/dbt-best-practices/references/sql-warehouse-sizing.md` | Sizing methodology, t-shirt size table, benchmarking protocol |
| `skills/databricks-dbsql/SKILL.md` | Warehouse API, DBSQL capabilities |
| `skills/databricks-execution-compute/SKILL.md` | Cluster policy context, compute mode decision matrix |
