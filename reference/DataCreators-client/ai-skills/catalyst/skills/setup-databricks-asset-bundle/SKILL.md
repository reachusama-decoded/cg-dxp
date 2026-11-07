---
name: setup-databricks-asset-bundle
description: |
  Scaffold the Databricks Asset Bundle (DAB) for a dbt data product in the
  edo-ig-data-products shape: writes one databricks.yml per product (with
  glob includes, sync paths, and local/dev/sqa/prd + DR targets), the
  variables/ directory (variables.yml + per-env + complex cluster shapes
  in clusters.yml), and per-dataset bundle files (one for the dbt run
  and one for Deequ DQ verification). Emits what
  actually deploys against the team's environment today; RFD 0012
  directives the team hasn't yet adopted (databricks_job_prefix, tags,
  permissions, webhook_notifications, serverless Python) are flagged
  inline as TODOs rather than enforced.
  Trigger phrases: "set up databricks asset bundle", "scaffold
  databricks.yml", "create job.yml for this dataset", "wire pipeline DAB",
  "set up dab for a new data product".
allowed-tools: Read Bash Write Edit Grep
metadata:
  tier: workflow
  lifecycle-phase: phase-4-build
  inputs:
    - data_products/{product}/dbt_project.yml          # product name + dbt model layout
    - data_products/{product}/datasets/{dataset}/contract/{dataset}.odcs.yaml  # contract drives ruleset names + classification
  dependencies: [databricks-bundles, write-dbt-wrapper]
  consumes: [setup-dbt-project, data-contract]
  emits:
    - data_products/{product}/databricks.yml
    - data_products/{product}/variables/variables.yml
    - data_products/{product}/variables/variables_{env}.yml   # scaffold per real env (dev/sqa/prd); mirror of targets.<env>.variables — not loaded by the bundle
    - data_products/{product}/variables/clusters.yml
    - data_products/{product}/datasets/{dataset}/bundle/{dataset}.job.yml
    - data_products/{product}/datasets/{dataset}/bundle/{dataset}_dq.job.yml
    - tests/dab/test_{dataset}_dab_structural.py
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    # Enforced today (see references/rfd-0012-citations.md for the full map).
    - DBX-BUNDLE-001           # bundle: name + targets
    - DBX-BUNDLE-002           # one bundle per data product
    - DBX-BUNDLE-009           # DBR LTS runtime
    # Deferred — emitted with inline TODO markers, not yet enforced:
    # DBX-BUNDLE-003 (promotions.yml hosts)
    # DBX-BUNDLE-004 (shared compute.yml T-shirts)
    # DBX-BUNDLE-006 (standard alert sink notifications)
    # DBX-BUNDLE-007 (cost-attribution tags)
    # DBX-BUNDLE-008 (explicit permissions block)
    # DBX-DAB-001 / DBX-DAB-004 (databricks_job_prefix)
    - DBX-DAB-002           # separate pipeline / compute DABs
    - DBX-DAB-003           # no email_notifications in pipeline DAB; failure alerting is platform-side (Astronomer Datadog), not a DAG callback
    # DBX-DAB-006 / DBX-DAB-008 (serverless Python via cgrepo)
    # Deploy-side, out-of-scope for emission:
    # DBX-BUNDLE-005 / DBX-SEC-002 (OAuth M2M — connect-databricks owns)
    # DBX-BUNDLE-010 (external tables — dbt model conventions)
---

# /setup-databricks-asset-bundle

Emit a Databricks Asset Bundle for a dbt data product in the
`edo-ig-data-products` shape — i.e. what the team's existing products
(`bloomberg`, `shared_ref`) actually use today. The skill defers some
RFD 0012 directives until the team adopts them; gaps are flagged inline
as `# TODO DBX-…` comments and tracked in
`references/rfd-0012-citations.md`.

This is not a greenfield "what should a DAB look like" skill. It's a
"what does this team's DAB look like" skill.

## When to invoke

- New data product needs a DAB scaffolded.
- New dataset added to an existing product (needs `<dataset>.job.yml` +
  `<dataset>_dq.job.yml`).
- Existing DAB needs refresh to match the current shape (the team rolled
  out a new variable, target, or cluster shape across products).

## When NOT to invoke

