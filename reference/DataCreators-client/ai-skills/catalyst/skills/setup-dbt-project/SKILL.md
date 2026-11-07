---
name: setup-dbt-project
description: |
  Scaffold a new dbt project for Databricks: dbt_project.yml (with UC catalog
  vars, Volume target-path, and the full Delta table properties block),
  profiles.yml, .sqlfluff, .pre-commit-config.yaml, .dbtignore, and
  packages.yml. Reads catalog placement and pattern bindings from
  .catalyst-build.yml written by /build-preflight. Use when starting a new
  dbt project or adding dbt to an existing data product.
  Trigger phrases: "scaffold dbt project", "create dbt_project.yml",
  "set up new dbt project for Databricks", "initialize dbt for this product".
allowed-tools: Read Bash Write Edit
metadata:
  tier: workflow
  lifecycle-phase: phase-4-build
  dependencies:
    - build-preflight
    - databricks-config
    - databricks-unity-catalog
    - dbt-best-practices
  consumes:
    - data-contract
    - data-model
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    # Canonical (RFD 0013 enumerated)
    - SQL-DBSQL-001         # OAuth-only profiles.yml
    - SQL-DBSQL-002         # +materialized default per layer
    - SQL-DBSQL-003         # Incrementals use merge strategy
    - SQL-DBSQL-005         # External tables only
    - SQL-DBSQL-006         # Test coverage on PKs (not_null + unique)
    - SQL-DBSQL-007         # Catalog/schema set per environment
    - SQL-DBSQL-008         # No PATs in profiles.yml (cross-ref DBX-SEC-002)
    - SQL-DBSQL-009         # VACUUM retention >= 168 hours (PR 94 sets 35 days, stricter)
    # Canonical (RFD 0012 cross-ref)
    - DBX-SEC-002           # SP owns production objects (identity, not auth type)
    # Cross-ref pending RFD 0008 enumeration
    - DBX-UC-001            # app_catalog/domain_catalog vars per env
    - DBX-UC-002            # UC Volume target-path
    - DBX-UC-004            # App vs Domain catalog separation (Build vs Publish)
    - DBX-UC-005            # SAP schema naming
    - DBX-UC-006            # DAP/CAP schema naming
    - DBX-UC-007            # Sandbox schema naming
    - SQL-NAMING-001        # lowercase identifiers; schema naming
    # Proposed (PR 94 prose → IDs, awaiting RFD 0008)
    - DBX-DELTA-001         # Delta file format default
    - DBX-DELTA-010         # UniForm Iceberg compat (proposed)
    - DBX-DELTA-011         # Column mapping mode = 'name' (proposed)
    - DBX-DELTA-012         # Deletion vectors enabled (proposed)
    - DBX-DELTA-013         # autoOptimize.optimizeWrite (proposed)
    - DBX-DELTA-014         # tuneFileSizesForRewrites (proposed)
    - DBX-DELTA-015         # log + deletedFile retention must match (proposed)
    - DBX-SEC-003           # cgrepo Nexus mirror routing (proposed)
---

# Setup dbt Project

Scaffold a complete, production-ready dbt project structure for Databricks
Unity Catalog. This skill reads context from `.catalyst-build.yml` (written
by `/build-preflight`) and the Design-phase artifacts (`data-contract.md`,
`data-model.md`) to produce seven files, then prints a setup checklist.

## Prerequisites

Before running this skill, `/build-preflight` should have been run and
`.catalyst-build.yml` should contain:
- `mode` (prototype / production / lift-and-shift)
- `product_type` (SAP / DAP / CAP / Sandbox)
- `target_catalog.app_catalog`
- `target_catalog.domain_catalog`
- `target_catalog.caspian_catalog`
- `patterns` (macro bindings)

If `.catalyst-build.yml` is absent, ask the user for:
1. Build mode
2. Product type + business group
3. App catalog name (format: `<team>-app-<env>`)
4. SQL warehouse HTTP path (from Databricks workspace → SQL Warehouses →
   Connection Details)

---

## What This Skill Produces

| File | Purpose |
|---|---|
| `dbt_project.yml` | Project definition with UC catalog vars, Volume target-path, default tblproperties |
| `profiles.yml` | Databricks serverless SQL warehouse connection profile for each env |
| `.sqlfluff` | RFD 0008 SQL linting rules + Jinja templating config |
| `.pre-commit-config.yaml` | sqlfluff linting + secret scan hooks |
| `.dbtignore` | Prevents dbt from scanning `.dplc/`, `.databricks/`, `.catalyst-build.yml` |
| `packages.yml` | dbt package dependencies (no dbt-project-evaluator runtime entry) |
| `schema.yml stub` | Minimal `models/sources.yml` with source declaration |

---

## Step 1 — Read Context

Read `.catalyst-build.yml` (if present) and any DPLC artifacts in `.dplc/`:

