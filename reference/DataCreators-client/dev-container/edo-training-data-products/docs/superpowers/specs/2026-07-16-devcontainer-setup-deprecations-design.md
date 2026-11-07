# Devcontainer Setup Deprecations Design

**Date:** 2026-07-16  
**Repository:** `edo-training-data-products`  
**Status:** Approved design (ready for implementation planning)

## 1. Problem Statement

The current setup surface still carries legacy pre-DinD and PAT-era tasks (`setup:host-path`, `setup:normalize-env`, `setup:databricks`) that no longer match the OAuth-first + DinD operating model. This creates user confusion, drift from `dpc-academy`, and avoidable startup complexity.

## 2. Evidence and Context

1. `dpc-academy` does not use `HOST_WORKSPACE_PATH` or a `set-host-path` script. Its `docker-compose.override.yml` uses relative mounts aligned to project layout.
2. In this repo, `setup:host-path` exists only to compute `HOST_WORKSPACE_PATH` for `docker-compose.override.yml`.
3. `setup:databricks` and `setup:normalize-env` encode old PAT-era assumptions and are not required by the default OAuth flow.
4. OAuth-first setup is already implemented through `setup:databricks` (renamed from `setup:databricks-oauth`), with explicit PAT fallback via `mise run setup:databricks --pat`.

## 3. Design Decisions

### 3.1 Remove host-path detection surface (approved)

- Delete `.devcontainer/utils/set-host-path.sh`.
- Remove `setup:host-path` from `.mise.toml`.
- Remove `HOST_WORKSPACE_PATH` usage and switch `docker-compose.override.yml` to a DPC-style relative bind mount:
  - `./data_products:/usr/local/airflow/dags`

### 3.2 Deprecate legacy PAT setup tasks from mise (approved)

- Remove `setup:normalize-env` task from `.mise.toml`.
- Remove `setup:databricks` task from `.mise.toml`.
- Keep PAT support only as an explicit path:
  - `mise run setup:databricks --pat`
- Keep `setup:env-file` only as optional bootstrap utility; it must not be required for OAuth.

### 3.3 Keep behavior-safe verification gates (approved)

- Update tests to assert the new task surface and compose mount contract.
- Update docs to remove references that imply host-path detection or legacy PAT task workflow.
- Validate in-container with:
  - `mise run setup`
  - `pytest`
  - `dpc-check`
  - `astro dev start` mount sanity

## 4. Non-Goals

- No changes to OAuth callback behavior, listener cleanup, or DinD startup/heal scripts unless required by failing verification.
- No removal of PAT fallback capability itself.

## 5. Risks and Mitigations

- **Risk:** Relative compose mount could break if users run Astro from the wrong directory.
  - **Mitigation:** Document repo-root invocation contract and keep troubleshooting guidance explicit.
- **Risk:** Removing legacy tasks may break undocumented user habits.
  - **Mitigation:** Keep PAT fallback through the supported setup script and update docs/commands to that path.

## 6. Success Criteria

1. No `setup:host-path`, `setup:normalize-env`, or `setup:databricks` tasks remain in `.mise.toml`.
2. `docker-compose.override.yml` no longer references `HOST_WORKSPACE_PATH`.
3. End-to-end startup and health checks pass with OAuth-first setup.
4. Documentation and tests reflect the new supported setup surface without contradiction.