- The team's repo doesn't match the edo-ig-data-products layout (`data_products/<product>/datasets/<dataset>/bundle/`). Use the predecessor version of this skill for the `<product-root>/databricks.yml + variables_<env>.yml + datasets/<dataset>/bundle/*.job.yml` Catalyst-default layout.
- The consumer repo doesn't keep shared code at the expected sibling paths (`../../shared` and `../.blueprints/src` relative to `data_products/<product>/databricks.yml`). The emitted `sync.paths` assumes that monorepo layout.
- Bulk migrating 10+ existing products at once. Single-product-at-a-time only.
- Authoring the *compute* DAB (long-lived warehouses, shared interactive clusters). That's the lifecycle-separation boundary: persistent compute belongs in a separate compute DAB, not the pipeline DAB. Use `/configure-sql-warehouse` for the compute DAB and reference the resulting IDs here by variable only.

## Mandatory refusal patterns

**These patterns must be refused in real-time when the user asks for them.**

### Pattern 1: Email notifications in pipeline DAB

**User request:** "Add email_notifications.on_failure to my pipeline DAB job" or similar.

**Your action:**
1. **Refuse the request outright.** Do not emit `email_notifications.on_failure` blocks.
2. **Explain ownership.** State: "Failure alerting is handled platform-side by Astronomer's Datadog integration — not by a DAG-level callback and not by the DAB. The pipeline DAB should not emit email notifications — that creates a duplicate alerting channel."
3. **Cite the rule.** Reference DBX-DAB-003: "Failure alerting is owned platform-side (Astronomer Datadog); the DAB owns system signals."
4. **Redirect.** Point the user to the platform-side alerting model — failure notification is configured neither in the DAB nor via a DAG `on_failure_callback` (see `/generate-dag` and RFD 0011 PY-AIRFLOW-008).

### Pattern 2: Inline warehouse definitions in pipeline DAB

**User request:** "Add a sql_warehouse_definition block to my pipeline DAB" or "Define the warehouse here for convenience" or similar.

**Your action:**
1. **Refuse the request outright.** Do not emit `sql_warehouse_definition` or any inline persistent compute definitions.
2. **Cite the rule.** State: "Lifecycle-separation rule (DBX-DAB-002): persistent compute definitions belong in a separate compute DAB, not the pipeline DAB. This keeps the two concerns decoupled."
3. **Explain the boundary.** Persistent compute (warehouses, shared clusters) has a different lifecycle than the pipeline. The pipeline DAB references compute by variable only.
4. **Redirect.** Direct the user to `/configure-sql-warehouse` as the correct skill for authoring the separate compute DAB. Once the compute DAB is defined, reference the resulting IDs (e.g., `sql_warehouse_id`) here as variables.

## Inputs the skill reads

| Source | What it gives us |
|---|---|
| `data_products/<product>/dbt_project.yml` | Product name (for `bundle.name`), dbt model layout, dataset directory list |
| `data_products/<product>/datasets/<dataset>/contract/<dataset>.odcs.yaml` | ODCS contract — used for Deequ ruleset names + data classification |
| Conversation context | Per-env workspace hosts (until promotions.yml lands per DBX-BUNDLE-003), and per-env IDs that aren't in source control: `cluster_id`, `sql_warehouse_id`, MSK secret scope, util bucket, Datadog webhook ID |
| `variables/variables_<env>.yml` and `databricks.yml#targets.<env>.variables:` (existing) | When refreshing an existing product, prior per-env values are reused rather than re-prompted |

If the ODCS contract is missing, the DQ job emits with `# TODO`
placeholders for ruleset names.

## Emission patterns

The skill emits whichever of these the user is asking for.

| Mode | Trigger | What's emitted |
|---|---|---|
| **new-product** | New `data_products/<product>/` with no `databricks.yml` | Full set: databricks.yml + variables/{variables.yml, variables_dev.yml, variables_sqa.yml, variables_prd.yml, clusters.yml} + per-dataset bundle/{.job, _dq.job}.yml for every dataset in the product |
| **new-dataset** | Existing product, new dataset folder | Per-dataset bundle/{.job, _dq.job}.yml only. variables/ and databricks.yml unchanged (the `include: datasets/**/bundle/*.yml` glob picks up the new files automatically). |
| **add-target** | Existing product, new env (`prd_dr`, etc.) | New `targets.<env>:` block appended to `databricks.yml` with its own per-target `variables:` overrides, plus a `variables/variables_<env>.yml` scaffold for the env. No per-dataset changes. |
| **refresh** | Existing product, bring all files to the current template version | Diff each file against the current template; for each one the user hasn't manually edited (Catalyst-version header matches), regenerate. |