```bash
cat .catalyst-build.yml 2>/dev/null
cat .dplc/data-contract.md 2>/dev/null
cat .dplc/data-model.md 2>/dev/null
```

From `data-contract.md` extract (if present):
- `product_name` — used as the dbt project name (`name:` field)
- `data_domain` — used for schema naming
- Source systems listed in the contract

From `data-model.md` extract (if present):
- Layer (ingestion / integration / publish) — determines schema name prefix
- Source system names — used in `raw_<source>` schema names for SAP

From `.catalyst-build.yml`:
- `mode`, `product_type`, `business_group`, `target_catalog.*`, `patterns`

If no DPLC artifacts are available, gather the minimum from the user:
- Product name (kebab-case, e.g., `employee-investment-allocation`)
- Source system abbreviation (e.g., `sap_hcm`, `advent_geneva`)
- Primary layer this project builds (ingestion / integration / publish)

---

## Step 2 — Emit `dbt_project.yml`

Write `dbt_project.yml` in the project root. Apply the schema-naming
convention from `skills/dbt-best-practices/references/catalog-architecture.md`
based on product type:

| Product type | Schema naming |
|---|---|
| SAP | `raw_<source>` (ingestion) + `stnd_<source>` (integration) |
| DAP / CAP | `<product_name>` (product-named, one schema per layer) |
| Sandbox | `<project_name>_proto` |

```yaml
# dbt_project.yml
# Generated by /setup-dbt-project (Catalyst Phase 4 — Build)
# Catalog architecture: skills/dbt-best-practices/references/catalog-architecture.md
# Delta table standards: skills/dbt-best-practices/references/delta-table-standards.md

name: '<product_name>'                        # kebab-case; matches data contract
version: '1.0.0'
config-version: 2

# dbt-databricks adapter settings
require-dbt-version: ">=1.8.0"

# Profile to use for this project (see profiles.yml)
profile: '<product_name>'

# Directory layout — Catalyst data-product layout.
# Models live under datasets/<dataset>/dbt/ subtrees; cross-dataset assets
# (seeds, tests, macros, snapshots, analyses) live under shared/. Product-local
# macros live in macros/; cross-dataset macros live in shared/macros/.
model-paths:    ["datasets"]
seed-paths:     ["shared/seeds"]
test-paths:     ["shared/tests"]
macro-paths:    ["macros", "shared/macros"]
snapshot-paths: ["shared/snapshots"]
analysis-paths: ["shared/analyses"]

# Target path is mode-aware (reads .catalyst-build.yml#mode):
#   - prototype mode: "target" (local dir, dbt default) — no UC Volume needed
#                     against a developer sandbox; logs are ephemeral per run.
#   - production mode (per DBX-UC-002): a UC Volume path of the shape
#       "/Volumes/{{ var('app_catalog') }}/{{ var('target_schema') }}/dbt_artifacts"
#     Volumes persist across warehouse restarts; the Volume MUST exist before
#     `dbt run` (the skill does not provision it).
target-path: "target"   # prototype-mode default; switch to the Volume path in production mode

# dbt packages are installed to a local path (not the Volume) because
# package code must be on the same Python path as dbt.
packages-install-path: "dbt_packages"

# Dispatch order: project macros override dbt_databricks, then dbt-utils.
dispatch:
  - macro_namespace: dbt
    search_order: ['<product_name>', 'dbt_databricks', 'dbt']
  - macro_namespace: dbt_utils
    search_order: ['<product_name>', 'dbt_utils']

# ─────────────────────────────────────────────────────────────────────────────
# Catalog variables
#
# Phase 4 Build writes to `app_catalog`.
# Phase 6 Publish deep-clones to `domain_catalog` (out of scope here).
# `caspian_catalog` is the legacy prototype catalog; retained for reference
# during lift-and-shift migrations.
#
# Set per environment in profiles.yml using `vars:` or by passing --vars on
# the CLI:  dbt run --vars '{"app_catalog": "investments-app-prd"}'
# ─────────────────────────────────────────────────────────────────────────────
vars:
  app_catalog: "<team>-app-dev"             # override per env (dev/qa/sqa/prd)
  domain_catalog: "<bg>-domain-dev"         # Phase 6 publish target only
  caspian_catalog: "caspian-dev"            # legacy reference / lift-and-shift
  target_schema: "<product_name>"           # schema inside app_catalog
  dbt_date: "dbt_date"                      # macro package alias

# ─────────────────────────────────────────────────────────────────────────────
# Model defaults
#
# All models default to incremental + delta + the Catalyst tblproperties block
# (UniForm, deletion vectors, 35-day retention, column mapping).
# Per-layer overrides are set below.
#
# Sources:   delta-table-standards.md → default tblproperties block
#            catalog-architecture.md  → schema naming
#            rule-severity-by-mode.md → mode-aware enforcement
# ─────────────────────────────────────────────────────────────────────────────
models:
  <product_name>:
    +materialized: incremental
    +file_format: delta
    +incremental_strategy: merge
    # Default tblproperties for all Catalyst Delta tables.
    # Rule-ID citations: DBX-DELTA-* family (proposed; awaiting RFD 0008 enumeration).
    # SQL-DBSQL-009 (VACUUM RETAIN >= 168hr) is satisfied by deletedFileRetentionDuration below.
    +tblproperties:
      delta.universalFormat.enabledFormats: 'iceberg'         # DBX-DELTA-010 (proposed) — UniForm for Iceberg readers
      delta.enableIcebergCompatV2: 'true'                     # DBX-DELTA-010 (proposed)
      delta.columnMapping.mode: 'name'                        # DBX-DELTA-011 (proposed) — schema evolution: rename/drop/widen
      delta.enableDeletionVectors: 'true'                     # DBX-DELTA-012 (proposed) — ~10x faster DELETE/UPDATE/MERGE
      delta.autoOptimize.optimizeWrite: 'true'                # DBX-DELTA-013 (proposed) — small-file management on write
      delta.tuneFileSizesForRewrites: 'true'                  # DBX-DELTA-014 (proposed) — MERGE-friendly file sizing
      delta.logRetentionDuration: 'interval 35 days'          # CG backup standard: 35 days (stricter than SQL-DBSQL-009's 168hr minimum)
      delta.deletedFileRetentionDuration: 'interval 35 days'  # DBX-DELTA-015 (proposed) — MUST match logRetention (footgun: mismatched values break time-travel silently)
      # delta.enableChangeDataFeed: 'true'                    # uncomment when downstream CDC
    # ─────────────────────────────────────────────────────────────────────
    # Per-layer schema overrides — MODE-AWARE (reads .catalyst-build.yml#mode).
    #
    # Prototype mode: OMIT the per-layer +schema: overrides. The developer
    # has a single sandbox schema; catalog + schema come from profiles.yml
    # via env vars. Auto-creating raw_*/stnd_* schemas is not guaranteed
    # against sandbox catalogs (CREATE SCHEMA may be restricted for non-admin
    # users), so a single schema avoids first-run failures.
    #
    # Production mode: emit per-layer overrides per product_type
    # (SAP/DAP/CAP/Sandbox conventions — see "Schema naming by product type"
    # below and skills/dbt-best-practices/references/catalog-architecture.md).
    # Production block (uncomment + adapt per product_type):
    #
    # staging:
    #   +schema: "raw_{{ var('target_schema') }}"
    #   +materialized: view                               # staging is cheap — views only
    #   +tblproperties: {}                                # no tblproperties needed for views
    # intermediate:
    #   +schema: "stnd_{{ var('target_schema') }}"
    #   +materialized: view
    # marts:
    #   +schema: "{{ var('target_schema') }}"
    #   +materialized: incremental
    # ─────────────────────────────────────────────────────────────────────
# Seeds (omit per-layer +schema in prototype mode; emit "stnd_<schema>" in production)
# seeds:
#   <product_name>:
#     +schema: "stnd_{{ var('target_schema') }}"
#     +file_format: delta
```

