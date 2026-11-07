# Post-plan Final-review Fix Report

**Date:** 2026-07-16

**Branch:** `feature/improvements`

**Baseline reviewed:** `0614a25` (`fix: resolve final modernization review findings`)

## Outcome

This pass resolves the five requested final-review areas while preserving the existing Docker-in-Docker, OAuth token refresh, and TLS enforcement behavior.

## Fixes

### 1. Harness environment host mappings

The five incorrect Databricks host overrides in `.harness/edo-training-data-products-pipeline.yaml` were restored from `main`. The resulting six deployment mappings are:

| Stage | Host environment | Region |
|---|---|---|
| dev primary | dev | us-east-1 |
| dev DR | dev | us-west-2 |
| SQA primary | sqa | us-east-1 |
| SQA DR | sqa | us-west-2 |
| production primary | prd | us-east-1 |
| production DR | prd | us-west-2 |

No other Harness pipeline logic was changed. A structural regression test now checks the complete ordered host list in `data_products/test_devcontainer_dind_wiring.py`.

### 2. Fresh-clone devcontainer bootstrap

`.devcontainer/devcontainer.json` no longer passes Docker `--env-file .devcontainer/.env`, so Docker does not reject a fresh clone before `postCreateCommand` can run. `.mise.toml` also no longer loads the missing file before its setup task creates it.

The existing `setup:env-file` task remains the single bootstrap point: it copies the tracked, secret-free `.devcontainer/utils/.env.example` to the git-ignored `.devcontainer/.env`. OAuth setup then reads that file after the container has started.

The explicit PAT path now exports the values sourced from `.devcontainer/.env` before handing off to `.devcontainer/utils/setup-databricks-config.sh`. This keeps PAT fallback functional without restoring Docker-level env-file injection.

### 3. dbt HTTP path wiring

All setup paths now map `DATABRICKS_HTTP_PATH` to the `DBT_HTTP_PATH` consumed by both tracked dbt profiles:

- OAuth contract: `.devcontainer/setup-databricks-dbt.sh`
- PAT contract: `.devcontainer/utils/setup-databricks-config.sh`
- Normalized shell environment: `.devcontainer/utils/normalize-env.sh`

Both `DATABRICKS_HTTP_PATH` and `DBT_HTTP_PATH` remain available, preserving Databricks CLI compatibility while satisfying dbt profile lookup.

### 4. Airflow settings template

A tracked, secret-free `.airflow/airflow_settings.yaml.example` now supplies the template already referenced by `.devcontainer/utils/setup-airflow-settings.sh`. It contains the empty connection/pool lists and the `databricks_job_prefix` placeholder that the setup script updates.

The setup guide, troubleshooting guide, and root README now use the same `.airflow/airflow_settings.yaml.example` and `.airflow/airflow_settings.yaml` paths. The documentation no longer instructs developers to hardcode a token in a tracked-style YAML example.

### 5. Cleanup and OAuth-first documentation

- Removed trailing whitespace from `.devcontainer/utils/.env.example`.
- Reworked `.devcontainer/README.md`, `GETTING_STARTED.md`, and `README.md` around the actual flow: open the devcontainer, let setup create the local env file, complete OAuth, and use PAT only as an explicit fallback.
- Documented that OAuth metadata is non-secret, shell tokens are short-lived, and CLI/dbt OAuth tokens are not persisted into Airflow settings.
- Corrected stale Airflow paths and connection ID references in `.devcontainer/TROUBLESHOOTING.md`.

## Regression coverage

`data_products/test_devcontainer_dind_wiring.py` now verifies:

1. startup does not require an untracked `.devcontainer/.env`;
2. setup still creates that file from the tracked safe template;
3. OAuth, PAT, and normalization scripts expose `DBT_HTTP_PATH`;
4. the Airflow setup script and documentation reference an existing tracked template; and
5. all Harness deployment stages use the expected environment- and region-specific hosts.

The new tests were observed failing for the unresolved findings before the implementation changes, then passing after the fixes.

## Validation

The following commands completed successfully after all code and documentation edits:

```bash
git diff --check
```

```bash
python -m pytest \
  data_products/test_devcontainer_dind_wiring.py \
  data_products/test_cert_wiring.py \
  data_products/test_tls_enforcement.py \
  data_products/test_devcontainer_python_target.py \
  -v
```

Result: **25 passed**.

```bash
sh -n \
  .devcontainer/utils/setup-airflow-settings.sh \
  .devcontainer/utils/setup-databricks-config.sh \
  .devcontainer/utils/normalize-env.sh \
  .devcontainer/utils/setup-databricks-dbt.sh \
  .devcontainer/post-start.sh \
  .devcontainer/start-dockerd.sh \
  .devcontainer/ensure-dockerd.sh

bash -n .devcontainer/setup-databricks-dbt.sh
```

## Remaining validation boundary

A live VS Code devcontainer rebuild and interactive Databricks OAuth browser login were not run from this host session. Static bootstrap regression tests, shell parsing, and the requested DinD/TLS/Python test suite cover the repository wiring; interactive authentication still depends on developer workspace access and browser availability.

### 6. Airflow settings follow-up

- `setup-airflow-settings.sh` now keeps the canonical root `airflow_settings.yaml`, adds both Databricks connection IDs, and only writes passwords in explicit PAT mode.
- The tracked `.airflow/airflow_settings.yaml.example` now mirrors both connection blocks with blank passwords.
- `healthcheck_all_platforms.dag.py` now uses the east-region SQA and PRD Databricks hosts only.
