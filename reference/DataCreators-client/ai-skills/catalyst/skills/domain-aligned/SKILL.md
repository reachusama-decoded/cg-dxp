---
name: domain-aligned
description: >-
  AI Catalyst DPLC Domain-Aligned Data Product Generator — Build canonical,
  domain-aligned data products from existing Unity Catalog source tables.
  Two output modes: **Databricks** (sandbox testing) and **EMR**
  (Casper IM/MSS production-ready artifacts with DAG, Deequ, DDL).
  Part of the AI Catalyst DPLC plugin bundle, aligned with RFD2 Phase 4 (Build).
  Orchestrates discovery, bi-temporal model design, profiling gates,
  dbt model generation, and optional Databricks execution.
  Use this skill when the user wants to build a canonical model from
  multiple existing UC tables, create a domain-aligned data product,
  generate dbt models that UNION multiple sources into a single canonical
  table, run a domain-aligned model in Databricks, or produce
  production-ready domain-aligned artifacts. Also trigger when
  the user says "domain-aligned", "canonical model from tables",
  "union sources", "consolidate tables", or "domain-aligned data product".
metadata:
  tier: workflow
  lifecycle-phase: phase-4-build
  dependencies:
    - discover-data
    - data-modeling
    - data-profiling
    - generate-dag
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
---

# AI Catalyst DPLC: Domain-Aligned Data Product Generator

> **RFD2 Phase:** Phase 4 (Build) — Domain-Aligned Pipeline  
> **Claude Code Users:** See *(planned — not yet created)* for equivalent command prompts

> **Integration Note**: This skill is invoked as part of the AI Catalyst DPLC lifecycle. It can also be used standalone.

Build canonical, domain-aligned data products from **existing Unity Catalog source tables**. Unlike [source-aligned](../source-aligned/SKILL.md) (which starts from raw CSV/DAT files), this skill starts from tables that already exist in UC and produces a single canonical model that UNIONs multiple sources.

## Output Modes

This skill supports two output modes:

| Mode | Description | When to Use |
|------|-------------|-------------|
| **Databricks** (default) | Generates dbt models to `workspace/generated/` and runs against Databricks SQL warehouse | Exploring data, validating model design, rapid iteration |
| **EMR** | Generates Casper foundation-ready artifacts directly into an IM or MSS foundation repo | Production deployment, ready to commit and merge into foundation repo |

### Mode Selection

- If the user says "databricks", "sandbox", "explore", or "test in Databricks" --> **Databricks** mode
- If the user says "EMR", "casper", "production", "IM", "MSS", "commit to repo", or "foundation-ready" --> **EMR** mode
- If the user has a foundation repo cloned locally --> suggest **EMR** mode
- If unclear, **ask the user** which mode they want

## Decision Rule

| User Context | Action |
|---|---|
| Has **existing UC tables** and wants a **canonical/domain model** (Databricks testing) | --> Use this skill, **Databricks** mode |
| Has **existing UC tables** and wants **Casper EMR-ready** artifacts | --> Use this skill, **EMR** mode |
| Has a **raw source file** (CSV/DAT) and **no existing project** | --> Use Casper Source-Aligned instead |
| Has an **existing foundation repo** and wants to add a **single-source entity** | --> Use entity-scaffold instead |
| Has an **existing Hourglass project** and is iterating | --> Use Hourglass phases instead |

**Key distinction from entity-scaffold:** This skill handles **multi-source UNION patterns** (multiple UC tables consolidated into one canonical model). entity-scaffold handles **single-source entity creation** from one standard-zone table.

## When to Use

- User wants to build a canonical data model from multiple UC source tables
- User asks to "consolidate", "union", or "standardize" data from several vendors/sources
- User mentions "domain-aligned", "canonical model", or "data product from existing tables"
- User wants to prototype a domain model in Databricks
- User wants to produce Casper foundation-ready domain-aligned artifacts