### Schema naming by product type

After generating the template, customize the per-layer `+schema:` values:

**SAP (Source Aligned Product):**
```yaml
staging:
  +schema: "raw_<source_system>"    # e.g., raw_sap_hcm
intermediate:
  +schema: "stnd_<source_system>"   # e.g., stnd_sap_hcm
marts:
  +schema: "stnd_<source_system>"   # or a curated schema name
```

**DAP / CAP (Domain or Consumer Aligned Product):**
```yaml
staging:
  +schema: "<product_name>_staging"
intermediate:
  +schema: "<product_name>"
marts:
  +schema: "<product_name>"
```

**Sandbox / Prototype:**
```yaml
staging:
  +schema: "<project_name>_proto"
intermediate:
  +schema: "<project_name>_proto"
marts:
  +schema: "<project_name>_proto"
```

---

## Step 3 — Emit `profiles.yml`

Write `profiles.yml` outside the project at `~/.dbt/profiles.yml` (preferred — keeps
secrets out of the repo). If the team requires an in-repo template, write
`profiles.yml.example` with placeholder env_var references instead — never commit
a real `profiles.yml` to the repo.

The profile is **mode-aware** (reads `.catalyst-build.yml#mode`):

- **Prototype mode** — default target is `dev` (OAuth U2M, browser flow). Uses
  the developer's cached `databricks auth login` token from `~/.databrickscfg`.
  No service-principal credentials required.
- **Production mode** — default target is `prod` (OAuth M2M, service-principal
  client credentials). SP-owned objects, rotating tokens.

Both shapes coexist in the same `profiles.yml`; only the default `target:`
changes by mode.

### Identity and auth method (two separate concerns)

