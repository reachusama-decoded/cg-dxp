# Atlas Reliability Session Handoff (2026-07-24)

## Objective
Fix failing `atlas_elt_demo_*` Airflow DAGs in local devcontainer/Astro runtime and harden reliability for trainees.

## What Was Implemented
1. Added missing local Airflow Variables for notify templating in `docker-compose.override.yml`:
   - `AIRFLOW_VAR_DATA_NOTIFY_TOPIC`
   - `AIRFLOW_VAR_KAFKA_SECRET_SCOPE`
   - `AIRFLOW_VAR_BOOTSTRAP_BROKERS`
   - `AIRFLOW_VAR_SCHEMA_REGISTRY_URL`
   - `AIRFLOW_VAR_AWS_REGION`
2. Updated Atlas DQ cluster config in `data_products/atlas_elt_demo/variables/clusters.yml`:
   - Removed `cluster_log_conf`
   - Added `spark.databricks.cluster.profile: "singleNode"`
3. Added focused regression tests in `data_products/test_atlas_local_runtime_contract.py` for:
   - Required local Airflow variables in compose
   - Atlas DQ cluster compatibility contract
4. Added broader local-env coverage and `.databricks` ignore:
   - `.gitignore`
   - `data_products/test_devcontainer_dind_wiring.py`

## Commits Pushed
1. `87a91f6` — Harden Atlas local DAG runtime defaults
2. `cb66a29` — Expand local environment regression coverage
3. `6943294` — Add Atlas reliability guardrails design spec
4. `bb8ea87` — Refine spec for training-wide allowlist policy

## Runtime Findings
1. Duplicate Databricks jobs existed for Atlas names under `[dev gqp]` prefix (caused Airflow name lookup failures).
2. Older DQ failures included invalid `cluster_log_conf` (fixed in repo and redeployed).
3. Current major DQ blocker is Databricks artifact policy:
   - `PERMISSION_DENIED ... deequ-2.0.16-spark-3.5.jar is not in the artifact allowlist`
4. `atlas_elt_demo/clients` DQ job uses `existing_cluster_id`; other Atlas DQ jobs use `job_cluster_key`, so failure signatures can differ by dataset.

## Design Spec Created For Next Phase
`docs/superpowers/specs/2026-07-24-atlas-reliability-guardrails-design.md`

Approved direction:
1. Add `mise run atlas:preflight` entrypoint
2. Preflight does actionable remediation for:
   - duplicate jobs
   - missing `dqf_libs` volume / missing Deequ artifact
   - allowlist gating with explicit admin request template
3. Keep init script verification-only for volume presence (preflight handles creation)
4. Use workspace-scoped broad trainee allowlist model (bounded to training workspace/compute)

## Remaining Work To Finish Feature
1. Implement `atlas:preflight` command and helper scripts.
2. Add tests for duplicate detection/remediation and allowlist error classification.
3. Update runbook/instructions so Atlas validation always runs preflight first.
4. Re-run full 7-DAG Atlas validation after preflight implementation and policy setup.

## Useful Operational Commands (used during this effort)
1. Deploy Atlas bundle with explicit Terraform binary path when needed:
   - `DATABRICKS_TF_EXEC_PATH=/tmp/terraform databricks bundle deploy -t local`
2. Check duplicate jobs:
   - `databricks jobs list --output json | jq ...`
3. Trigger/check DAG runs from scheduler container:
   - `airflow dags trigger ...`
   - `airflow dags state ...`
   - `airflow tasks states-for-dag-run ...`