**Recommended pre-step:** Run the `discover-data` skill first to identify available UC source tables.

---

## Outputs

### Databricks Mode

All artifacts are written to `workspace/generated/domain-aligned/<model_name>/`:

```
workspace/generated/domain-aligned/<model_name>/
├── discovery/
│   └── discovery_report.md          # Source table inventory and domain context
├── model/
│   ├── <model>.yaml                 # Model specification (columns, grain, keys)
│   ├── <model>.mmd                  # Mermaid ER diagram
│   ├── <model>_ddl.sql              # CREATE TABLE DDL
│   ├── <model>_mapping.sql          # Source-to-target mapping SQL
│   └── <model>.md                   # Model documentation
├── profiling/
│   └── <table>.md                   # Per-source profiling reports
├── dbt/
│   ├── dbt_project.yml              # dbt project configuration
│   ├── profiles.yml                 # Databricks connection profile
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_<vendor>_<entity>.sql      # One per source table
│   │   ├── intermediate/
│   │   │   └── int_<model>_union.sql          # UNION ALL of staging models
│   │   ├── canonical/
│   │   │   └── <model>.sql                    # Final canonical model
│   │   └── schema.yml                         # Column docs + tests
│   └── macros/
│       ├── generate_surrogate_key_v3.sql
│       └── get_custom_schema.sql
└── databricks/
    ├── run_results.json             # dbt run output
    └── databricks_report.md         # Summary of Databricks execution
```

### EMR Mode

Artifacts are written directly into the target foundation repo:

#### IM Foundation Layout

```
models/<dc_tag>/<entity_name>_f/
  <entity_name>.yml                           # Model YAML with sources + meta
  staging/
    stage_<source_1>.sql                      # Staging per source (renamed columns)
    stage_<source_2>.sql
    ...
  integration/int_<entity_name>_union.sql     # UNION ALL + dedup + checksum
  prepared/<entity_name>.sql                  # bitemporal_load_v2, surrogate key
database/<entity_name>.sql                    # Hive DDL
dags/<entity_name>_dbt.dag.yml                # Airflow DAG YAML
deequ_rules/<entity_name>_dbt.dq.yml          # Deequ DQ rules
```

#### MSS Foundation Layout

```
models/<dc_tag>/<entity_name>/
  <entity_name>.yml
  staging/
    stage_<source_1>.sql
    stage_<source_2>.sql
    ...
  integration/int_<entity_name>_union.sql
  prepared/<entity_name>.sql
database/dbt_tables/<entity_name>.sql
dags/<dc_tag>/<entity_name>_dbt.dag.yml
deequ_rules/<dc_tag>/<entity_name>_dbt.dq.yml
```

---

## Order of Operations

### Shared Steps (Both Modes)

Steps 1-3 are identical regardless of output mode:

```
1. discover        --> Delegate to discover-data --> discovery_report.md
                       |  Human checkpoint: confirm source tables
                       |
2. model           --> Delegate to data-modeling --> model spec YAML + ER + DDL + mapping
                       |  Human checkpoint: confirm grain, keys, model design
                       |
3. profile         --> Delegate to data-profiling --> updated model spec (HARD GATE)
                       |  Human checkpoint: review profiling findings
```

### Databricks Mode (Steps 4-6)

```
4. generate-dbt    --> INTERNAL MODE --> staging + union + canonical dbt models
                       |
5. validate        --> Score >= 7 to proceed, up to 5 retries
                       |
6. run-databricks  --> INTERNAL MODE --> execute dbt on Databricks SQL warehouse
                       Human checkpoint: review Databricks data
```

### EMR Mode (Steps 4-10)