**Detecting hand-edits in refresh mode.** Each emitted file carries a `# Catalyst-version: N` header on line 3. A file is considered untouched and safe to regenerate when (a) its header version matches the current template's version *and* (b) a SHA-256 hash of the file's content (with the header line stripped) matches the hash of the template rendered with the file's recorded inputs — a baseline hash sidecar stored at `.catalyst/baselines/<relative-path>.sha256`. If either check fails the file is skipped and the user is warned with a one-line diff summary so they can resolve manually. The skill invokes `scripts/refresh_detect.py --repo-root <dir> --file <path> --template-version <int> --template-hash <hex>` per file and consumes its JSON verdict (one of `safe-to-regenerate`, `skip-hand-edited`, `bootstrapped`, `missing`).

**Bootstrap (first `mode=refresh` against a repo with no baselines).** `.catalyst/baselines/` is a skill-owned artifact; it doesn't exist in the team's repos today. On the first refresh against a product where no baseline sidecar is present:

1. The skill treats the current on-disk file as authoritative.
2. It invokes `scripts/refresh_detect.py --repo-root <dir> --file <path> --bootstrap`, which writes a baseline SHA-256 (computed against the on-disk file, header stripped) to `.catalyst/baselines/<relative-path>.sha256` and returns verdict `bootstrapped`.
3. It **skips** the diff comparison for that file in this run.
4. The user is told: "Bootstrapped N baselines. Re-run `mode=refresh` to get diff behavior." On the next refresh, the baseline exists and hand-edit detection works normally.

This avoids the catch-22 where the first refresh would either flag every file as edited (false positives) or silently overwrite hand-edits.

**Refresh-mode contract — preserves unrecognized blocks.** Refresh only touches the targets / variables / files the skill knows how to emit. Any target block the user has hand-added — a new env not yet in the skill's matrix — is left untouched. Within recognized blocks, the skill regenerates the fields it owns and leaves user-added keys alone. The matrix of "what the skill owns" is documented in `references/targets-matrix.md`.

See `references/bundle-root.md`, `references/variables-layout.md`,
`references/per-dataset-jobs.md`, `references/dq-jobs.md` for what each
file looks like.

## Steps

### Step 1 — Detect repo shape

```bash
# Confirm the layout matches edo-ig-data-products
test -d data_products && echo "data_products/ root present"
ls data_products/*/databricks.yml 2>/dev/null | head -3
ls data_products/*/datasets/*/bundle/*.job.yml 2>/dev/null | head -3
```

If the repo uses the older `<product-root>/databricks.yml + variables_<env>.yml + datasets/<dataset>/bundle/*.job.yml` Catalyst-default layout, stop and ask the user which layout they want. The two shapes are not interchangeable per-product.

### Step 2 — Gather context

Read in this order:

1. `data_products/<product>/dbt_project.yml` → product name, dataset list (from `model-paths` and the `datasets/` directory).
2. For each dataset: `data_products/<product>/datasets/<dataset>/contract/<dataset>.odcs.yaml` → classification, identity keys, Deequ ruleset hints if present.
3. Existing `variables/variables_<env>.yml` files and `databricks.yml` `targets.<env>.variables:` blocks, if present → reuse prior per-env values.

For per-env workspace hosts and per-env values not in source (cluster IDs, MSK config, util bucket), ask the user. The skill writes them into the matching `targets.<env>.variables:` block in `databricks.yml` and mirrors the same values into `variables_<env>.yml` as scaffolding so each env is reproducible.

### Step 3 — Pick the emission mode

Default: `new-dataset` when an existing `databricks.yml` is present, `new-product` otherwise. User can override (`mode=add-target`, `mode=refresh`).

### Step 4 — Emit files

Per mode (see table above). Each file is templated from
`templates/...`. Every placeholder used in the templates is listed below
with its source so the renderer knows where to pull each value. (Run
`grep -rohE '\{\{[A-Z_][A-Z0-9_]*\}\}' templates/ | sort -u` to keep this
table in sync.)

**Product / dataset identity**

