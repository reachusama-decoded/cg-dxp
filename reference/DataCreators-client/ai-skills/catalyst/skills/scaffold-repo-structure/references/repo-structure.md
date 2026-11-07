# Catalyst Data Product Repo Structure

Canonical reference for the file/directory layout of a Catalyst-shaped data
product repository. Mirrors the operational reference at
`cg-open-itg/edo-ig-data-products`. Cited by every build-phase skill that
emits files into a data product repo.

When a build skill needs to know "where does file X live?" — the answer is
here. Do not duplicate path conventions in skill bodies.

## Top-level layout

A Catalyst data product repo is **multi-product**: one repo can host multiple data products under `data_products/<product>/`. Each product is **self-contained** — its own `databricks.yml`, `dbt_project.yml`, `variables/`, `python/`, etc. Repo-root files are cross-cutting (shared `airflow/` helpers, Python deps, infrastructure).

```
<repo-root>/                                  # multi-product home — matches cg-open-itg/edo-ig-data-products
├── airflow/                                  # shared Airflow helpers (vendored, not pip-installed) — cross-product
│   ├── assets.py                             # Asset registry — /generate-dag
│   ├── callbacks/
│   │   └── on_success_log_databricks_url.py  # /generate-dag
│   └── shared/                               # /generate-dag (astro-blueprints pattern only)
│       ├── databricks_dbt.py
│       └── asset_signal.py
├── base_airflow_settings.yaml                # Astronomer/Airflow workspace settings — cross-product
├── dbt_wrapper.py                            # /write-dbt-wrapper — single shared dbt dispatcher (repo-root; pulled into each product bundle via sync.paths)
├── data_products/                            # one subdirectory per data product
│   └── <product>/                            # the data product root (`<product-root>` in skill bodies)
│       ├── databricks.yml                    # /setup-databricks-asset-bundle — pipeline DAB (per-product)
│       ├── <scope>-compute.databricks.yml    # /configure-sql-warehouse — persistent compute DAB (separate lifecycle)
│       ├── dbt_project.yml                   # /setup-dbt-project — dbt project config (per-product)
│       ├── packages.yml                      # /setup-dbt-project — dbt package deps (NO dbt-project-evaluator runtime)
│       ├── DATABRICKS_RUNTIME_VERSION        # /setup-dbt-project — pinned runtime
│       ├── requirements.txt                  # per-product Python deps (cgrepo-indexed)
│       ├── .copier-answers.yml               # if scaffolded via copier
│       ├── .catalyst-build.yml               # Catalyst state file (mode, patterns, target catalog)
│       ├── .dbtignore                        # /setup-dbt-project
│       ├── dbt_profiles/
│       │   └── profiles.yml                  # /setup-dbt-project — dbt connection profiles
│       ├── variables/
│       │   ├── variables.yml                 # /setup-databricks-asset-bundle — base vars (incl. databricks_job_prefix)
│       │   ├── variables_dev.yml             # per-env overrides
│       │   ├── variables_qa.yml
│       │   ├── variables_sqa.yml
│       │   ├── variables_prd.yml
│       │   ├── variables_prd_dr.yml
│       │   └── clusters.yml                  # /configure-sql-warehouse — t-shirt cluster defs
│       ├── init_scripts/
│       │   └── install_requirements.sh       # /write-dbt-wrapper — cgrepo-aware pip install
│       ├── python/
│       │   └── <pkg-name>/
│       │       ├── __init__.py
│       │       └── main.py                   # per-product Python entry (if any). The dbt wrapper itself lives at the repo root — see `/dbt_wrapper.py` above.
│       ├── shared/                           # /setup-dbt-project — cross-dataset dbt content (per-product)
│       │   ├── macros/
│       │   ├── tests/
│       │   ├── seeds/
│       │   ├── snapshots/
│       │   └── analyses/
│       ├── sources.yml                       # /setup-dbt-project — Unity Catalog source decls
│       └── datasets/                         # one subdirectory per dataset within the product
│           └── <dataset>/
│               ├── contract/
│               │   └── <dataset>.contract.yaml      # /data-contract (Phase 3)
│               ├── dbt/
│               │   ├── <dataset>.sql                # /source-aligned, /domain-aligned, /consumer-aligned
│               │   ├── <dataset>_raw.sql            # staging layer
│               │   └── schema.yml                   # /data-contract → dbt schema/tests
│               ├── runtime/
│               │   ├── notebook.ipynb               # exception pattern; default is jobs
│               │   └── sql_file_task.sql            # exception pattern
│               ├── bundle/
│               │   └── <dataset>.job.yml            # /setup-databricks-asset-bundle — Databricks job
│               └── airflow/
│                   ├── <dataset>.dag-factory.yml    # /generate-dag — Pattern A (default)
│                   ├── <dataset>.dag.yaml           # /generate-dag — Pattern B (astro-blueprints, opt-in)
│                   └── <dataset>.dq.yml             # /generate-dag — DQ checks (RFD 0011 §9)
├── docker-compose.override.yml               # local-dev container overrides
├── Dockerfile                                # local-dev / Astronomer build context
├── mise.lock                                 # mise toolchain lock
├── pytest.ini                                # repo-level pytest config (cross-product)
├── README.md                                 # repo-level README
├── requirements.txt                          # repo-level Python deps (cgrepo-indexed; pulled in by all products)
├── .gitignore                                # repo-level
├── .pre-commit-config.yaml                   # /setup-dbt-project — sqlfluff + secret scan (cross-product)
├── workspace/                                # scratch, NOT shipped to runtime
│   └── dag-proposals/                        # /generate-dag lift-and-shift output
│       └── data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag-factory.yml
└── tests/
    ├── dags/                                 # /generate-dag — emitted structural DAG tests
    │   └── test_<dataset>_dag.py
    └── data_products/                        # /unit-test-report (Phase 4) — dbt unit tests
```

