---
name: source-aligned
description: >-
  Generate source-aligned data product artifacts — ingestion YAML, DQ rules,
  dbt models (staging/integration/prepared), DDL, source YAML, and
  Airflow DAGs — from a CSV, DAT, or .out.gz source file. Part of the
  AI Catalyst DPLC plugin bundle, aligned with RFD2 Phase 4 (Build). Use this skill
  whenever the user mentions catalyst source-aligned, data profiling a source file,
  generating ingestion configs, creating dbt models from a data file,
  building a data product pipeline, generating DDL or Airflow DAGs from
  source data, validating generated artifacts, tuning existing models,
  running dbt against Databricks, or processing Bloomberg/RDM/Moody's/FactSet/
  Refinitiv/MSCI feeds. Also trigger when the user asks about process_domain,
  dc_tag, bitemporal_load_v2, or batch-processing multiple data feeds.
metadata:
  tier: workflow
  lifecycle-phase: phase-4-build
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
---

# AI Catalyst DPLC: Source-Aligned Data Product Generator

> **RFD2 Phase:** Phase 4 (Build) — Source-Aligned Pipeline  
> **Claude Code Users:** See *(planned — not yet created)* for equivalent command prompts

> **Integration Note**: This skill is invoked as part of the AI Catalyst DPLC lifecycle. It can also be used standalone for batch data product generation.

Generate all artifacts needed to ingest and curate a data source into the foundation layer. This skill orchestrates multiple generation steps, producing EMR/Databricks-targeted code.

## Decision Rule

| User Context | Action |
|---|---|
| Has a **raw source file** (CSV/DAT) and **no existing project** | → Use this skill (Casper Source-Aligned) |
| Has an **existing Hourglass project** and is iterating | → Use Hourglass phases instead |
| Completed source-aligned generation | → Enter Hourglass lifecycle at Phase 1 (Bootstrap) to configure and iterate |

## When to Use

- User provides a CSV/DAT file and wants to create a data pipeline
- User asks to "generate ingestion", "create dbt models from file", "build a data product"
- User wants the full source-aligned workflow from profiling to DAG generation

**Recommended pre-step:** Run the `clone-repos` skill first to ensure reference repos and templates are available.

## Outputs

All artifacts are written to `workspace/generated/source-aligned/<model_name>/` and **separated by workload**:

```
workspace/generated/source-aligned/<model_name>/
├── ingestion/
│   ├── profiling_output.md      # Data profiling results
│   ├── <process_name>.yml       # Ingestion configuration
│   ├── pipeline.py              # Ingestion DAG loader
│   └── dq.yml                   # Data quality rules
├── curation-emr/
│   ├── source.yml               # Source-to-target mapping
│   ├── ddl.sql                  # CREATE TABLE DDL
│   └── models/
│       ├── staging/
│       │   └── stage_<source>.sql   # Staging dbt model
│       ├── integration/
│       │   └── int_<model>_v4.sql   # Integration dbt model
│       ├── prepared/
│       │   └── <model>_v4.sql       # Prepared dbt model
│       └── <model>.yml              # dbt model YAML
└── curation-databricks/
   ├── dag.yml                  # Airflow DAG configuration
   └── models/                  # Databricks-ready dbt models (patched)
       ├── staging/
       ├── integration/
       ├── prepared/
       └── <model>.yml
```

## Order of Operations

Execute steps in this exact order. Each step depends on outputs from previous steps.

```
0. read-context          ─► Read .catalyst-build.yml#mode; branch emission accordingly
                            │
1. profile               ─► Detect/skip headers & trailers; recommend PKs; always keep null columns
                            │  If non-flat-CSV shape: scaffold ingestion/local_helper.py
                            │
2. generate-ingestion    ─► <process_name>.yml, dq.yml, pipeline.py
                            │
3. generate-source       ─► User confirms dataset type (Master/Balance)
                            │  User provides as_of_col if Balance
                            │
4. generate-ddl          ─► ddl.sql
                            │
5. validate (ddl)        ─► Validates DDL, loops if issues
                            │
6. generate-dbt          ─► staging → integration → prepared → model.yml
                            │
7. validate (dbt)        ─► Validates dbt models, loops if issues
                            │
8. generate-dag          ─► dag.yml
                            │
9. validate (dag)        ─► Validates Airflow DAG, loops if issues
                            │
10. verify-live-data     ─► Run emitted ingestion against a small slice;
                            │  assert column count, no all-null rows, unique
                            │  names, type consistency; loop on failure
```

### Step 0: Read context (`.catalyst-build.yml#mode`)

Before any generation, read `.catalyst-build.yml` from the repo root (or
the model workspace). The `mode` field switches emission defaults; if
the file is missing, default to `prototype`.

| Mode | Emission shape |
|---|---|
| `prototype` | `curation-databricks/` only; skip `curation-emr/`; scaffold `local_helper.py` if Issue-1 triggers; run verify-live-data (step 11) against the user-supplied sample file |
| `production` | Both `curation-emr/` and `curation-databricks/`; verify-live-data runs against a small slice of real production data |
| `lift-and-shift` | Detect existing artifacts in the target locations; align emitted output with what's there rather than overwriting |

Mirrors the pattern set by AICAT-135 (`setup-databricks-asset-bundle`)
and AICAT-140 (`setup-dbt-project`).

### Human-in-the-Loop Checkpoints