```
4.  detect-repo         --> Identify IM vs MSS from dbt_project.yml
                            |
5.  analyze-context     --> Scan existing models in same dc_tag folder for conventions
                            |
6.  confirm-inputs      --> HUMAN CHECKPOINT: entity name, PKs, dataset type,
                            source tables, dc_tag, domain, schedule
                            |
7.  generate-staging    --> One staging model per source table (Casper macros)
                            |
8.  generate-integration --> UNION ALL staging + dedup + checksum (Casper conventions)
                            |
9.  generate-prepared   --> bitemporal_load_v2, surrogate key, audit columns
                            |
10. generate-model-yml  --> Sources, meta, tags following foundation patterns
                            |
11. generate-ddl        --> Hive DDL for curated zone
                            |
12. generate-dag        --> Delegate to dag-yaml skill
                            |
13. generate-deequ      --> Delegate to deequ-rules skill
                            |
14. validate-all        --> Cross-check consistency across all artifacts
                            Human checkpoint: review all generated artifacts
```

### Human-in-the-Loop Checkpoints

| After Step | Confirmation Required | Mode |
|------------|----------------------|------|
| 1 (discover) | Confirm which UC source tables to include | Both |
| 2 (model) | Confirm grain, surrogate key columns, column mappings, model design | Both |
| 3 (profile) | Review profiling findings; spec must be updated before proceeding | Both |
| 6 (databricks: run-databricks) | Review Databricks data output | Databricks |
| 6 (emr: confirm-inputs) | Confirm entity name, PKs, target foundation, dc_tag, schedule | EMR |
| 14 (emr: validate-all) | Review all generated artifacts before committing | EMR |

---

## Databricks Mode Execution

### Key Differences from Source-Aligned

| Aspect | Source-Aligned | Domain-Aligned (Databricks) |
|--------|---------------|----------------|
| **Input** | Raw CSV/DAT file | Existing UC tables |
| **Sources** | Single | Multiple (UNION) |
| **Layers** | staging --> integration --> prepared | staging --> intermediate (UNION) --> canonical |
| **Strategy** | `bitemporal_load_v2` | Standard incremental merge |
| **Target schema** | `cspn_work2_` / `cspn_fndn2_` | `cspn_cons2_${env}` |
| **Naming** | `*_v4` suffix | Clean canonical names (no suffix) |

### Step 4: Generate dbt Models (Internal Mode)

This is the core generation step. Generate three layers of dbt models:

#### 4a. Staging Models (one per source table)

For each source table, generate `stg_<vendor>_<entity>.sql`:

```sql
{{ config(materialized='view') }}

SELECT
    -- Map source columns to canonical column names
    <source_col_1>   AS <canonical_col_1>,
    <source_col_2>   AS <canonical_col_2>,
    ...
    '<vendor_name>'  AS dl_source,
    CURRENT_TIMESTAMP() AS dl_system_from_date
FROM {{ source('<source_name>', '<table_name>') }}
```

Key rules:
- One staging model per vendor source table
- Rename columns to match canonical model spec
- Add `dl_source` literal to identify the vendor
- Cast types to match canonical model
- Filter out obviously bad rows if profiling revealed issues

#### 4b. Intermediate Model (UNION ALL)

Generate `int_<model>_union.sql`:

```sql
{{ config(materialized='view') }}

SELECT * FROM {{ ref('stg_<vendor1>_<entity>') }}
UNION ALL
SELECT * FROM {{ ref('stg_<vendor2>_<entity>') }}
UNION ALL
SELECT * FROM {{ ref('stg_<vendor3>_<entity>') }}
```

Key rules:
- UNION ALL of all staging models (NOT UNION -- keep duplicates for now)
- All staging models must have identical column sets (handled in staging layer)
- This is a view -- no materialization needed

#### 4c. Canonical Model

Generate `<model>.sql`:

```sql
{{
  config(
    materialized='incremental',
    unique_key='dl_row_uid',
    incremental_strategy='merge',
    schema=env_var('DATABRICKS_DEFAULT_SCHEMA'),
    file_format='delta',
    meta={
      'surrogate_key_cols': ['<natural_key_col1>', '<natural_key_col2>'],
      'load_type': 'master'
    }
  )
}}

WITH source_data AS (
    SELECT * FROM {{ ref('int_<model>_union') }}
),

with_surrogate_key AS (
    SELECT
        {{ generate_surrogate_key_v3(['<natural_key_col1>', '<natural_key_col2>']) }} AS dl_row_uid,
        *,
        MD5(CONCAT_WS('||', <all_business_cols>)) AS checksum,
        CURRENT_TIMESTAMP() AS dl_business_from_date,
        CAST('9999-12-31' AS TIMESTAMP) AS dl_business_to_date,
        CURRENT_TIMESTAMP() AS dl_system_from_date,
        CAST(NULL AS TIMESTAMP) AS dl_system_to_date,
        TRUE AS is_current
    FROM source_data
)

SELECT * FROM with_surrogate_key

{% if is_incremental() %}
WHERE dl_system_from_date > (SELECT MAX(dl_system_from_date) FROM {{ this }})
{% endif %}
```

Key rules:
- Incremental merge on `dl_row_uid` (surrogate key)
- Schema from `DATABRICKS_DEFAULT_SCHEMA` env var
- Bi-temporal columns added here (not in staging/intermediate)
- Checksum for change detection
- `is_current` flag for SCD Type 2 pattern

#### 4d. Schema YAML

Generate `schema.yml` with:
- Source definitions for all UC tables
- Model documentation for staging, intermediate, and canonical
- Column descriptions from model spec
- Tests: `not_null` and `unique` on `dl_row_uid`, `not_null` on key columns

#### 4e. dbt Project Files

Generate:
- `dbt_project.yml` -- project config with model paths
- `profiles.yml` -- Databricks connection using env vars

**Prompt reference:** `prompts/dbt_canonical_model.md`

**Output:** All dbt files written to `workspace/generated/domain-aligned/<model_name>/dbt/`

### Step 5: Validate

Apply validation criteria from `prompts/validation.md`:
- SQL syntax correctness
- All staging models have consistent column sets
- UNION ALL in intermediate model references all staging models
- Canonical model has surrogate key, bi-temporal columns, incremental config
- Schema YAML has tests on key columns
- No hardcoded catalog/schema references

If `score < 7`, regenerate with feedback (up to 5 retries).

### Step 6: Run Databricks (Internal Mode)

Execute the generated dbt project against Databricks:

**Prerequisites:**
- `.env` has `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_WAREHOUSE_ID`
- `DATABRICKS_DEFAULT_CATALOG` and `DATABRICKS_DEFAULT_SCHEMA` are set

**Execution:**
```bash
python skills/domain-aligned/scripts/run_domain_databricks.py \
  --model-name <model> \
  --dbt-dir workspace/generated/domain-aligned/<model>/dbt
```

The Databricks runner:
1. Copies macro overrides from `skills/domain-aligned/templates/dbt_project/macros/`
2. Runs `dbt deps` (if packages.yml exists)
3. Runs `dbt run --select +<model>`
4. Runs `dbt test --select +<model>`
5. Generates `databricks_report.md` with row counts and sample data

**Checkpoint:** Review Databricks results with the user.

### Validation Loop

After generating dbt models, validation runs automatically:
- If `score >= 7`: Proceed to Databricks execution
- If `score < 7`: Regenerate with feedback (up to 5 retries)
- Validation criteria in `prompts/validation.md`

---

## EMR Mode Execution

### Key Differences: EMR vs Databricks