**Mental model.** A repo is the **home for one or more data products**. The repo itself owns shared `airflow/` helpers (used across all products), Python deps, and infra config. Each product under `data_products/<product>/` is otherwise self-contained: its own dbt project, bundle, variables, wrapper, and datasets. Skills that emit per-product files (e.g., `/setup-dbt-project`, `/setup-databricks-asset-bundle`, `/write-dbt-wrapper`) operate within a `<product-root>` = `data_products/<product>/`.

## Path ownership matrix

| Path | Owning skill | When emitted |
|---|---|---|
| `data_products/<product>/databricks.yml` | `/setup-databricks-asset-bundle` | Phase 4 infra setup (per-product) |
| `data_products/<product>/<scope>-compute.databricks.yml` | `/configure-sql-warehouse` | Phase 4 infra setup (per-product) |
| `data_products/<product>/dbt_project.yml`, `packages.yml`, `.dbtignore` | `/setup-dbt-project` | Phase 4 infra setup (per-product) |
| `data_products/<product>/dbt_profiles/profiles.yml` | `/setup-dbt-project` (template) + `/configure-sql-warehouse` (warehouse_id wire-in) | Phase 4 infra setup (per-product) |
| `data_products/<product>/variables/variables_<env>.yml` | `/setup-databricks-asset-bundle` (per-env defs incl. `databricks_job_prefix`) + `/configure-sql-warehouse` (warehouse_id + http_path wire-in) | Phase 4 infra setup (per-product) |
| `data_products/<product>/variables/clusters.yml` | `/configure-sql-warehouse` | Phase 4 infra setup (per-product) |
| `dbt_wrapper.py` (repo root — single shared dispatcher, sync'd into each product bundle via `sync.paths: ../../dbt_wrapper.py`) | `/write-dbt-wrapper` | Phase 4 infra setup (repo-level, shared across all products) |
| `data_products/<product>/init_scripts/install_requirements.sh` | `/write-dbt-wrapper` | Phase 4 infra setup (per-product) |
| `data_products/<product>/shared/macros/`, `shared/tests/`, etc. | `/setup-dbt-project` | Phase 4 infra setup (per-product) |
| `airflow/assets.py`, `airflow/callbacks/*` (repo root) | `/generate-dag` | Phase 4 per-dataset (cross-product helpers) |
| `airflow/shared/*` (repo root, blueprints pattern) | `/generate-dag` (vendored) | Phase 4 per-dataset (Pattern B only) |
| `.pre-commit-config.yaml`, `.sqlfluff` (repo root, cross-product) | `/setup-dbt-project` | Phase 4 infra setup (repo-level) |
| `data_products/<product>/datasets/<dataset>/contract/<dataset>.contract.yaml` | `/data-contract` | Phase 3 design |
| `data_products/<product>/datasets/<dataset>/dbt/*.sql` | `/source-aligned`, `/domain-aligned`, `/consumer-aligned` | Phase 4 model authoring |
| `data_products/<product>/datasets/<dataset>/dbt/schema.yml` | `/data-contract` (template) + `/<*>-aligned` (filling) | Phase 3 → 4 |
| `data_products/<product>/datasets/<dataset>/bundle/<dataset>.job.yml` | `/setup-databricks-asset-bundle` | Phase 4 infra setup |
| `data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag-factory.yml` | `/generate-dag` | Phase 4 per-dataset (Pattern A) |
| `data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag.yaml` | `/generate-dag` | Phase 4 per-dataset (Pattern B) |
| `data_products/<product>/datasets/<dataset>/airflow/<dataset>.dq.yml` | `/generate-dag` | Phase 4 per-dataset |
| `data_products/<product>/datasets/<dataset>/runtime/*` | exception pattern — not default | Phase 4 if explicitly chosen |
| `workspace/dag-proposals/**` | `/generate-dag` (lift-and-shift mode only) | Non-runtime; for manual diff/merge |
| `tests/dags/test_<dataset>_dag.py` | `/generate-dag` (emitted structural test) | Phase 4 per-dataset |

## Naming conventions

- **Product name**: kebab-case, descriptive (e.g., `client-positions`, `asset-reference-data`, `orders`).
- **Dataset name**: snake_case, suffix indicates layer (`_curr` = curated, `_raw` = staging, `_daily` = daily snapshot, etc.).
- **Job key in `<dataset>.job.yml`**: `<dataset>_job` (e.g., `daily_positions_job`).
- **DAG ID**: `<app>__<dataset>` with double-underscore separator. `<app>` is OQ-1 — may include domain prefix.
- **Catalog references**: see `/dbt-best-practices/references/catalog-architecture.md` for SAP/DAP/CAP/Sandbox conventions.

## Non-runtime locations

- `workspace/` — scratch outputs (lift-and-shift proposals, triage reports, etc.). Never shipped to a runtime DAG scanner.
- `tests/` — pytest content. Not picked up by Airflow's DAG scanner.

## Lift-and-shift output path

When `/generate-dag` runs in `lift-and-shift` mode, it emits proposals to:

```
workspace/dag-proposals/data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag-factory.yml
```

This mirrors the canonical runtime layout under the `workspace/` prefix. User
diffs against the original at `data_products/<product>/datasets/<dataset>/airflow/`
and moves files manually when ready. No version/RFD numbers in runtime
artifact filenames.