| After Step | Confirmation Required |
|------------|----------------------|
| 1 (profile) | PKs are recommended by default (user may override); 100% null columns are always kept |
| 3 (source) | Confirm dataset type (Master if no date in PK, else Balance); provide `as_of_col` for Balance |
| 5, 7, 9 (validate) | Review validation feedback, approve or request regeneration |

### Validation Loop

After each major artifact type (DDL, dbt, Airflow), validation runs automatically:
- If `score >= 7`: Proceed to next step
- If `score < 7`: Regenerate with feedback (up to 5 retries)
- Validation criteria in `prompts/validation.md`

---

## How to Execute

### Default dbt pattern (required)

Co-intelligence **defaults to v4 bi-temporal** models using **`bitemporal_load_v2`**. Prototype/merge-only behavior is **not** used unless explicitly requested.

This means prepared models:
- include `dl_row_uid`, `dl_checksum_value`, and audit columns via macros
- use `incremental_strategy = "bitemporal_load_v2"`
- require `meta.surrogate_key_cols` in the model config

If the user explicitly requests prototype-only behavior, call it out and switch to non-bitemporal configs.

### Input Folder Setup (Required)

Before running the skill, **ensure the input directory exists**. If it doesn't, create it and place your source files there:

```
workspace/source-aligned/inputs/
```

If the directory is missing, create it automatically before profiling:

- Create: `workspace/source-aligned/inputs/`
- Coach the user: "Please place your CSV/DAT file in `workspace/source-aligned/inputs/` and provide the full path."

### Local-first execution (Databricks)

Use this path when you want to run the source-aligned outputs **locally first** against Databricks before handing off to developers.

**Goal:** Reuse the generated artifacts to load data into raw → standard layers and run dbt against Databricks.

**Execution checklist (local):**
1. **Databricks auth**: Ensure the Databricks CLI is configured (profile preferred). Use the same warehouse for profiling + execution.
2. **Landing (raw) path**: Use the `l2r.landing_path` and `l2r.file_pattern` from `ingestion.yml` to place files into the raw landing zone. Keep the directory convention intact.
3. **Raw → Standard**: Use the generated `ingestion.yml` + `schema` to load into standard tables in Databricks. When executing locally, mirror the standard table naming used in `caspian-pipelines`/`caspian-im-foundation` so the handoff is straightforward.
4. **dbt run**: Execute the generated dbt models against Databricks once the standard tables exist. Use the same model naming and folder structure expected by `caspian-im-foundation`.
5. **Validate**: Sample a few rows from raw and standard to confirm row counts and nullability rules before sending outputs to devs.

**Local helper (SQL Warehouse):**
Use `scripts/dbx_sql.py` for ad-hoc checks or to run prototype SQL:
- `scripts/dbx_sql.py --warehouse-id <WAREHOUSE_ID> --sql-file <file.sql>`

**Local helper (ingestion adapter):**
Use the Databricks local adapter to push files to landing/raw and load a standard Delta table:
- `python skills/source-aligned/scripts/databricks_local_ingest.py --ingestion-yml <path/to/<process_name>.yml> --input-file <path/to/file>`

Optional flags:
- `--landing-only` (skip raw→standard; no pyspark required)
- `--use-databricks-sdk` (upload to Volumes via Databricks SDK)
- `--landing-base dbfs:/tmp/coi/landing`
- `--raw-base dbfs:/tmp/coi/raw`
- `--standard-catalog main`
- `--standard-schema standard_<process_domain>`
- `--standard-table <process_name>`
- `--standard-path-base dbfs:/tmp/coi/standard`
- `--run-dbt --dbt-project <path> --dbt-models <selector> --profiles-dir <path>`

Environment overrides (for Databricks-specific settings):
- `COI_DBX_LANDING_BASE`
- `COI_DBX_RAW_BASE`
- `COI_DBX_STANDARD_CATALOG`
- `COI_DBX_STANDARD_SCHEMA`
- `COI_DBX_STANDARD_TABLE`
- `COI_DBX_STANDARD_PATH_BASE`

You can also provide a YAML overrides file:
- `--env-config path/to/dbx_env.yml`

Example `dbx_env.yml`:
```yaml
COI_DBX_LANDING_BASE: /Volumes/<catalog>/<schema>/<volume>/landing
COI_DBX_RAW_BASE: /Volumes/<catalog>/<schema>/<volume>/raw
COI_DBX_STANDARD_CATALOG: <catalog>
COI_DBX_STANDARD_SCHEMA: <standard_schema_from_env>
COI_DBX_STANDARD_TABLE: <optional_override_table_name>
DATABRICKS_RUN_AS_USER: <user_email>   # usually blank — auto-detected from CLI auth
```

> **Heads-up on `DATABRICKS_RUN_AS_USER`.** Leave it blank in most cases;
> the serverless submit script (`submit_serverless_raw_to_standard.py`)
> auto-detects via `client.current_user.me()` so the job runs as whatever
> identity the Databricks CLI is currently authed as. **Do not** copy it
> from `databricks schemas get <catalog>.<schema>` → `created_by`: that's
> provisioning history (often an admin / elevated account like `<user>2a@`)
> and won't match the CLI's day-to-day identity (`<user>@`). The job will
> fail or run under the wrong principal.

**Databricks Volumes note:**
- Use Volumes for landing and raw paths.
- Standard is written as managed **tables** (catalog/schema/table), so no volume path is required unless you
   explicitly want external locations (then set `COI_DBX_STANDARD_PATH_BASE`).