| Aspect | Databricks Mode | EMR Mode |
|--------|---------------|-----------------|
| **Output location** | `workspace/generated/` | Foundation repo working copy |
| **Staging macro** | `{{ source() }}` | `cspn_source_v2()` (IM) / `cspn_source()` (MSS) |
| **Integration** | UNION ALL as view | UNION ALL + dedup + checksum (view or insert_overwrite) |
| **Canonical/Prepared** | Incremental merge | `bitemporal_load_v2` with `as_of_col` |
| **Schema** | `env_var('DATABRICKS_DEFAULT_SCHEMA')` | `cspn_fndn2_` + `target.name` |
| **Audit columns** | Manual bi-temporal columns | `{{ get_audit_cols() }}` macro |
| **Surrogate key** | Explicit in SELECT | `{{ generate_surrogate_key_v3() }}` reads from meta |
| **DAG YAML** | None | Generated (delegates to dag-yaml) |
| **Deequ rules** | None | Generated (delegates to deequ-rules) |
| **DDL** | None | Hive DDL for curated zone |
| **Project files** | dbt_project.yml + profiles.yml | Not needed (uses foundation repo's config) |

### Step 4: Detect Repository

Read `dbt_project.yml` in the foundation repo root:
- If `name: 'casper_im_foundation'` --> IM mode
- If `name: 'casper_mss_foundation'` --> MSS mode

Also scan for `cspn_source_v2` vs `cspn_source` usage in existing staging files
to confirm macro conventions.

See `prompts/detect_repo.md` for the full detection procedure.

### Step 5: Analyze Context

Read 2-3 existing models in `models/<dc_tag>/` to learn:
- Column naming patterns (camelCase -> snake_case renames)
- Schema prefix conventions (`cspn_work2_`, `cspn_fndn2_`, `cspn_cons2_`)
- Dedup strategies (ROW_NUMBER patterns, partition keys)
- Checksum computation style
- Integration materialization (view vs incremental insert_overwrite)
- Source schema suffix patterns
- **Multi-source patterns** (if any existing domain-aligned models exist, study them)

### Step 6: Confirm Inputs (HUMAN CHECKPOINT)

Present all gathered and inferred values to the user:

```
Entity name:         <entity_name>
Source tables:       <list of UC tables to UNION>
Source schemas:      <schema prefix per source>
Domain:              <domain>
DC tag:              <dc_tag>
Dataset type:        <master|balance>
PK columns:         <pk_columns>
As-of column:        <as_of_col>  (balance only)
Schedule:            <cron or null>
Upstream DAGs:       <list of upstream DAG names or none>
Repo type:           <IM|MSS>
Vendor identifiers:  <list of dl_source values>
```

Wait for user confirmation before proceeding.

### Step 7: Generate Staging Models

Create one staging model per source table. Each staging model reads from its
respective source and renames columns to the canonical snake_case schema.

**Prompt reference:** `prompts/generate_foundation_staging.md`

**Key differences from Databricks mode staging:**
- Uses `cspn_source_v2()` (IM) or `cspn_source()` (MSS) instead of `{{ source() }}`
- Schema built with `var("source_schema_suffix")`
- Adds `'<vendor_name>' AS dl_source_system_code` for provenance
- All columns listed explicitly (no `SELECT *`)
- Column names in original case at this layer (rename happens in integration)

**Output:** One `stage_<source_table>.sql` per source table

### Step 8: Generate Integration Model (UNION + Dedup)

Create the integration model that UNIONs all staging models, deduplicates,
and computes the checksum. This is the **key difference from single-source
entity-scaffold** -- the integration layer consolidates multiple sources.

**Prompt reference:** `prompts/generate_foundation_integration.md`

**Pattern:**

```sql
{{
    config(
        schema = "cspn_work2_"|string + target.name,
        materialized='view'
    )
}}

{% set input_tables = ['stage_<source_1>', 'stage_<source_2>', ...] %}

WITH union_cte AS (
    SELECT *, '<vendor_1>' AS dl_source FROM {{ref('stage_<source_1>')}}
    UNION ALL
    SELECT *, '<vendor_2>' AS dl_source FROM {{ref('stage_<source_2>')}}
),

renamed_cte AS (
    SELECT
      -- camelCase to snake_case renames
      <renamed_columns>,
      dl_source,
      ROW_NUMBER() OVER (
        PARTITION BY <pk_columns>
        ORDER BY <order_column> DESC
      ) seq
    FROM union_cte
)

SELECT
    <snake_case_columns>,
    dl_source,
    sha1(concat_ws('|', <checksum_columns>)) AS dl_checksum_value
FROM renamed_cte
WHERE seq = 1
```

**Key rules:**
- UNION ALL of all staging models
- Add `dl_source` to track provenance if not already in staging
- ROW_NUMBER dedup across all sources (same dedup pattern as entity-scaffold)
- sha1(concat_ws) checksum
- Materialized as view (or insert_overwrite for MSS)

### Step 9: Generate Prepared Model

Create the prepared model with bitemporal incremental strategy.

**Prompt reference:** `prompts/generate_foundation_prepared.md`

This is identical to the entity-scaffold prepared model pattern:
- `bitemporal_load_v2` strategy
- `generate_surrogate_key_v3()` from meta
- `get_audit_cols()` macro
- `cspn_commit_checkpoints()` post-hook
- `dl_source_system_code` from domain meta

### Step 10: Generate Model YAML

Create the dbt model YAML with sources and Casper meta.

**Prompt reference:** `prompts/generate_foundation_model_yml.md`

**Key difference from single-source:** Multiple sources listed in the `sources`
block (one per UC table). Each staging model is NOT listed; only the
integration and prepared models are listed.

```yaml
version: 2

sources:
  - name: cspn_std_<domain_1>_{{target.name}}
    tables:
      - name: <source_table_1>
  - name: cspn_std_<domain_2>_{{target.name}}
    tables:
      - name: <source_table_2>

models:
  - name: int_<entity_name>_union
    meta:
      enabled: true
      domain: <primary_domain>
  - name: <entity_name>
    meta:
      enabled: true
      domain: <primary_domain>
      dataset_type: <master|balance>
      table_name: <entity_name>
      tags: {"dc": "<dc_tag>"}
      process_schema: cspn_fndn2
```

### Step 11: Generate DDL

Create the Hive/Spark DDL for the prepared table.

**Prompt reference:** `prompts/generate_foundation_ddl.md`

Same pattern as entity-scaffold DDL, with all business columns from
the integration output plus standard audit columns.

### Step 12: Generate DAG YAML

**Delegate to --> `dag-yaml` skill**

Pass the collected inputs:
- Entity name, repo type, dc_tag, schedule
- For multi-source: if sources have different ingestion DAGs, configure
  multiple `dag_exec_check` tasks or use a single check for the latest source

If `dag-yaml` is not available, generate inline using patterns from
the references.

### Step 13: Generate Deequ Rules

**Delegate to --> `deequ-rules` skill**

Pass the collected inputs:
- Entity name, PK columns, repo type, domain, dc_tag
- For multi-source: add `hasCompleteness` on `dl_source` column
  and `isContainedIn` to validate source values

If `deequ-rules` is not available, generate inline using patterns
from the references.

### Step 14: Validate All (HUMAN CHECKPOINT)

Cross-check consistency across all generated artifacts:

| Check | What to Verify |
|-------|----------------|
| Column names | Same columns appear in staging --> integration --> prepared --> DDL |
| PK columns | Surrogate key cols in prepared config match PKs in DDL and Deequ rules |
| Refs | `{{ ref("int_<entity>_union") }}` in prepared matches integration model name |
| Source | Staging `cspn_source_v2`/`cspn_source` table names match `sources` in model YAML |
| Schema | DDL schema (`cspn_fndn2_{env}`) matches prepared model schema prefix |
| DAG | DAG model name matches prepared model name |
| Tags | `dc` tag in model YAML matches dc_tag in Deequ rules `process_domain` |
| Dataset type | `dataset_type` in YAML matches `load_type` in prepared config |
| UNION sources | All source tables from discovery are represented in staging models |
| dl_source | All vendor identifiers appear in integration UNION |

Present the validation report to the user for final review.

---

## Configuration

### Required User Inputs

| Input | Description | Example |
|-------|-------------|---------|
| Source tables | List of UC tables to UNION | `catalog.schema.table1`, `catalog.schema.table2` |
| Model name | Name for the canonical model | `dim_security`, `fact_trade` |
| Grain | What each row represents | "One row per security per business date" |

### Additional Inputs (EMR Mode)

| Input | Description | Example |
|-------|-------------|---------|
| `foundation_repo_path` | Path to the cloned foundation repo | `/path/to/casper-im-foundation` |
| `dc_tag` | Data classification tag | `acr`, `mfi`, `sft`, `mst` |
| `domain` | Primary source system domain | `rapid`, `cdm`, `thor`, `taco` |
| `dataset_type` | Master or balance | `master`, `balance` |
| `pk_columns` | Primary key column list | `['security_uid', 'as_of_date']` |
| `as_of_col` | (balance only) Business date column | `as_of_date` |
| `schedule_info` | Cron expression or null | `15 00 * * 2-6` or `null` |

### Required Environment Variables (Databricks Mode Only)

| Variable | Description |
|----------|-------------|
| `DATABRICKS_HOST` | Databricks workspace URL |
| `DATABRICKS_TOKEN` | SP-scoped credential ONLY (OAuth-materialized bearer or SP-PAT) per DBX-SEC-002. User PATs forbidden. See `/connect-databricks` for OAuth pattern. |
| `DATABRICKS_WAREHOUSE_ID` | SQL warehouse ID |
| `DATABRICKS_DEFAULT_CATALOG` | Target catalog |
| `DATABRICKS_DEFAULT_SCHEMA` | Target schema |

### Inferred Values

| Value | How It's Determined |
|-------|---------------------|
| Vendor names | Extracted from source table paths |
| Column mappings | From model spec YAML |
| Surrogate key | From grain/natural key definition |
| Repo type (foundation) | `dbt_project.yml` project name |
| Model directory suffix | IM adds `_f`, MSS does not |
| Source macro | IM uses `cspn_source_v2`, MSS uses `cspn_source` |
| Template refs | Determined by repo type (v4 variants for IM) |

---

## IM vs MSS Differences (EMR Mode)

| Aspect | IM Foundation | MSS Foundation |
|--------|---------------|----------------|
| Model directory | `models/<dc_tag>/<entity>_f/` | `models/<dc_tag>/<entity>/` |
| Source macro | `cspn_source_v2(schema, "table")` | `cspn_source(schema, "table")` or `{{ source() }}` |
| DDL location | `database/<entity>.sql` | `database/dbt_tables/<entity>.sql` |
| DAG location | `dags/<entity>_dbt.dag.yml` (flat) | `dags/<dc_tag>/<entity>_dbt.dag.yml` |
| Deequ location | `deequ_rules/<entity>_dbt.dq.yml` (flat) | `deequ_rules/<dc_tag>/<entity>_dbt.dq.yml` |
| Prepared schema | `cspn_fndn2_` + target.name | `cspn_fndn2_` or `cspn_cons2_` + target.name |
| Post-curate task | `refresh_pds_dremio` (Dremio refresh) | `adls_replication` (ADLS sync) |
| v4 suffix | Yes for v4 models (`_v4` on entity name) | No suffix |
| Curate template | `dbt_emr_critical_v4` | `dbt_emr_small` |
| XCom template | `dbt_emr_critical_xcom_generation_bitemporal_v2_v4` | `dbt_xcom_generation_bitemporal` |
| Tag template | `dbt_casper_balance_tag_v4` | `dbt_casper_tag` |
| DQ template | `emr_spark_deequ_verify_v11_critical_v4` | `emr_spark_deequ_verify_v11` |
| Notify template | `dbt_kafka_balance_notify` | `dbt_kafka_notify` |

---

## Prompt Templates

### Databricks Mode

| File | Purpose |
|------|---------|
| `prompts/dbt_canonical_model.md` | How to generate UNION-based dbt models |
| `prompts/dbt_schema_yml.md` | How to generate schema.yml with tests |
| `prompts/dbt_project_setup.md` | How to generate dbt_project.yml and profiles.yml |
| `prompts/run_databricks.md` | How to execute dbt models in Databricks |
| `prompts/validation.md` | Validation criteria for generated models |

### EMR Mode

| File | Purpose |
|------|---------|
| `prompts/detect_repo.md` | How to identify IM vs MSS from repo contents |
| `prompts/generate_foundation_staging.md` | Staging models with Casper macros (one per source) |
| `prompts/generate_foundation_integration.md` | UNION ALL + dedup + checksum (Casper conventions) |
| `prompts/generate_foundation_prepared.md` | Prepared model with bitemporal_load_v2 |
| `prompts/generate_foundation_model_yml.md` | Model YAML with multiple sources and Casper meta |
| `prompts/generate_foundation_ddl.md` | Hive DDL for curated zone |

---

## Next Steps After Generation

### Databricks Mode

1. **Review outputs** in `workspace/generated/domain-aligned/<model_name>/`
2. **Iterate on model** -- adjust columns, add sources, refine mappings
3. **Promote to EMR** -- re-run in **EMR** mode to generate Casper-ready artifacts
4. **Deploy** -- commit to foundation repo and let CI/CD deploy

### EMR Mode

1. **Review** -- Run the `foundation-review` skill to validate naming
   conventions, schema consistency, and CI readiness.
2. **Commit** -- Create a feature branch in the foundation repo and commit
   all generated files.
3. **PR** -- Open a pull request for team review.
4. **Deploy** -- Merge and let CI/CD deploy to EMR/Databricks.

---

## Error Handling

| Error | Resolution |
|-------|------------|
| `dbt_project.yml` not found (foundation) | Confirm the foundation_repo_path is correct |
| No existing models in dc_tag folder | Ask the user for explicit conventions; fall back to defaults |
| Conflicting entity name | Warn the user that a model directory already exists; confirm overwrite or rename |
| Missing `as_of_col` for balance | Re-prompt the user; this is required for bitemporal_load_v2 |
| Source tables not accessible | Verify UC table paths and permissions |
| Column type mismatch across sources | Check staging model CASTs; flag to user for resolution |
| dag-yaml or deequ-rules skill not available | Generate inline using reference patterns |

---

## Appendix: Naming Conventions (EMR Mode)

### Entity Name Rules

- Always `snake_case`
- IM v4 models append `_v4` (e.g., `consolidated_security_v4`)
- IM model directories append `_f` (e.g., `consolidated_security_v4_f`)
- MSS model directories match the entity name exactly (e.g., `territory`)

### Integration Model Naming (Multi-Source)

- Integration model name: `int_<entity_name>_union`
- The `_union` suffix distinguishes multi-source integration from single-source

### Source Table Naming

- IM: `<domain>_<descriptive_name>_f1_v1_t1` (e.g., `rapid_security_master_f1_v1_t1`)
- MSS: `<domain>_<descriptive_name>` or via `{{ source() }}`

### Schema Prefixes

| Schema | Usage |
|--------|-------|
| `cspn_std_<domain>_` | Standard zone source tables |
| `cspn_work2_` | Staging and integration work schema |
| `cspn_fndn2_` | Foundation prepared tables |
| `cspn_cons2_` | Consolidated schema (some MSS) |

## Post-completion: Wiki Update

> After completing this skill, the `domain-wiki` skill handles wiki updates in `docs/wiki/`. See *(external plugin — not bundled in this repo)*.
