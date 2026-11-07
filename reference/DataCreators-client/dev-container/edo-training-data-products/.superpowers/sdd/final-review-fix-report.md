# Final Review Consolidated Fix Report

This report is organized by finding so each review item has an explicit disposition, followed by validation evidence and remaining concerns.

## Findings

### 1. Harness and health-check environment hosts — adjudicated

No host values were changed. Git evidence proves the cited values predate the modernization range, and authoritative SQA/production workspace mappings are not available in this scope. See [final-review-adjudication.md](final-review-adjudication.md#finding-1--environment-specific-databricks-hosts) for commit and blame evidence. A separate deployment-owned change is required because guessing endpoints could route validation or deployment traffic to the wrong workspace.

### 2. Databricks setup placeholder handling — fixed

`.devcontainer/setup-databricks-dbt.sh` now:

- Treats only known token samples as placeholders; the documented training host and warehouse path remain valid defaults.
- Requires complete OAuth or PAT inputs and exits non-zero with a specific message instead of silently succeeding without authentication.
- Verifies the Databricks CLI exists and probes `current-user me` after OAuth login.
- Keeps PAT setup explicit through `--pat` or `FORCE_PAT_SETUP=1`.

Regression coverage is in `data_products/test_devcontainer_dind_wiring.py`.

### 3. Missing Airflow settings example — fixed

`.devcontainer/utils/setup-airflow-settings.sh` now reports that the optional template is missing and exits successfully instead of failing at `cp`. Existing settings and template-based setup behavior remain unchanged.

### 4. OAuth access-token persistence and reuse — fixed

OAuth setup now writes only non-secret host, warehouse, catalog, schema, and a private `DPC_DATABRICKS_AUTH_MODE` marker to `~/.config/dpc/databricks.env`. It no longer writes an OAuth access token.

`.mise/env.sh` clears inherited OAuth token variables and requests a current token from the Databricks CLI cache for the active shell. The marker is deliberately private rather than `DATABRICKS_AUTH_TYPE`, because the latter controls the Databricks CLI credential provider and `oauth` is not a supported provider name. Explicit PAT fallback behavior remains available.

### 5. `dpc-check` depth — fixed

`.devcontainer/check.sh` now verifies:

- Required `docker`, `python`, `databricks`, and `astro` commands.
- The inner Docker daemon.
- The three CA bundle paths installed by `.devcontainer/Dockerfile`.
- Tool versions.
- Live Databricks identity as a soft authentication check, so missing login is actionable but does not hide local image-health results.

Required local-image failures are accumulated and reported together.

### 6. Docker daemon recovery races and blocking — fixed

`.devcontainer/start-dockerd.sh` now serializes startup with a PID-owned lock, detects stale ownership, avoids duplicate daemon launches, terminates unhealthy daemon processes before removing PID files, and uses condition-based readiness checks.

`.devcontainer/ensure-dockerd.sh` now schedules a `nohup` recovery with `--no-wait` and returns immediately. Concurrent attach hooks defer to the startup lock rather than racing to kill and restart the daemon.

### 7. Host Docker socket troubleshooting — fixed

`.devcontainer/TROUBLESHOOTING.md` no longer instructs users to inspect or mount `/var/run/docker.sock`. Recovery steps now target the inner Docker daemon and its logs.

### 8. Pre-existing repository-structure test failure — adjudicated

The full suite still has the known `data_products/orders` failure. Git evidence shows both the expectation and missing directory predate modernization. See [final-review-adjudication.md](final-review-adjudication.md#finding-8--test_repo_structurepy-expects-data_productsorders). Restoring a data product or changing the initial structure contract requires a separate repository-owner decision.

### 9. Pytest integration marker — fixed

`pytest.ini` now registers the `integration` marker used by `data_products/test_cert_tool_integration.py`.

## Validation

Required targeted tests:

```text
python -m pytest data_products/test_devcontainer_dind_wiring.py data_products/test_cert_wiring.py data_products/test_tls_enforcement.py data_products/test_devcontainer_python_target.py -v
21 passed in 0.05s
```

Required shell syntax validation:

```text
sh -n .devcontainer/setup-databricks-dbt.sh .devcontainer/start-dockerd.sh .devcontainer/ensure-dockerd.sh .devcontainer/check.sh .devcontainer/utils/setup-airflow-settings.sh
exit 0
```

Additional validation:

```text
bash -n .mise/env.sh
git diff --check
exit 0

python -m pytest -v
1 failed, 74 passed, 3 skipped in 0.15s
```

The sole full-suite failure is `data_products/test_repo_structure.py::TestDirectoryStructure::test_expected_data_product_folders_exist[orders]`, adjudicated above.

## Remaining Concerns

- Authoritative SQA and production Databricks hosts and matching Harness secret mappings still require deployment-owner input.
- The obsolete `orders` structure expectation still requires a repository-owner decision.
- Live OAuth refresh and inner-dockerd recovery require the dev-container runtime and credentials; this pass validated their static wiring, shell syntax, and regression contracts but did not run those live external operations on the macOS host.

## 10. Airflow settings path and Databricks host fixes — fixed

- `setup-airflow-settings.sh` now maintains the canonical `airflow_settings.yaml` file that Astro loads locally.
- The tracked `.airflow/airflow_settings.yaml.example` template now includes a safe `databricks_default` connection block.
- The setup script fills that connection from local Databricks credentials when available.
- `healthcheck_all_platforms.dag.py` now points SQA and PRD Databricks checks at the environment-specific hosts instead of the dev host.
- The Harness pipeline mapping was already correct, so only an adjudication note was added there.

Validation run for this pass:

```text
python -m pytest data_products/test_cert_wiring.py data_products/test_devcontainer_dind_wiring.py data_products/test_tls_enforcement.py -v
sh -n .devcontainer/utils/setup-airflow-settings.sh
```
