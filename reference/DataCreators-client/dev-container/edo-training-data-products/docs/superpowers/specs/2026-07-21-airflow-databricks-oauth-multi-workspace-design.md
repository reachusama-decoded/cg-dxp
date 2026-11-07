# Airflow Databricks OAuth Multi-Workspace Design

## Goal

Enable local Astro/Airflow in the devcontainer to authenticate Databricks operators and hooks with OAuth-first behavior across multiple workspaces, without requiring PATs by default.

## Decision Summary

Recommended design is a **multi-connection OAuth sync control plane**:

1. Model workspace as first-class config (`workspace_key -> databricks_conn_id + host + profile`).
2. Keep Airflow Databricks usage connection-based (no provider patching).
3. Run an internal Airflow sync workflow that refreshes each mapped connection token only when changed or near expiry.
4. Keep PAT support as explicit per-connection fallback only when OAuth is blocked.

## Why This Design

This design balances developer ease and reliability:

- It preserves existing DAG/operator/hook behavior (everything still uses `databricks_conn_id`).
- It avoids Docker file-watch fragility across macOS/Windows nested container flows.
- It avoids invasive changes to Airflow Databricks provider internals.
- It supports one Airflow environment serving many data products with potentially different Databricks workspaces.

## Claim Validation

### Claim 1: Single workspace per repo is not guaranteed

**Validated.** Confluence guidance explicitly allows a logical lakehouse to map to multiple workspaces.

- Source: `Lakehouse Models - Single Tenant vs. Multi-Tenant - GUIDELINES - DRAFT` (`IntegrationArchitecture`, page `55222503`), including language that a lakehouse may be served by `1..N workspaces`.

### Claim 2: One data product maps to one logical workspace

**Reasonable default, not hard-enforced platform invariant.** Current repo patterns align with this, but architecture guidance allows different physical mappings by model.

- Repo evidence: data products currently use shared host/connection patterns.
- Confluence evidence: workspace is treated as execution boundary and can vary by tenancy model.

### Claim 3: One Airflow environment serves multiple data products

**Matches current implementation.**

- Repo evidence: shared Databricks connection IDs (`caspian-training-databricks`, `databricks_default`) are reused across multiple dataset DAG configs.
- Repo IaC patterns are deployment-centric (single deployment context with many DAGs/data products).

## Architecture

### 1) Workspace Connection Registry

Add a local config artifact (YAML/JSON) as source of truth for local mapping:

- `workspace_key`
- `databricks_conn_id`
- `databricks_host`
- `databricks_profile` (e.g., `DEFAULT`, `CSPN_DEV`, etc.)
- optional `auth_mode` (`oauth` default, `pat` fallback)

This decouples DAG ownership from auth wiring and allows many workspace connections in one Airflow environment.

### 2) OAuth Sync Control Plane (Local Airflow)

Create an internal sync workflow in Airflow that:

1. Reads registry entries.
2. Resolves OAuth session/token for each `profile + host`.
3. Compares token fingerprint/expiry with stored connection state.
4. Upserts Airflow connection credentials only when needed.
5. Emits explicit status (`healthy`, `expired`, `misconfigured`, `unreachable`) per connection.

### 3) Runtime Consumption Path

No changes required for user DAG logic beyond selecting proper `databricks_conn_id`.

All Databricks operators/hooks continue using standard Airflow connection lookup.

## Data Flow

1. Developer authenticates with existing OAuth setup flow.
2. Astro starts with all mapped Databricks connections available.
3. Sync workflow updates stale/expiring connection tokens.
4. User DAGs execute with current credentials via `databricks_conn_id`.
5. On expiry/misconfiguration, sync emits actionable remediation messages.

## Error Handling

- No silent failures.
- Per-connection status and remediation command are surfaced.
- Expired sessions fail fast with targeted instructions for the exact profile/connection.
- Partial failures do not mask other workspace results.

## Testing Strategy

1. **Unit tests**
   - registry parsing and validation
   - token-change/near-expiry decision logic
   - per-connection update behavior
2. **Integration tests (local)**
   - sync updates both `databricks_default` and custom conn IDs
   - stale token path transitions to healthy after OAuth refresh
   - multi-workspace mapping does not cross-write credentials
3. **Developer checks**
   - `dpc-check` confirms mapped connections have valid OAuth-backed auth state
   - healthcheck DAG validates each mapped Databricks connection can perform a minimal API call

## Alternatives Considered

### A) File watcher sidecar on token-cache.json

Pros: event-driven semantics.  
Cons: lower cross-platform reliability in nested Docker on macOS/Windows.

### B) Hook/operator patching for on-demand token resolution

Pros: freshest possible token at call-time.  
Cons: higher maintenance/risk; touches provider behavior.

### C) PAT-only local auth

Pros: simple static mental model.  
Cons: manual PAT creation/rotation, weaker developer UX and security posture than OAuth-first.

## Recommended Path

Implement the Airflow sync control plane with workspace registry and OAuth default, plus explicit PAT fallback per connection.

## Sources

- Confluence: `Data & Integration Architecture` space (`IntegrationArchitecture`), page `55222503`.
- Confluence: `Caspian` space (`CSPN`), pages reviewed for orchestration and environment patterns, including `115540210` and `332990128`.
- Repository evidence:
  - `.airflow/airflow_settings.yaml.example`
  - `data_products/**/airflow/*.dag.yml`
  - `data_products/.blueprints/*.py`
  - `iac/main.tf`, `iac/airflow_connections.tf`, related deployment-centric IaC files