`DBX-SEC-002` is about **identity**, not token type. The identity that runs
`dbt run` becomes the owner of every table, view, and schema it creates —
and "user-owned production objects" is the failure mode (orphaned tables
when the developer leaves, owner-scoped DROP/ALTER permissions, mixed
audit trails). Whether that identity authenticates via OAuth or PAT is a
**separate** axis — that one is about credential rotation and revocation,
not ownership.

**Identity rules:**

- **Production dbt must execute as a service principal.** SP owns the
  resulting objects; the SP outlives any individual developer.
- **Iteration dbt executes as the developer**, against whatever scope
  their grants allow. The developer owns what they create; that's fine
  because (a) it's bounded by their grants and (b) promotion to
  production re-owns the objects to the SP via the deep-clone-to-domain
  step.
- "Prototype mode" in this skill means "iterating as the developer." It
  may target a dedicated sandbox catalog, *or* a production-shaped
  catalog where the developer happens to have narrow dev-level grants —
  the skill doesn't enforce a catalog name pattern. The constraint is
  "what your grants let you create," not "the catalog matches a
  prefix." Don't point a U2M target at a catalog where you have
  CREATE-on-prod grants you don't intend to exercise.

**Auth method (preference, not gate):**

1. **OAuth M2M** (SP client credentials) — production default outside the
   Databricks job. Rotating, scoped, full SP audit trail.
2. **OAuth U2M** (developer browser flow) — local-iteration default.
   Cached by `databricks auth login`; no `client_id`/`client_secret`
   needed. First `dbt debug` opens a browser; later calls reuse the
   cache.
3. **SP-PAT** — static SP-issued token. Same ownership semantics as
   M2M; fall back to this while M2M is being provisioned.
4. **User-PAT** — static developer-issued token. Same ownership
   semantics as U2M (user owns what they create); the downsides are
   the usual PAT downsides — long-lived, no rotation, manual revocation
   if leaked. Discouraged but not categorically forbidden; if you use
   one, it's bound by the same identity rules as U2M.

**What we don't do:** run production dbt under any user identity —
whether authenticated via U2M, user-PAT, or anything else. The
ownership problem is "user as creator," not "token shape."

Inside a Databricks job, none of this profiles.yml machinery applies —
the wrapper hydrates the SP's identity from the job's ambient context
(see `/write-dbt-wrapper`).

**Watch:** Databricks released *Service-principal OAuth U2M* in beta
(2026-05-20). Once GA, the U2M flow can mint a token as an SP's
identity (requires the developer to hold the Service Principal Manager
role on that SP), collapsing the local "iterate as me" vs "deploy as
SP" split into a single browser-flow path. When it lands, this skill
should grow a fourth `auth_type: oauth` shape — U2M-as-SP — alongside
the M2M client-credentials and U2M-as-user shapes documented above.
Re-test the emitted profile against the GA release before adopting.

### Template

