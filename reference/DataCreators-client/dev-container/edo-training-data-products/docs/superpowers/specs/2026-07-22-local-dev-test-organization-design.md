# Local Dev Test Organization Design

## Purpose

Define a clear, low-friction structure for **local development environment tests** so contributors can quickly find the right check, run it at the right time, and avoid mixing runtime health checks with static contract tests.

## Scope

This design covers **local environment validation only** (devcontainer, DinD, local Airflow wiring, local auth/TLS contracts, and local tooling gates).

It does **not** redesign data product business logic testing strategy.

## Problem Statement

Current checks are effective but hard to discover because they are split across command gates and large mixed pytest modules. In particular:

1. `dpc-check` and `verify-with-databricks.sh` are command gates with different runtime assumptions.
2. Most pytest checks are deterministic file/script contract checks, but a subset is live integration.
3. `data_products/test_devcontainer_dind_wiring.py` combines many concerns, making ownership and intent unclear.
4. DAG integrity tests are not grouped with the rest of local-env tests in an obvious way.

## Design Principles

1. **Single scope:** local-env only.
2. **Primary split by execution mode:** offline vs live.
3. **Secondary split by domain:** devcontainer, airflow, auth, tls, etc.
4. **Keep operational gates as commands:** do not force `dpc-check` into pytest.
5. **Preserve fast default path:** contributors should run deterministic checks first.

## Target Taxonomy

### 1) Command Gates (outside pytest)

- `dpc-check` (`.devcontainer/check.sh`)
  - Role: live local preflight (container state, DinD readiness, TLS wiring, installed tools, auth signals).
- `scripts/verify-with-databricks.sh`
  - Role: external E2E gate (real Databricks + dbt connectivity and build).

### 2) Pytest Suites

```
tests/
  local_env/
    offline/
      devcontainer/
      airflow/
      auth/
      tls/
      tooling/
    live/
      auth/
      tls/
      cli_integration/
```

- **Primary meaning of folders**
  - `offline/`: deterministic checks; no required external network/auth side effects.
  - `live/`: checks that require real auth/network/external services.
- **Secondary meaning of folders**
  - Domain ownership and discoverability (`devcontainer`, `airflow`, etc.).
- **Markers**
  - Keep `integration` marker for live external checks.
  - Add domain markers (for example `airflow`, `devcontainer`) only when useful for slicing.

## Classification Rules

Use this rule for any test (including split DinD tests):

1. If it validates the **current runtime state now** by executing environment probes, it belongs to command gates (`dpc-check` / `verify-with-databricks.sh`).
2. If it is pytest and can run deterministically without external dependencies, put it in `tests/local_env/offline/...`.
3. If it is pytest and requires real external auth/network/service calls, put it in `tests/local_env/live/...` and mark `integration`.

### DinD Test Placement

Split DinD-related tests by behavior, not by filename history:

- Static assertions on `devcontainer.json`, shell scripts, compose wiring, and docs references -> `tests/local_env/offline/devcontainer/...`.
- Any DinD test that must call live external systems (if introduced later) -> `tests/local_env/live/...`.

## Proposed Migration Plan

1. Create `tests/local_env/offline` and `tests/local_env/live`.
2. Move existing local-env pytest files from `data_products/test_*.py` into appropriate new paths.
3. Split `test_devcontainer_dind_wiring.py` into focused modules:
   - runtime/devcontainer contract
   - local airflow contract
   - local auth contract
   - tls/tooling contract
4. Move live cert/tool checks to `tests/local_env/live/cli_integration/`.
5. Update `pytest.ini` test discovery to include the new test roots.
6. Keep `dpc-check` and `verify-with-databricks.sh` as first-class gates and document execution order.

## Developer Run Model

Recommended local sequence:

1. `dpc-check`
2. `pytest tests/local_env/offline`
3. Optional live suite: `CERT_INTEGRATION_TESTS=1 pytest tests/local_env/live -m integration`
4. `bash scripts/verify-with-databricks.sh`

Rationale: this minimizes failed runs caused by avoidable environment issues and keeps most feedback fast/deterministic before external gates.

## Success Criteria

1. A new contributor can answer “which test should I run?” from folder names alone.
2. Default pytest path is deterministic and does not unexpectedly require live auth.
3. Live tests are explicit and opt-in by path and marker.
4. No single local-env test module mixes unrelated concerns at the current scale of `test_devcontainer_dind_wiring.py`.

## Risks and Mitigations

- **Risk:** contributors continue running old paths.
  - **Mitigation:** keep temporary compatibility aliases and update docs with exact commands.
- **Risk:** test moves accidentally change collection behavior.
  - **Mitigation:** adjust `pytest.ini` in the same change and validate collection output.
- **Risk:** overuse of markers creates complexity.
  - **Mitigation:** keep markers minimal (`integration` + only high-value domain markers).