**Serverless job notes (Databricks):**
- Use `skills/source-aligned/scripts/submit_serverless_raw_to_standard.py` for serverless runs.
- Upload `scripts/databricks_local_ingest.py` and the ingestion YAMLs into the code volume first (via `scripts/upload_to_volume.py`).
- **Landing upload is required** before serverless raw→standard: upload the source files into the landing path for each feed.
   - Uses `COI_DBX_LANDING_BASE` if set, otherwise `/Volumes/<catalog>/<schema>/landing`.
   - You can do this automatically with `submit_serverless_raw_to_standard.py --upload-landing` by passing
      `--local-ingestion-yml` and `--input-file` pairs (must match `--ingestion-yml` order).
- The serverless environment is pinned to **version 4** in the submit script; do not add external dependencies.
- `dbfs:/` config reads must work without `/dbfs` mount; the adapter reads `dbfs:/` via Spark in serverless.
- Raw outputs follow ingestion-libs layout: `/raw/<domain>/<name>/YYYY/MM/DD/HHMMSSffffff/`.
- Standard tables include ingestion partition columns `year__`, `month__`, `day__`, `time__` (matching ingestion libs).

**Curation (dbt) run (Databricks SQL):**
- Use `skills/source-aligned/scripts/run_curation_dbt.py` to run dbt models against Databricks SQL.
- The runner auto-detects the latest generated models under `workspace/generated/source-aligned/<model>/models` (or `sample_workspace_output/generated/...`) and the latest `dbt_project.yml` under `workspace/generated` if paths are omitted.
- Provide `--model-name <model>` to pick a specific generated model directory.
- You can override with `--models-dir` and `--dbt-project` if needed. The runner patches models to match curation behavior:
   - Replace `{{target.name}}` with the target name.
   - Replace `chronological` with `latest`.
   - Remove `vacuum` and `cspn_commit_checkpoints()` hooks.

**Casper source-aligned macro overrides (self-contained):**
To avoid reliance on other skills, source-aligned maintains its own macro templates under:

```
skills/source-aligned/templates/dbt_project/macros_overrides/
```

These are copied into `workspace/generated/dbt_project/macros_overrides/` before running dbt.
Included overrides:
- `surrogate_key_v3.sql` (implements `generate_surrogate_key_v3()` + `get_audit_cols()`)
- `cspn_commit_checkpoints.sql` (no-op)
- `create_schema.sql` (no-op for CREATE SCHEMA)
- `cspn_utils.sql` (implements `cspn_source()` used by staging models)
- `dbt_spark_get_incremental_sql.sql` (compatibility shim)
- `get_custom_schema.sql` (Unity Catalog schema handling)

**Databricks dbt customizations captured (EMR → Databricks parity):**
The following Databricks-specific behaviors are explicitly captured so runs match the EMR pattern without relying on external repos:

- **Incremental strategy support:** `bitemporal_load_v2` is supported via `dbt_spark_get_incremental_sql.sql`.
- **Schema creation:** `create_schema.sql` is a no-op to avoid CREATE SCHEMA permission failures.
- **Source resolution:** `cspn_utils.sql` provides `cspn_source()` so staging models resolve fully qualified UC tables.
- **Schema naming:** `get_custom_schema.sql` ensures Unity Catalog schema names are treated as full schema names (no suffix concatenation).
- **Checkpoint hooks:** `cspn_commit_checkpoints.sql` is a no-op to avoid EMR-only hooks.

**dbt warnings eliminated (expected structure):**
- Model YAML uses `config.meta` (not top-level `meta`).
- `load_type` is placed under `config.meta` in SQL configs.
- `dbt deps` is skipped when `packages.yml` is empty to avoid warnings.

If any new EMR-only macro or hook appears in generated models, it must be mirrored here as a Databricks-safe override.

**Runtime patching by `scripts/run_curation_dbt.py`:**
The dbt runner applies these patches at runtime to make EMR-style models work in Databricks:

| Pattern | Replacement | Why |
|---------|------------|-----|
| `schema = "cspn_work2_"\|string + target.name` | `schema = env_var('DATABRICKS_DEFAULT_SCHEMA')` | EMR schemas don't exist in user's catalog |
| `schema = "cspn_fndn2_"\|string + target.name` | `schema = env_var('DATABRICKS_DEFAULT_SCHEMA')` | Same reason |
| `cspn_std_<domain>_<suffix>` source schemas | `DATABRICKS_DEFAULT_SCHEMA` | Source tables are in user's schema, not EMR convention |
| `generate_surrogate_key_v3()` | `generate_surrogate_key_v3(['<pk_col>'])` | Jinja can't reliably read `model.config.meta` at compile time |
| `vacuum {{ this }} retain 0 hours` | (removed) | Not needed for prototype runs |
| `{{ cspn_commit_checkpoints() }}` | (removed) | EMR-only hook |

**Schema resolution (Databricks env-only):**
All staging/integration/prepared models are configured to write to the schema provided by:

```
env_var('DATABRICKS_DEFAULT_SCHEMA')
```

The source schema used by staging models also comes from `DATABRICKS_DEFAULT_SCHEMA`.
This avoids `cspn_work2_<target>` and other suffix-based schemas that are not present in the environment.

**Required env vars for dbt-databricks:**
- `DATABRICKS_HOST`, `DATABRICKS_TOKEN`