| Placeholder | Source |
|---|---|
| `{{PRODUCT}}` | Product directory name = `bundle.name` |
| `{{DATASET}}` | Dataset directory name |
| `{{PROJECT_NAME}}` | User input — project umbrella (e.g. `edo-ig-data-products`) |
| `{{PROJECT_TEAM}}` | User input — project team identifier (e.g. `EDOIG`) |
| `{{APP_NAME}}` | User input — application slug (e.g. `ig_data_products`) |
| `{{ATM_ID}}` | User input — per-product Capital Group ATM ID |
| `{{TEAM_DISTRIBUTION_LIST}}` | Deprecated / no longer emitted in job templates (Airflow owns human alerts) |

**Per-env workspace + compute**

| Placeholder | Source |
|---|---|
| `{{DEV_WORKSPACE_HOST}}` / `{{SQA_WORKSPACE_HOST}}` / `{{PRD_WORKSPACE_HOST}}` | User input — per-env workspace host (e.g. `cg-db-caspian-ig-dev-us-east-1.cloud.databricks.com`) |
| `{{DEV_DR_WORKSPACE_HOST}}` / `{{SQA_DR_WORKSPACE_HOST}}` / `{{PRD_DR_WORKSPACE_HOST}}` | User input — DR-region workspace host |
| `{{DEV_PROFILE}}` | User input — local CLI profile name for the commented-out `profile:` line in `local` target |
| `{{DEV_CLUSTER_ID}}` | From the team's persistent cluster registry |
| `{{DEV_SQL_WAREHOUSE_ID}}` / `{{SQA_SQL_WAREHOUSE_ID}}` / `{{PRD_SQL_WAREHOUSE_ID}}` | From `/configure-sql-warehouse` output |
| `{{DEV_SQL_WAREHOUSE_HTTP_PATH}}` / `{{SQA_SQL_WAREHOUSE_HTTP_PATH}}` / `{{PRD_SQL_WAREHOUSE_HTTP_PATH}}` | From `/configure-sql-warehouse` output |

**Per-env catalogs + schemas**

| Placeholder | Source |
|---|---|
| `{{DEV_DEFAULT_CATALOG}}` / `{{SQA_DEFAULT_CATALOG}}` / `{{PRD_DEFAULT_CATALOG}}` | From the team's catalog registry (per-env Caspian default catalog) |
| `{{DEV_DEFAULT_SCHEMA}}` / `{{SQA_DEFAULT_SCHEMA}}` / `{{PRD_DEFAULT_SCHEMA}}` | From the team's schema registry (per-env default schema) |
| `{{DEV_CHECKPOINT_SCHEMA}}` / `{{SQA_CHECKPOINT_SCHEMA}}` / `{{PRD_CHECKPOINT_SCHEMA}}` | From the team's schema registry — schema that holds `standard_dataset_checkpoints` |
| `{{CHECKPOINT_TABLE_NAME}}` | From `dbt_project.yml` / team convention — usually `standard_dataset_checkpoints` |
| `{{DEV_APP_CATALOG}}` / `{{SQA_APP_CATALOG}}` / `{{PRD_APP_CATALOG}}` | From Caspian infra config — per-env IG app catalog |
| `{{DEV_DR_APP_CATALOG}}` / `{{SQA_DR_APP_CATALOG}}` / `{{PRD_DR_APP_CATALOG}}` | From Caspian infra config — DR-region app catalog |
| `{{DEV_CASPIAN_CATALOG}}` / `{{SQA_CASPIAN_CATALOG}}` / `{{PRD_CASPIAN_CATALOG}}` | From Caspian infra config — per-env source catalog |
| `{{SQA_TARGET_SCHEMA}}` / `{{PRD_TARGET_SCHEMA}}` | From dbt project / team convention — per-env write schema |
| `{{DEV_DR_TARGET_SCHEMA}}` / `{{SQA_DR_TARGET_SCHEMA}}` / `{{PRD_DR_TARGET_SCHEMA}}` | DR-region write schema |

**Per-env Kafka / data-notify / buckets**

