# Bundle root — `databricks.yml`

The product-level bundle file. One per data product (DBX-BUNDLE-002).
Lives at `data_products/<product>/databricks.yml`.

## Required sections

```
bundle:        # name + cli version
include:       # globs + variable files
sync:          # paths shipped to workspace + exclusions
targets:       # per-env host, root_path, variable overrides
```

## `bundle.name`

Matches the data product name (e.g. `bloomberg`, `shared_ref`). This is
load-bearing — `${bundle.name}` appears throughout `root_path`,
checkpoint references, and downstream skill compose. Don't decorate it
with a domain prefix unless the team agrees on a `<domain>_<product>`
convention org-wide.

## `include` globs

Three categories pulled in:

| Glob | Purpose |
|---|---|
| `datasets/**/bundle/*.yml` | Auto-discover per-dataset job YAMLs. Adding a dataset = adding `datasets/<new>/bundle/<new>.job.yml`; the bundle picks it up without an edit here. |
| `variables/variables.yml` | Variable declarations (defaults skew dev). |
| `variables/clusters.yml` | Complex `small_cluster` / `dqf_cluster` declarations referenced by per-dataset jobs. |

Per-target `include:` is **not** supported by the DAB schema
(`config.Target.additionalProperties: false`; `include` is root-only).
Env-specific values live inline in each `targets.<env>.variables:` block.
`variables_dev.yml` / `variables_sqa.yml` / `variables_prd.yml` are still
emitted as scaffolding for the real environments (and serve as a reference
mirror of each env's values) but are not loaded by the bundle at deploy
time — see `targets-matrix.md`.

## `sync` paths

The bundle ships more than the YAML. The real repo includes:

```
- .                              # the product directory itself
- ../../dbt_wrapper.py            # repo-root wrapper invoked by spark_python_task
- ../../shared                    # cross-product macros, caspian helpers
- ./dbt_profiles                  # dbt connection profiles
- ./dbt_project.yml               # dbt project config
- ./packages.yml                  # dbt packages manifest
- ./requirements.txt              # Python deps for the wrapper
- ./init_scripts                  # cluster init scripts
- ./dbt_packages                  # vendored dbt packages
- ../.blueprints/src              # blueprint helper modules (cross-product)
```

`exclude` keeps non-deployables out: `**/airflow/**` (DAG YAMLs are loaded
by Airflow, not Databricks), `**/contract/**` (ODCS contracts ship
elsewhere).

## Targets

The skill emits seven targets:

| Target | Mode | Purpose |
|---|---|---|
| `local` | development | Per-user dev space; `default: true` for `databricks bundle deploy` with no `--target`. Authors iterate here and only deploy to `dev` when they need to share. |
| `dev` | (default) | Shared dev environment |
| `sqa` | (default) | System QA |
| `prd` | production | Production |
| `dev_dr` / `sqa_dr` / `prd_dr` | mirror of base target | DR-region deploys |

Each target's `variables:` block carries the full set of env-specific
overrides (kafka, secrets, brokers, catalog/schema, cluster IDs). The
matching `variables_<env>.yml` file (for `dev` / `sqa` / `prd`) mirrors
the same values as a reference artifact but isn't loaded by the bundle.

### Adding a new target

1. Add a target block in `databricks.yml` with `workspace.host` +
   `root_path` + a `variables:` block of per-target overrides.
2. (Optional, for real environments) Add a matching `variables_<env>.yml`
   scaffold under `variables/`.
3. Validate: `databricks bundle validate --target <env>`.

### Catalyst-version bump rule

Each emitted file carries a `# Catalyst-version: N` header. Bump `N`
whenever the emitted layout or include topology changes shape (not for
substantive variable adds — those are caught by the structural canary
test). Header is integer-only; semver-style `2.1` is rejected by
`refresh_detect.py` on purpose. All template files currently carry
`# Catalyst-version: 2 (per-product / datasets-bundle layout)`.

## What this template does *not* own

- Per-dataset job definitions (see `per-dataset-jobs.md`)
- Cluster shapes (see `variables-layout.md` / `clusters.yml`)
- DQ jobs (see `dq-jobs.md`)
- Deploy mechanics (handled by `databricks bundle deploy` from CI, not
  this skill)