**Optional env vars:**
- `DATABRICKS_HTTP_PATH` (if omitted, dbt will derive it from `DATABRICKS_WAREHOUSE_ID` in the generated `profiles.yml`)
- `DATABRICKS_WAREHOUSE_ID` (used to auto-fill http_path when not explicitly set)
- `DBT_TARGET` (defaults to `dev1`)

**Execution note (no shell exports needed):**
`scripts/run_curation_dbt.py` loads `.env` directly, so you do **not** need `export $(...)` or `xargs`.

If `COI_DBX_LANDING_BASE` / `COI_DBX_RAW_BASE` are not set, the adapter defaults to:
- `/Volumes/<catalog>/<schema>/landing`
- `/Volumes/<catalog>/<schema>/raw`

**Standard schema requirement:**
- `COI_DBX_STANDARD_SCHEMA` or `DATABRICKS_DEFAULT_SCHEMA` must be set in `.env` or `--env-config`.
- `COI_DBX_STANDARD_CATALOG` or `DATABRICKS_DEFAULT_CATALOG` must be set in `.env` or `--env-config`.

**Prototype-mode layer-to-schema mapping (prompt; never auto-create):**

In production mode the layer→schema mapping is decided by infra (set
`COI_DBX_STANDARD_*` and `DATABRICKS_DEFAULT_*` explicitly); skip this
section. In prototype mode the developer usually has access to
**several** schemas in their working catalog — but none of them are
obviously named for the layers this skill needs to populate
(`raw`, `standard`, dbt-target / `curated`). The skill's job is to
help the user **map** existing schemas to layers, not to assume
schema names follow a convention or that only one schema exists.

The collision risk is real and worth naming: if `standard` and
`dbt-target` land in the same schema, raw-shape tables sit next to
curated marts in the same namespace — that's the AICAT-133 Bug 2
failure mode, and promotion to production will need cleanup.

Before running serverless ingest in prototype mode:

1. Read-only list the schemas the developer has `CREATE TABLE` on
   inside their working catalog (use
   `skills/clients/databricks_tools_core/unity_catalog/` —
   `list_schemas` + `check_schema_grants`).
2. If `COI_DBX_STANDARD_*` and `DATABRICKS_DEFAULT_*` aren't already
   pointing at distinct schemas, present the candidates and ask the
   user to map them to layers explicitly:

   > **Layer-to-schema mapping**
   >
   > Schemas you have `CREATE TABLE` on in `{catalog}`:
   > `schema_a`, `schema_b`, `schema_c`, …
   >
   > For this run, which schema should be used for:
   > - **standard** (raw→standard ingestion target)? →
   > - **dbt-target** (curated marts the dbt models write to)? →
   >
   > These can be the same schema if you accept the collision risk;
   > otherwise pick two different ones from the list above.

3. If a layer's target schema doesn't already exist among the
   candidates, **stop** — the skill never runs `CREATE SCHEMA`.
   Surface the exact `databricks schemas create --catalog-name
   <catalog> --name <schema>` command for the user to run with their
   own grants, then re-invoke the skill.
4. Persist the resolved mapping to `.catalyst-build.yml` under
   `layer_schema_mapping:` so the next invocation doesn't re-prompt:

   ```yaml
   # .catalyst-build.yml  (append)
   layer_schema_mapping:
     catalog:     "<catalog>"
     standard:    "<schema_for_raw_to_standard>"
     dbt_target:  "<schema_for_curated_dbt>"
     resolved_by: source-aligned     # idempotency marker
   ```

**The skill never runs `CREATE SCHEMA`** — schema provisioning belongs
to the developer / platform team and may need grants the CLI-authed
identity doesn't have. This is the same posture as the existing
`create_schema.sql` no-op convention elsewhere in the skill bundle.

### Multiple Files = Multiple Data Products

**Each source file is treated as an independent data product.** If you have multiple files in the inputs folder, you can:
- Process them **sequentially** (one at a time with confirmation between each), OR
- Process them **in parallel** if the user says "don't care about order" or similar

When processing multiple files:
1. List the files in `workspace/source-aligned/inputs/`
2. Generate all artifacts for each file
3. After **all files** are generated, ask once: "Do you want me to run these in Databricks now?"
4. If yes, run serverless ingestion for **all files together**, then dbt for each model

```
workspace/source-aligned/inputs/
├── equity_namr.out.gz          → Run 1 → workspace/generated/source-aligned/equity_namr/
├── equity_namr_cins.out.gz     → Run 2 → workspace/generated/source-aligned/equity_namr_cins/
└── another_feed.csv            → Run 3 → workspace/generated/source-aligned/another_feed/
```

### Mode: `full` (Complete Workflow)

Run the entire workflow from profiling to DAG generation.

**User provides:**
- Path to source file (CSV/DAT)
- `process_domain` (system of record, e.g., "blmbrg", "rdm", "moodys") — used for raw path and standard schema
- `dc_tag` (data classification tag, e.g., "blmbrg", "ref", "ofs") — often same as domain, but not always
- `schedule_info` (cron expression or "unscheduled")

**Note:** `process_domain` ≠ `dc_tag` in all cases. Example: RDM (system of record) uses `ref` as the dc_tag.