```yaml
# profiles.yml — Generated by /setup-dbt-project (Catalyst Phase 4 — Build)
#
# Per SQL-DBSQL-001 + DBX-SEC-002: OAuth M2M (service principal) is the standard auth.
# Per DBX-UC-001: catalog is set per environment; never hardcode prd catalog in dev.
# Per SQL-DBSQL-007: host + http_path resolved per environment via env vars (CI
#                    populates from secrets store per pipeline; local dev uses
#                    direnv / 1Password CLI to load the SP's credentials).

<product_name>:
  # target: is mode-aware. Skill picks the default from .catalyst-build.yml#mode:
  #   prototype  -> target: dev     (OAuth U2M, browser flow — sandbox only)
  #   production -> target: prod    (OAuth M2M, service-principal credentials)
  target: dev
  outputs:

    # ─────────────────────────────────────────────────────────────────────
    # Prototype-mode default — OAuth U2M (browser flow).
    # Uses the developer's existing `databricks auth login` session; the
    # cached token in ~/.databrickscfg is picked up automatically when
    # auth_type: oauth is set WITHOUT client_id / client_secret.
    # First `dbt debug` opens a browser; subsequent calls reuse the cache.
    # The catalog/schema vars resolve to whatever scope the developer's
    # grants allow — sandbox catalog OR a production-shaped catalog where
    # they have narrow dev-level grants. The constraint is the grants,
    # not the catalog name (see Step 3 prose; DBX-SEC-002 governs identity,
    # not auth type).
    # ─────────────────────────────────────────────────────────────────────
    dev:
      type: databricks
      host: "{{ env_var('DBX_HOST_DEV') }}"                   # SQL-DBSQL-007
      http_path: "{{ env_var('DBX_HTTP_PATH_DEV') }}"         # SQL-DBSQL-007 — SQL warehouse, not interactive cluster
      auth_type: oauth                                         # SQL-DBSQL-001 — U2M: no client_id / client_secret
      catalog: "{{ var('app_catalog', '<team>-app-dev') }}"   # DBX-UC-001 — sandbox catalog only
      schema: "{{ var('target_schema', '<product_name>') }}"
      threads: 4

    # ─────────────────────────────────────────────────────────────────────
    # Production targets — OAuth M2M (service-principal client credentials).
    # `prod` is the production-mode default (selected when
    # .catalyst-build.yml#mode == production). qa / sqa / prd are
    # promotion-stage siblings. All require DBX_CLIENT_ID + DBX_CLIENT_SECRET
    # provisioned per environment; emit these only when the M2M env vars
    # are configured.
    # ─────────────────────────────────────────────────────────────────────
    prod:
      type: databricks
      host: "{{ env_var('DBX_HOST_PRD') }}"
      http_path: "{{ env_var('DBX_HTTP_PATH_PRD') }}"
      auth_type: oauth                                         # SQL-DBSQL-001 + DBX-SEC-002 (M2M)
      client_id: "{{ env_var('DBX_CLIENT_ID') }}"              # service principal client_id
      client_secret: "{{ env_var('DBX_CLIENT_SECRET') }}"      # service principal client_secret (rotated automatically)
      catalog: "{{ var('app_catalog', '<team>-app-prd') }}"
      schema: "{{ var('target_schema', '<product_name>') }}"
      threads: 8

    qa:
      type: databricks
      host: "{{ env_var('DBX_HOST_QA') }}"
      http_path: "{{ env_var('DBX_HTTP_PATH_QA') }}"
      auth_type: oauth
      client_id: "{{ env_var('DBX_CLIENT_ID') }}"
      client_secret: "{{ env_var('DBX_CLIENT_SECRET') }}"
      catalog: "{{ var('app_catalog', '<team>-app-qa') }}"
      schema: "{{ var('target_schema', '<product_name>') }}"
      threads: 4

    sqa:
      type: databricks
      host: "{{ env_var('DBX_HOST_SQA') }}"
      http_path: "{{ env_var('DBX_HTTP_PATH_SQA') }}"
      auth_type: oauth
      client_id: "{{ env_var('DBX_CLIENT_ID') }}"
      client_secret: "{{ env_var('DBX_CLIENT_SECRET') }}"
      catalog: "{{ var('app_catalog', '<team>-app-sqa') }}"
      schema: "{{ var('target_schema', '<product_name>') }}"
      threads: 4

    prd:
      type: databricks
      host: "{{ env_var('DBX_HOST_PRD') }}"
      http_path: "{{ env_var('DBX_HTTP_PATH_PRD') }}"
      auth_type: oauth
      client_id: "{{ env_var('DBX_CLIENT_ID') }}"
      client_secret: "{{ env_var('DBX_CLIENT_SECRET') }}"
      catalog: "{{ var('app_catalog', '<team>-app-prd') }}"
      schema: "{{ var('target_schema', '<product_name>') }}"
      threads: 8

# ─────────────────────────────────────────────────────────────────────────────
# Fallback: PAT issued to the service principal (acceptable while OAuth is
# being provisioned). Uncomment ONLY if OAuth client credentials aren't yet
# available for your SP. The PAT MUST belong to the service principal — never
# to a developer's user account.
#
# How to tell if the PAT is SP-issued vs user-issued:
#   $ databricks current-user me --token "$DATABRICKS_TOKEN"
#   If "userName" matches a service principal name (no @ sign, ends in
#   "-sp" or similar org convention), it's an SP-PAT — acceptable.
#   If "userName" is your email address, it's a USER-PAT — DO NOT USE.
#
# Migrate to OAuth as soon as the SP's client_id/client_secret are available.
# ─────────────────────────────────────────────────────────────────────────────
#
# <product_name>:
#   target: dev
#   outputs:
#     dev:
#       type: databricks
#       host: "{{ env_var('DBX_HOST_DEV') }}"
#       http_path: "{{ env_var('DBX_HTTP_PATH_DEV') }}"
#       token: "{{ env_var('DBX_SP_TOKEN') }}"    # SP-issued PAT — keeps the SP as the executing identity
#       catalog: "{{ var('app_catalog', '<team>-app-dev') }}"
#       schema: "{{ var('target_schema', '<product_name>') }}"
#       threads: 4
```

### Environment variable inventory

CI sets these per pipeline (env-scoped secrets); local dev uses `direnv` or `op run`
pointed at 1Password / Vault.

| Variable | Where set | Notes |
|---|---|---|
| `DBX_HOST_<ENV>` | CI per-env secret | workspace hostname, no scheme (e.g., `dbc-abc123.cloud.databricks.com`) |
| `DBX_HTTP_PATH_<ENV>` | CI per-env secret | SQL warehouse HTTP path (`/sql/1.0/warehouses/<id>`) |
| `DBX_CLIENT_ID` | CI org-scoped secret | service principal client_id (one SP per env or one SP across envs depending on RBAC setup) |
| `DBX_CLIENT_SECRET` | CI org-scoped secret | SP client_secret — rotate per security policy |
| `DBX_SP_TOKEN` | CI per-env secret (fallback only) | SP-PAT for fallback profile — drop once OAuth lands |