| Placeholder | Source |
|---|---|
| `{{DEV_KAFKA_SECRET_SCOPE}}` / `{{PRD_KAFKA_SECRET_SCOPE}}` | From Caspian infra config — deprecated, paired with the ARN below |
| `{{DEV_KAFKA_SECRET_ARN}}` / `{{PRD_KAFKA_SECRET_ARN}}` | From Caspian infra config — AWS Secrets Manager ARN for Kafka creds |
| `{{DEV_ROOTCA_SECRET_ARN}}` / `{{PRD_ROOTCA_SECRET_ARN}}` | From Caspian infra config — AWS Secrets Manager ARN for Kafka root CA |
| `{{DEV_DATA_NOTIFY_TOPIC}}` / `{{SQA_DATA_NOTIFY_TOPIC}}` / `{{PRD_DATA_NOTIFY_TOPIC}}` | From Caspian infra config — Kafka topic for data-ready notifications (prd intentionally uses the same dev-style topic name today; the per-env block makes overrides explicit) |
| `{{DEV_MSK_BOOTSTRAP_BROKERS}}` / `{{PRD_MSK_BOOTSTRAP_BROKERS}}` | From Caspian infra config |
| `{{DEV_SCHEMA_REGISTRY_URL}}` / `{{PRD_SCHEMA_REGISTRY_URL}}` | From Caspian infra config |
| `{{DEV_ZONE_BUCKET}}` / `{{PRD_ZONE_BUCKET}}` | From S3 zone registry |
| `{{DEV_UTIL_BUCKET}}` / `{{PRD_UTIL_BUCKET}}` | From S3 zone registry |

**DQ job (Deequ)**

| Placeholder | Source |
|---|---|
| `{{DQ_APPLICATION_NAME}}` | User input / team convention (e.g. `caspian-im-foundation`) |
| `{{DQ_SCHEMA_TEMPLATE}}` | Team convention — env-templated schema (e.g. `"caspian_${var.env}.curated_ref"`) |
| `{{DATASET_RULESET_DATASET_NAME}}` | From the ODCS contract or user input — Deequ `dataset_name` |
| `{{DATASET_RULESET_NAME}}` | From the ODCS contract or user input — Deequ `ruleset_name` |

**Quoting convention:** every `{{...}}` placeholder in the templates is
wrapped in double quotes so the unrendered template parses as valid
YAML. The renderer substitutes the placeholder body (the surrounding
quotes stay valid YAML in the rendered output too). Mapping keys like
`"{{DATASET}}_job":` use the same quoting trick.

### Step 5 — Validate

The skill runs the validate call best-effort and surfaces the
stdout+stderr to the user. Soft-pass on auth failures (a missing token
in the workspace returns 403 on `/scim/v2/Me`); hard-fail on schema /
parser errors.

```bash
databricks bundle validate --target dev --output json
```

Why `--output json`: when the auth call fails but the bundle parses
fine, the JSON output still includes the resolved bundle structure;
that's enough to confirm the YAML is well-formed even without a working
workspace token. If you see a 403 on `/scim/v2/Me` and no schema errors,
treat that as a pass — the bundle structure is valid; the failure is
authentication, not the bundle itself. Fix the auth out-of-band
(`databricks configure` or set `DATABRICKS_TOKEN`).

The skill's behavior:

1. Attempt `databricks bundle validate --target dev --output json`.
2. Capture stdout + stderr.
3. If exit code != 0 *and* stderr matches `403` / `/scim/v2/Me` /
   `authentication`: soft-pass — surface the auth message but don't
   block.
4. Otherwise (schema error, parser error, unresolved variable): hard-fail
   and surface the exact CLI message.

Expected on success: `Validation OK`. Common failures:

| Error | Fix |
|---|---|
| `bundle.name does not match` | Reconcile `bundle.name` with the product directory name. They must match. |
| `cluster_id not set` | Fill `databricks.yml#targets.<env>.variables.cluster_id` with the team's persistent cluster ID. |
| `python_file not found` | Confirm `../../dbt_wrapper.py` exists (root-level wrapper); if not, run `/write-dbt-wrapper` first. |
| `${var.X} not declared` | Add the variable declaration to `variables.yml`. Per-target `variables:` blocks only override, they don't declare. |
| `notebook_path not found` | The Deequ verify notebook (`runtime/dq_verify`) must exist under the dataset folder. Authored separately — see Step 6 handoffs. |
| `403 on /scim/v2/Me` | Auth, not bundle. Soft-pass; configure a token and re-run when needed. |

### Step 6 — Handoffs

**Pre-handoff check — DQ notebook existence.** Before emitting any
`<dataset>_dq.job.yml`, the skill checks whether
`data_products/<product>/datasets/<dataset>/runtime/dq_verify.py`
exists. The DQ job's `notebook_task.notebook_path` resolves to that
file at deploy time; if it isn't there, `databricks bundle deploy` will
fail with a workspace-path error even though `validate` passes.