**Tag confirmation (required):**
Before accepting `dc_tag`, confirm against existing ingestion configs in `caspian-pipelines`:
1. Check `workspace/reference/repos/caspian-pipelines/config/dc_tag_list.yml` for valid tags.
2. Search `workspace/reference/repos/caspian-pipelines/dags/ingestion/**` for related files by `process_domain`,
   `process_name`, or similar filename patterns. If a close match exists, reuse its `file_tags.dc`.
3. If no match exists, use the provided `dc_tag` and note that it was user-supplied.

Helper script (optional):
`python skills/source-aligned/scripts/find_related_ingestion_configs.py --process-domain <domain> --process-name <name> --file-pattern <pattern>`

**Example invocation:**
```
Run source-aligned on /path/to/my_data.csv with dc_tag=aix and schedule=unscheduled
```

**I will:**
1. Profile the file (see `prompts/data_profiling.md`)
2. Recommend PKs by default (you can override) and always keep 100% null columns
3. Generate ingestion.yml, dq.yml, and pipeline.py (see `prompts/ingestion_yml.md`, `prompts/dq_yml.md`, `prompts/ingestion_pipeline.md`)
4. Generate source.yml, asking you to confirm dataset type (see `prompts/source_yml.md`)
5. Generate DDL and validate (see `prompts/ddl.md`, `prompts/validation.md`)
6. Generate dbt models and validate (see `prompts/dbt_staging.md`, `prompts/dbt_integration.md`, `prompts/dbt_prepared.md`, `prompts/dbt_model_yml.md`, `prompts/validation.md`)
7. Generate Airflow DAG and validate (see `prompts/airflow_dag.md`, `prompts/validation.md`)
8. Write artifacts separated by workload:
   - `ingestion/` (profiling_output.md, ingestion.yml, dq.yml, pipeline.py)
   - `curation-emr/` (source.yml, ddl.sql, models/)
   - `curation-databricks/` (dag.yml)

---

### Mode: `profile`

Profile a source file to understand schema, datatypes, and primary key candidates.

**User provides:**
- Path to source file

**I will:**
1. Run Python profiling script via terminal (pandas-based)
2. Display profiling table with: Column Name, Data Type, Null Count, Null %, Unique Count, Uniqueness %, PK Candidate, Sample Values
3. Apply datatype overrides (datetime64→timestamp, float64→decimal, etc.)
4. Recommend primary keys by default (user can override) and always keep null columns

**Execution note:** To avoid shell heredoc issues, always write multi-line Python profiling code to a temporary script under `workspace/tmp/` and run it from there.

**Prompt reference:** `prompts/data_profiling.md`

**Header/Trailer detection (all delimited files):**
- Always scan the first and last 200 lines to detect preamble/trailer blocks.
- Compute the dominant delimiter count per line (mode); any leading/trailing lines with a different delimiter count are treated as preamble/trailer.
- Also treat any lines containing known markers (e.g., `START-OF-*`, `END-OF-*`) or `key=value` metadata lines as preamble/trailer.
- For detected preamble/trailer, set `header: false`, `skip_header_rows`, and `skip_footer_rows` in ingestion.

**Marker-based files (.out.gz or similar):** If the file uses `START-OF-FIELDS` / `START-OF-DATA` / `END-OF-DATA` markers, profile it with a temporary helper script under `workspace/tmp/` (workspace-only, not a reusable skill script):

`python workspace/tmp/profile_bloomberg_markers.py --input <path/to/file.out.gz> --output-dir <output_dir>`

**Non-flat-CSV formats — scaffold a workspace-local helper.** If the
profile step detects marker framing, multi-block headers, request-response
prefix columns, or a footer block, the skill copies
`skills/source-aligned/templates/local_helper.py` to:

```
workspace/generated/source-aligned/<model_name>/ingestion/local_helper.py
```

The helper is the user's code now — product-specific. It produces a
flat CSV the standard ingestion pipeline consumes; wire it by pointing
`ingestion.yml#l2r.file_pattern` at the helper output, not the raw
file. See `references/local_helpers.md` for the iteration loop and the
graduation criteria (when to promote a helper to a first-class
adapter).

---

### Mode: `generate-ingestion`

Generate ingestion.yml, dq.yml, and pipeline.py from profiling output.

**Requires:** Completed profiling, user-confirmed PKs, dc_tag, schedule_info

**I will:**
1. Generate `ingestion.yml` with schema, file patterns, landing paths
2. Generate `dq.yml` with uniqueness rules on primary keys
3. Generate `pipeline.py` to load the YAML and create Airflow DAG

**Note:** For files with explicit header/footer markers **only when markers are present**, auto-detect and set:
- `header: false`
- `skip_header_rows: <line_number_of_START-OF-DATA>`
- `skip_footer_rows: <trailing_lines_after_END-OF-DATA>`
Helper script: `skills/source-aligned/scripts/header_footer_markers.py` (pass `--start-marker` / `--end-marker`)

**Execution safety note (avoid heredoc):**
To prevent shell heredoc issues, **do not** generate ingestion YAML via inline `python - <<'PY'` blocks. Use the helper script:

`python skills/source-aligned/scripts/generate_ingestion_from_profile.py --profile <profiling_output.md> --output <process_name>.yml --process-domain <domain> --process-name <name> --file-pattern <file> --landing-path <path> --dc-tag <dc_tag> --cron "<cron>" --delimiter "|" --skip-header-rows <n> --skip-footer-rows <n>`