The repo's `.gitignore` MUST include `profiles.yml` (covered by `.dbtignore` Step 6
below). Committing a `profiles.yml` with literal secrets is a hard fail in pre-commit
and CI per DBX-SEC-002.

Fill `DBX_HOST_<ENV>` and `DBX_HTTP_PATH_<ENV>` for the user from
`.catalyst-build.yml#databricks_readiness` if available, or prompt:

> "What is the Databricks workspace hostname for each environment?
>  (Find it in Databricks workspace → Compute → SQL Warehouses →
>   Connection Details → Server hostname)"

---

## Step 4 — Emit `.sqlfluff`

Write `.sqlfluff` in the project root. Rules are sourced from RFD 0008
SQL coding standards categories. [RFD 0008 — SQL & Databricks coding standards (forthcoming — see `docs/superpowers/specs/2026-05-14-dplc-build-skills-design.md` for the canonical rule list)]

```ini
# .sqlfluff
# Generated by /setup-dbt-project (Catalyst Phase 4 — Build)
# Rule set: RFD 0008 SQL coding standards (Capital Group)
# Reference: docs/superpowers/specs/2026-05-14-dplc-build-skills-design.md (RFD 0008 forthcoming)

[sqlfluff]
templater = jinja
dialect = sparksql
sql_file_exts = .sql
exclude_rules = L016,L034

[sqlfluff:templater:jinja]
apply_dbt_builtins = True

[sqlfluff:rules]
# SQL-NAMING-001: consistent identifier casing
capitalisation_policy = lower
extended_capitalisation_policy = lower

# SQL-FMT: indentation and formatting
indent_unit = space
tab_space_size = 4

# SQL-DBSQL-006: primary-key tests (not_null + unique) required on declared PKs
# Enforced by dbt test suite; not a sqlfluff lint rule.

[sqlfluff:rules:L010]
capitalisation_policy = lower

[sqlfluff:rules:L014]
# SQL-NAMING-001: unquoted identifiers are lowercase
capitalisation_policy = lower

[sqlfluff:rules:L030]
# SQL-NAMING-001: function names are lowercase
capitalisation_policy = lower

[sqlfluff:rules:L040]
# SQL-NAMING-001: NULL / boolean keywords are lowercase
capitalisation_policy = lower

[sqlfluff:templater:jinja:macros]
# Prevents sqlfluff from failing on dbt-specific macros
ref = '<str>'
source = '<str>'
config = '<dict>'
var = '<str>'
```

---

## Step 5 — Emit `.pre-commit-config.yaml`

Write `.pre-commit-config.yaml` in the project root.

```yaml
# .pre-commit-config.yaml
# Generated by /setup-dbt-project (Catalyst Phase 4 — Build)
# Hooks: SQL linting (sqlfluff) + secret scanning (detect-secrets)

repos:
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: 3.1.0
    hooks:
      - id: sqlfluff-lint
        name: sqlfluff-lint (RFD 0008 SQL standards)
        additional_dependencies:
          - dbt-databricks>=1.8.0
          - sqlfluff-templater-dbt>=3.1.0
        args: [--dialect, sparksql]

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        name: detect-secrets (prevent credential leaks)
        args:
          - --baseline
          - .secrets.baseline
        exclude: >
          (?x)^(
            \.dplc/.*|
            \.catalyst-build\.yml|
            tests/fixtures/.*
          )$
```

> **Note on package sources:** If your environment is air-gapped from GitHub,
> replace the `repo:` URLs with your organisation's internal mirror of these
> pre-commit hook repositories, or host the hooks in an internal registry.
> The sqlfluff and detect-secrets packages themselves are installed by pre-commit
> from the `additional_dependencies` field — ensure they are available in the
> internal PyPI mirror at
> `https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/`.

---

## Step 6 — Emit `.dbtignore`

Write `.dbtignore` in the project root. This prevents dbt from scanning
directories that hold Catalyst metadata or Databricks workspace files.

```gitignore
# .dbtignore
# Generated by /setup-dbt-project (Catalyst Phase 4 — Build)

# DPLC artifacts — not dbt models
.dplc/

# Databricks workspace metadata
.databricks/

# Catalyst build cache
.catalyst-build.yml

# Python virtual environments
.venv/
venv/
__pycache__/
*.pyc

# IDE and OS files
.DS_Store
.idea/
.vscode/
*.swp

# dbt artifacts (generated; not source)
target/
dbt_packages/
logs/
```

---

## Step 7 — Emit `packages.yml`

Write `packages.yml` in the project root.

> **Important:** `dbt-project-evaluator` is **NOT** added as a runtime
> dependency. Catalyst's `/dbt-best-practices` skill covers dbt-project-evaluator
> categorical rules at generation time. Running `dbt-project-evaluator` as a
> runtime package adds CI overhead and often fails on incomplete projects mid-build.
> Remove the entry if it is already present in the project.