- If `runtime/dq_verify.py` **exists**: emit the DQ job YAML normally.
- If `runtime/dq_verify.py` **does not exist**: emit the DQ job YAML
  with a `# TODO: author runtime/dq_verify.py before deploy — see references/dq-jobs.md`
  comment at the top of the file, **and** surface a loud warning to the
  user in the handoff list below. Don't silently skip the DQ job — the
  scaffold should be there so the author has a starting point.

After the bundle validates, surface these to the user:

1. **`databricks.yml#targets.<env>.variables:` per-env IDs** — anything still placeholder. Most commonly: `cluster_id`, the SQL warehouse IDs, the MSK config (including `kafka_secret_arn` / `rootca_secret_arn`). Each needs a real value before deploy.
2. **`dbt_wrapper.py`** — must exist at repo root for the `spark_python_task` to resolve.
3. **Init scripts package mirrors** — if `init_scripts/install_requirements.sh` or `init_scripts/install_dqf_requirements.sh` installs Python packages, verify they use `--index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/` (or equivalent pip config). Public PyPI is blocked on the corporate network; cluster-start failures show up later in init-script logs, not in `databricks bundle validate`.
4. **DQ notebook source (`runtime/dq_verify.py`)** — for each dataset where the file was missing at emit time, the skill emits the job YAML with a TODO header. Author the notebook before `databricks bundle deploy` runs; the workspace-path resolution happens at deploy time, not validate time.
5. **Deequ ruleset** — the DQ notebook references a ruleset by name (`<dataset>_v<n>_base`). Confirm it exists in the application catalog.
6. **Airflow DAG** — orchestration lives in `data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag.yml`. The DAB doesn't declare a `trigger:`; Airflow calls the job via `DatabricksRunNowOperator`. See `/generate-dag`.
7. **Deferred RFD 0012 directives** — link the user to `references/rfd-0012-citations.md` so they can see which directives are still TODO and plan the migration.

## RFD 0012 compliance map

Every emitted file carries `# DBX-NNN-…` comments at lines tied to a
directive, plus `# TODO DBX-NNN: …` comments for the deferred ones.
`references/rfd-0012-citations.md` is the single source of truth: it
lists every directive, marks it emitted/deferred/n-a, and (at the top)
spells out **where each rule is enforced** (emission grep / structural
test / human review).

## Anti-goals

- **No serverless Python by default.** The real repo runs dbt on
  `existing_cluster_id`; serverless is deferred until the team validates
  it against their init-scripts + custom-JAR needs (DBX-DAB-006).
  "Serverless" here means **Lakeflow Jobs Serverless** — the auto-routed
  compute pool a task lands in when it has no `job_cluster_key`,
  `existing_cluster_id`, or `new_cluster` block (distinct billing line).
  Not the same as Interactive Serverless Compute (notebook sessions) or
  Lakeflow Declarative Pipelines Serverless (DLT) — both out of scope.
- **No job-level email notifications.** Airflow's
  on_failure_callback is the human-alerting owner for pipeline failures.
- **No PagerDuty / Slack notifications.** Datadog is the system-alert
  sink (when DBX-BUNDLE-006 webhook integration lands); Airflow's
  on_failure_callback handles human-facing alerts (per RFD 0011).
- **No inline cluster definitions** in `*.job.yml`. Cluster shapes live
  as complex vars in `clusters.yml`; jobs reference them
  (DBX-DAB-005 spirit).
- **No DAB-level trigger** for dataset jobs. Airflow owns scheduling.
- **No managed Unity Catalog tables.** External tables only
  (DBX-BUNDLE-010 — enforced at the dbt-model layer, not in this skill).

## See also

- `references/rfd-0012-citations.md` — the authoritative directive map; includes the "where each rule is enforced" matrix at the top.
- `references/bundle-root.md` — `databricks.yml` structure.
- `references/variables-layout.md` — variables/ directory conventions.
- `references/per-dataset-jobs.md` — `<dataset>.job.yml` anatomy.
- `references/dq-jobs.md` — `<dataset>_dq.job.yml` (Deequ) anatomy.
- `references/targets-matrix.md` — local/dev/sqa/prd + DR matrix.
- `references/compute-model.md` — when each compute shape applies.