**Output location:** write to `workspace/generated/source-aligned/<model_name>/ingestion/<process_name>.yml`.

**Authoritative ingestion schema reference:**
- `workspace/reference/repos/caspian-ingestion-libs/casper/orchestration/templates/ingestion/model/__init__.py`
- `workspace/reference/repos/caspian-ingestion-libs/docs/PipelineConfigSpec.yml`

**Prompt references:** `prompts/ingestion_yml.md`, `prompts/dq_yml.md`, `prompts/ingestion_pipeline.md`

**Helper (optional):**
`python skills/source-aligned/scripts/generate_coi_artifacts.py --ingestion <process_name>.yml --base-dir workspace/generated/source-aligned/<model_name> --process-domain <domain> --process-name <name> --dc-tag <dc_tag> --schedule-interval "<cron_plus_30>" --pk <pk_alias> [--pk <pk_alias> ...]`

---

### Mode: `generate-source`

Generate source.yml (source-to-target mapping).

**Requires:** Completed ingestion.yml and dq.yml

**I will:**
1. Determine dataset type (Master if no date field in PK, else Balance)
2. Ask you to confirm dataset type
3. If Balance, ask for `as_of_col` (business date column)
4. Generate `source.yml` with column mappings

**Prompt reference:** `prompts/source_yml.md`

**Output location:** write to `workspace/generated/source-aligned/<model_name>/curation-emr/source.yml`.

---

### Mode: `generate-ddl`

Generate CREATE TABLE DDL from source.yml.

**Requires:** Completed source.yml

**I will:**
1. Generate DDL with appropriate audit columns (different for Master vs Balance)
2. Include partitioning, Delta table properties, S3 location

**Prompt reference:** `prompts/ddl.md`

**Output location:** write to `workspace/generated/source-aligned/<model_name>/curation-emr/ddl.sql`.

---

### Mode: `generate-dbt`

Generate all dbt models from source.yml.

**Requires:** Completed source.yml

**I will generate (in order):**
1. Staging model (`stage_<source>.sql`) - SELECT * from source
2. Integration model (`int_<model>_v4.sql`) - Casts, transforms, checksum
3. Prepared model (`<model>_v4.sql`) - Final model with surrogate key and audit columns
4. Model YAML (`<model>.yml`) - dbt documentation

**Prompt references:** `prompts/dbt_staging.md`, `prompts/dbt_integration.md`, `prompts/dbt_prepared.md`, `prompts/dbt_model_yml.md`

**Output location:** write to `workspace/generated/source-aligned/<model_name>/curation-emr/models/`.

**Helper (optional):**
`python skills/source-aligned/scripts/generate_dbt_ddl_dag.py --source workspace/generated/source-aligned/<model_name>/curation-emr/source.yml --base-dir workspace/generated/source-aligned/<model_name>`

---

### Mode: `generate-dag`

Generate Airflow DAG YAML.

**Requires:** Completed DDL and dbt models

**I will:**
1. Generate 7-task DAG structure:
   - ingestion → scd_curate → xcom → dq_validation → scd_tag → refresh_delta_ds → scd_notify
2. Configure EMR container operators with Spark settings

**Prompt reference:** `prompts/airflow_dag.md`

**Output location:** write to `workspace/generated/source-aligned/<model_name>/curation-databricks/dag.yml`.

---

### Mode: `verify-live-data`

Run the emitted ingestion against a small slice of the source file and
sanity-check the output before declaring the workflow complete. Catches
column shifts, junk rows, name collisions, and type drift that inspection
alone misses.