```yaml
# packages.yml
# Generated by /setup-dbt-project (Catalyst Phase 4 — Build)
#
# IMPORTANT: dbt-project-evaluator is NOT included.
# Catalyst enforces its rules at generation time via /dbt-best-practices.
# See: skills/dbt-best-practices/SKILL.md for the rule source mapping.

packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.3.0", "<2.0.0"]

  - package: dbt-labs/dbt_date
    version: [">=0.10.0", "<1.0.0"]

  # Uncomment if your product uses dbt Mesh cross-project references:
  # - package: dbt-labs/dbt_meshify
  #   version: [">=0.9.0", "<1.0.0"]
```

After writing `packages.yml`, remind the user that `dbt deps` must be run
before model development:

```
dbt deps --project-dir . --profiles-dir .
```

In a Databricks Asset Bundle or CI context, this is handled by the
`dbt_wrapper.py` dispatcher (see `/write-dbt-wrapper`).

---

## Step 8 — Emit `models/sources.yml` Stub

Create a minimal source declaration stub to prevent dbt graph errors when
models reference `{{ source(...) }}`. Use source system names from
`data-contract.md` if available.

```yaml
# models/sources.yml
# Generated by /setup-dbt-project (Catalyst Phase 4 — Build)
# Populate with actual source table names once ingestion is confirmed.

version: 2

sources:
  - name: <source_system>            # e.g., sap_hcm; matches raw_<source> schema
    database: "{{ var('app_catalog') }}"
    schema: "raw_<source_system>"
    description: >
      Raw ingestion layer for <source_system>. Populated by the source-aligned
      pipeline. Do not write to this schema from domain/consumer models.
    tables:
      - name: <first_table>          # replace with actual table names from data-model.md
        description: "TODO: add description"
```

---

## Setup Checklist

After writing all files, print a setup checklist for the user:

```
/setup-dbt-project — Setup Checklist
═══════════════════════════════════════════════════════════════
Files written:
  ✓  dbt_project.yml         — project definition + catalog vars + tblproperties
  ✓  profiles.yml            — U2M dev (prototype) + M2M prod/qa/sqa/prd (production)
  ✓  .sqlfluff               — RFD 0008 SQL linting rules
  ✓  .pre-commit-config.yaml — sqlfluff + detect-secrets hooks
  ✓  .dbtignore              — excludes .dplc/, .databricks/, .catalyst-build.yml
  ✓  packages.yml            — dbt_utils + dbt_date (no dbt-project-evaluator)
  ✓  models/sources.yml      — source declaration stub

Next steps:
  1. Provision the service principal in each environment (dev/qa/sqa/prd)
     and grant USE CATALOG / USE SCHEMA permissions on the app_catalog.
  2. Set DBX_HOST_<ENV> and DBX_HTTP_PATH_<ENV> per environment (CI secrets
     or local direnv / 1Password CLI).
  3. For production mode: set DBX_CLIENT_ID + DBX_CLIENT_SECRET for the
     service principal (OAuth M2M). DO NOT use a personal access token —
     see DBX-SEC-002.
     For prototype mode: run `databricks auth login` once; the OAuth U2M
     token is cached in ~/.databrickscfg and used automatically by the
     `dev` target. No SP credentials required.
  4. Run: dbt deps --project-dir . --profiles-dir ~/.dbt
  5. Verify: dbt debug --target dev   (prototype: U2M browser flow)
        or:  dbt debug --target prod  (production: SP M2M)
  6. Author models with: /source-aligned, /domain-aligned, or /consumer-aligned
  7. Run /write-dbt-wrapper to generate the Databricks task dispatcher
  8. Run /setup-databricks-asset-bundle to scaffold the pipeline bundle

Standards applied (canonical IDs from RFD 0011/0012/0013):
  SQL-DBSQL-001  — OAuth-only profiles.yml (no PATs in primary path)
  SQL-DBSQL-002  — +materialized default per layer in dbt_project.yml
  SQL-DBSQL-003  — Incremental strategy = merge
  SQL-DBSQL-005  — External tables only
  SQL-DBSQL-006  — Test coverage on PKs (not_null + unique)
  SQL-DBSQL-007  — Catalog/schema set per environment, never hardcoded
  SQL-DBSQL-008  — OAuth preferred over PAT for credential rotation (independent of DBX-SEC-002)
  SQL-DBSQL-009  — VACUUM RETAIN >= 168 hours (Catalyst sets 35 days)
  DBX-SEC-002    — SP is the executing identity for production; user identity OK for iteration within their grants

Standards applied (cross-ref pending RFD 0008 enumeration):
  DBX-UC-001     — app_catalog / domain_catalog vars per environment
  DBX-UC-002     — Volume target-path for dbt artifacts
  DBX-UC-004     — App vs Domain catalog separation (Build vs Publish)
  DBX-UC-005/006/007 — Schema naming per product type (SAP / DAP-CAP / Sandbox)
  SQL-NAMING-001 — lowercase identifiers; schema naming convention

Standards applied (proposed — PR 94 prose elevated to IDs, awaiting RFD 0008):
  DBX-DELTA-001/010..015 — Delta tblproperties block (UniForm, column mapping,
                           deletion vectors, autoOptimize, tune file sizes,
                           log+deletedFile retention parity)
  DBX-SEC-003    — cgrepo Nexus mirror routing for all package installs
═══════════════════════════════════════════════════════════════
```