**Requires:** Emitted ingestion YAML + a slice of source data (in
`prototype` mode this is the user-supplied sample file; in `production`
mode it's a small slice — first/last 100 rows — of real production data).

**I will:**
1. Load the first/last N rows of the source (or the helper output if a
   `local_helper.py` was scaffolded) into a DataFrame using the emitted
   ingestion config.
2. Assert:
   - Column count matches what the profile step computed
   - No row is NULL across every business column (junk-row check —
     comment lines, footer markers, etc. shouldn't land as data)
   - Output column names are unique (no collisions from prefix columns
     vs FIELDS-header columns)
   - Declared types are consistent with observed values (no string
     values in a column declared INT64, etc.)
3. On failure: report which assertion broke and which generation step
   owns the fix (profile / generate-ingestion / generate-ddl / generate-dbt).
   Loop back to that step.

**Mode interaction:**
- `prototype`: verify against the user-supplied sample file
- `production`: verify against a small slice of real production data
- `lift-and-shift`: skip if existing artifacts already pass downstream
  data-quality gates

---

### Mode: `validate`

Validate generated artifacts against quality criteria.

**Requires:** One or more generated artifacts (DDL, dbt, Airflow)

**User provides:**
- Artifact type to validate: `ddl`, `dbt`, `airflow`, or `all`
- The artifact content (or path to artifact)

**I will:**
1. Apply validation criteria from `prompts/validation.md`
2. Return structured assessment with score, issues, recommendations
3. If score < 7, provide feedback for regeneration

**Prompt reference:** `prompts/validation.md`

---

### Mode: `tune`

Modify existing models based on user feedback.

**Requires:** Generated models, user modification request

**User provides:**
- Specific change request (add column, change type, modify transformation, etc.)
- Which model to modify (or "all" to apply consistently)

**I will:**
1. Analyze the modification request
2. Identify affected model files (staging, integration, prepared, yml, ddl)
3. Apply changes consistently across all affected files
4. Return complete updated files

**Example requests:**
- "Add column `currency_code` with type STRING"
- "Change `market_value` from DECIMAL(18,2) to DECIMAL(18,4)"
- "Remove column `deprecated_field`"
- "Change load_type from full to balance with as_of_col=effective_date"

**Prompt reference:** `prompts/tuner.md`

---

## Configuration

### Required User Inputs

| Input | Description | Example |
|-------|-------------|---------|
| `file_path` | Path to source CSV/DAT file | `workspace/source-aligned/inputs/my_data.csv` |
| `process_domain` | System of record (NOT inferred from filename) | `blmbrg`, `rdm`, `moodys`, `refinitiv` |
| `dc_tag` | Data classification tag (often same as domain, but not always) | `blmbrg`, `ref`, `ofs`, `rat` |
| `schedule_info` | Cron schedule or "unscheduled" | `0 21 * * 1-5` or `unscheduled` |

**Important:** `process_domain` and `dc_tag` are often the same (e.g., Bloomberg uses `blmbrg` for both), but not always:
- RDM (system of record) → `dc_tag` = `ref`
- Moody's (system of record) → `dc_tag` = `rat` (ratings)

**Recommended input location:** `workspace/source-aligned/inputs/`

### Inferred Values

| Value | How It's Determined |
|-------|---------------------|
| `process_name` | Filename without extension and timestamp |
| `target_table` | Process name with `_v4` suffix, minus `f1_v1_t1` |
| `dataset_type` | `Master` if no date in PK, `Balance` if date in PK |

---

## Prompt Templates

All generation is guided by prompt templates in `prompts/`:

| File | Purpose |
|------|---------|
| `references/data_profiling.md` | How to profile files with pandas |
| `references/ingestion_yml.md` | How to generate ingestion.yml |
| `references/ingestion_pipeline.md` | How to generate pipeline.py |
| `references/dq_yml.md` | How to generate dq.yml |
| `references/source_yml.md` | How to generate source.yml |
| `references/ddl.md` | How to generate DDL |
| `references/dbt_staging.md` | How to generate staging model |
| `references/dbt_integration.md` | How to generate integration model |
| `references/dbt_prepared.md` | How to generate prepared model |
| `references/dbt_model_yml.md` | How to generate model YAML |
| `references/airflow_dag.md` | How to generate Airflow DAG |
| `references/validation.md` | Validation criteria for all artifact types |
| `references/tuner.md` | How to modify existing models |
| `references/local_helpers.md` | When to scaffold `local_helper.py` and graduation path |

---

## Next Steps After Generation

After generating artifacts:

1. **Review outputs** in `workspace/generated/source-aligned/<model_name>/`
2. **Test dbt models** using the `run-databricks` skill (optional)
3. **Commit to repos** - ingestion artifacts to `casper-pipelines`, dbt/DDL to `casper-im-foundation`
4. **Deploy via CI/CD** to production EMR/Databricks environment

### Databricks execution prompt (required)

After **all artifacts** for a file are generated, always ask:

> "Do you want me to run the ingestion + dbt curation in Databricks now?"

**Behavior:**
- If the user says **yes**, run the Databricks steps using **existing `.env` settings** (or `DATABRICKS_CONFIG_PROFILE`).
- **Do not ask the user to re‑enter credentials** if `.env` already contains them.
- Only request credentials **if** `.env` is missing or incomplete for required fields.
- Never create a new `.env` if one already exists.

---

## Databricks Execution Path (end-to-end)

When executing in Databricks, follow this exact sequence:

### Step 1: Verify `.env` exists and has required settings

Check for `.env` in the repo root. Required fields:
- `DATABRICKS_HOST` or `DATABRICKS_CONFIG_PROFILE`
- `DATABRICKS_TOKEN` (if not using profile)
- `DATABRICKS_WAREHOUSE_ID` or `DATABRICKS_HTTP_PATH`
- `DATABRICKS_DEFAULT_CATALOG`
- `DATABRICKS_DEFAULT_SCHEMA`
- `DATABRICKS_RUN_AS_USER` (for serverless jobs — usually blank; auto-detected from CLI auth. See heads-up note above; do NOT copy from a schema's `created_by`.)

**If `.env` exists with these fields, do NOT ask for credentials. Just use them.**

### Step 2: Upload code + configs to Databricks Volume

Use `scripts/upload_to_volume.py` to push:
- `scripts/databricks_local_ingest.py`
- All generated `<process_name>.yml` files

```bash
python skills/source-aligned/scripts/upload_to_volume.py \
  --volume code \
  --files skills/source-aligned/scripts/databricks_local_ingest.py \
         workspace/generated/source-aligned/<model>/ingestion/<process_name>.yml
```

### Step 3: Run serverless raw→standard (with landing upload)

Use `scripts/submit_serverless_raw_to_standard.py` with `--upload-landing`:

```bash
python skills/source-aligned/scripts/submit_serverless_raw_to_standard.py \
  --volume code \
  --ingestion-yml <process_name>.yml \
  --local-ingestion-yml workspace/generated/source-aligned/<model>/ingestion/<process_name>.yml \
  --input-file workspace/source-aligned/inputs/<source_file> \
  --upload-landing \
  --wait
```

This:
1. Uploads source files to `/Volumes/<catalog>/<schema>/landing/<landing_path>/`
2. Submits a serverless job to run raw→standard ingestion
3. Waits for completion

### Step 4: Run dbt curation

Use `scripts/run_curation_dbt.py`:

```bash
python skills/source-aligned/scripts/run_curation_dbt.py \
  --model-name <model> \
  --select +<model>_v4
```

**The runner automatically:**
- Patches schemas to use `DATABRICKS_DEFAULT_SCHEMA` (not `cspn_work2_*` or `cspn_fndn2_*`)
- Injects surrogate key columns into `generate_surrogate_key_v3()` calls
- Removes EMR-only hooks (`vacuum`, `cspn_commit_checkpoints`)

### Why NOT use the local adapter directly?

`scripts/databricks_local_ingest.py` with local paths **only works** when:
- You're running inside Databricks (notebook/job), or
- You're using `--use-databricks-sdk` to upload via API

It **fails** if you try to `mkdir` a `/Volumes/...` path locally—that's a Databricks-managed path, not a local filesystem.

**Default to serverless** for Databricks execution unless the user explicitly requests local Spark.
---

## Branch Creation & Push

After artifacts are generated and validated (optionally executed in Databricks), create feature branches in target repos.

### Dual Repository Setup

Keep **reference repos** pristine (always on main) and use **working repos** for branch creation:

| Purpose | Location | Usage |
|---------|----------|-------|
| Reference | `workspace/reference/repos/` | Pattern extraction, reading code, stays on main |
| Working | `workspace/working/repos/` | Branch creation, commits, pushes |

The script auto-clones working repos if they don't exist.

### Batch Mode

For processing many files (up to 300+), use a **single branch** for all configs. Branch names auto-generate with timestamps if not provided:

```bash
# Auto-generated branch name: feature/blmbrg-ingestion-20250120-143022
python skills/source-aligned/scripts/prepare_branch.py \
  --artifact-dir workspace/generated/source-aligned/govt_* \
  --repo pipelines \
  --process-domain blmbrg
```

### System of Record → dc_tag Mapping

The **System of Record** (`process_domain`) identifies the source system. The **dc_tag** determines the folder structure in `caspian-im-foundation`.

| System of Record (`process_domain`) | dc_tag | Notes |
|-------------------------------------|--------|-------|
| `blmbrg` | `blmbrg` | Bloomberg — same for both |
| `rdm` | `ref` | Reference Data Management → reference data |
| `moodys` | `rat` | Moody's → ratings |
| `refinitiv` | `ref` | Refinitiv → reference data |
| `factset` | `fds` | FactSet |
| `msci` | `msci` | MSCI — same for both |
| `rapid` | `raem` | RAPID → RA Equity Models |
| `comet` | `mor` | COMET → Mortgage |

If the system of record is not in this table, **ask the user** for the appropriate dc_tag.

### Repository Destinations

| Artifact Type | Repository | Destination Path |
|---------------|------------|------------------|
| Ingestion (`*.yml`, `pipeline.py`, `dq.yml`) | `caspian-pipelines` | `dags/ingestion/<process_domain>/<process_name>/` |
| Curation EMR (dbt models) | `caspian-im-foundation` | `models/<dc_tag>/<table_name>_f/` |
| Curation Databricks | **TBD** | Structure not finalized |

### Using `scripts/prepare_branch.py`

```bash
# Auto-generate branch with timestamp (recommended)
python skills/source-aligned/scripts/prepare_branch.py \
  --artifact-dir workspace/generated/source-aligned/govt_* \
  --repo pipelines \
  --process-domain blmbrg
# -> creates: feature/blmbrg-ingestion-20250120-143022

# Explicit branch name with timestamp
python skills/source-aligned/scripts/prepare_branch.py \
  --artifact-dir workspace/generated/source-aligned/govt_* \
  --repo pipelines \
  --process-domain blmbrg \
  --branch feature/blmbrg-govt-batch-20250120-143022

# Curation batch
python skills/source-aligned/scripts/prepare_branch.py \
  --artifact-dir workspace/generated/source-aligned/govt_* \
  --repo im-foundation \
  --dc-tag blmbrg
# -> creates: feature/blmbrg-curation-20250120-143022

# Dry run to preview
python skills/source-aligned/scripts/prepare_branch.py \
  --artifact-dir workspace/generated/source-aligned/govt_* \
  --repo pipelines \
  --process-domain blmbrg \
  --dry-run
```

**Options:**
- `--dry-run`: Preview without making changes
- `--commit-message`: Custom commit message (default: auto-generated)

### Workflow

1. **Dry-run** — Preview changes with `--dry-run`
2. **Confirm with user** — Show branch name and file count
3. **Create branch, commit, push** — Script handles git operations to working repo
4. **User creates PR manually** — Script outputs PR URL

### Safety Checks

The script:
- Uses separate working repos (doesn't touch reference repos)
- Auto-clones working repo if not present
- Stashes uncommitted changes if working tree is dirty
- Fetches latest from origin before creating branch
- Uses `--force-with-lease` for safe push

### Databricks Curation — TBD

Databricks curation branch creation is **not yet implemented**. The `curation-databricks/` artifacts are generated but the target repo structure is pending finalization.

See `prompts/branch_creation.md` for detailed mapping and commit message templates.

## Post-completion: Wiki Update

> After completing this skill, the `domain-wiki` skill handles wiki updates in `docs/wiki/`. See *(external plugin — not bundled in this repo)*.