---

## Pattern Bindings (from `.catalyst-build.yml`)

If `.catalyst-build.yml#patterns` contains bound macros, emit guidance:

```
Pattern bindings from /build-preflight:
  source-wrapper    → macros/stg_source_wrapper.sql
    Add to dispatch order in dbt_project.yml (already included above)
  audit-columns     → macros/add_audit_columns.sql
    Add a post-hook in dbt_project.yml:
      models:
        <product_name>:
          +post-hook: "{{ add_audit_columns() }}"
```

For unbound patterns, emit a reminder:

```
Unbound patterns (run /dbt-best-practices for implementation guidance):
  bitemporal-incremental  — needed for slowly-changing datasets
  surrogate-key           — needed if no natural primary key exists
```

---

## References

- Catalog architecture: `skills/dbt-best-practices/references/catalog-architecture.md`
- Delta table standards: `skills/dbt-best-practices/references/delta-table-standards.md`
- Rule severity by mode: `skills/dbt-best-practices/references/rule-severity-by-mode.md`
- dbt-best-practices skill: `skills/dbt-best-practices/SKILL.md`
- `.catalyst-build.yml` schema: `skills/build-preflight/SKILL.md`

## Standards

### Canonical (RFD 0013 enumerated)

| Standard | Where applied |
|---|---|
| **SQL-DBSQL-001** | `profiles.yml` declares `auth_type: oauth` + `client_id`/`client_secret` env vars; no `token:` in primary path |
| **SQL-DBSQL-002** | `dbt_project.yml` declares `+materialized` per layer (view for staging/intermediate, incremental for marts) |
| **SQL-DBSQL-003** | Models default to `+incremental_strategy: merge` |
| **SQL-DBSQL-005** | External tables only — Volume target-path lives at `/Volumes/<catalog>/<schema>/dbt_artifacts` |
| **SQL-DBSQL-006** | Primary-key tests (`not_null` + `unique`) baked into `schema.yml` stubs (enforced by `/write-dbt-test`) |
| **SQL-DBSQL-007** | `host` / `http_path` / `catalog` / `schema` resolved per environment via env vars; never hardcoded |
| **SQL-DBSQL-008** | No PATs in primary `profiles.yml` (cross-ref `DBX-SEC-002`) |
| **SQL-DBSQL-009** | VACUUM retention satisfied by `delta.deletedFileRetentionDuration: 'interval 35 days'` (840hr; stricter than the 168hr minimum) |

### Canonical (RFD 0012 cross-ref)

| Standard | Where applied |
|---|---|
| **DBX-SEC-002** | Identity, not auth type. Production `profiles.yml` targets execute as a service principal (M2M; SP-PAT fallback). Prototype targets execute as the developer (U2M) bounded by their grants. Production dbt never runs under a user identity regardless of token type. |

### Cross-ref pending RFD 0008 enumeration

| Standard | Where applied |
|---|---|
| **DBX-UC-001** | `app_catalog` / `domain_catalog` vars declared per environment |
| **DBX-UC-002** | dbt `target-path` set to `/Volumes/<catalog>/<schema>/dbt_artifacts` |
| **DBX-UC-004** | App catalog for Build; Domain catalog for Publish (DEEP CLONE between) |
| **DBX-UC-005** | SAP schema naming: `raw_<source>` + `stnd_<source>` |
| **DBX-UC-006** | DAP/CAP schema naming: product-named |
| **DBX-UC-007** | Sandbox schema naming: `<project>_proto` |
| **SQL-NAMING-001** | Lowercase identifiers; schema naming per product type |

### Proposed (PR 94 prose → IDs; awaiting RFD 0008 enumeration)

| Standard | Where applied |
|---|---|
| **DBX-DELTA-001** | `+file_format: delta` default for all materialized models |
| **DBX-DELTA-010** | UniForm Iceberg compat in `+tblproperties:` |
| **DBX-DELTA-011** | Column mapping mode = `'name'` |
| **DBX-DELTA-012** | Deletion vectors enabled |
| **DBX-DELTA-013** | autoOptimize.optimizeWrite enabled |
| **DBX-DELTA-014** | tuneFileSizesForRewrites enabled |
| **DBX-DELTA-015** | `delta.logRetentionDuration` MUST equal `delta.deletedFileRetentionDuration` |
| **DBX-SEC-003** | All package installs route through cgrepo Nexus mirror (`.pre-commit-config.yaml` notes the policy) |
