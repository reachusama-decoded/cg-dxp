---
name: scaffold-repo-structure
description: |
  Answer "where does file X live?" for a Catalyst data product repo, or
  scaffold the empty directory tree for a new product. Use when a build
  skill (or human) needs the canonical layout for `databricks.yml`,
  `dbt_project.yml`, `{dataset}.dag-factory.yml`, etc., or when bootstrapping
  a brand-new data product directory. Owns the authoritative layout
  reference (`references/repo-structure.md`) cited by every build-phase skill.
  Trigger phrases: "where does file X live in a Catalyst data product repo",
  "what's the path for the dbt project", "scaffold the repo structure",
  "set up data product repo layout", "create the data product directory tree",
  "where does databricks.yml go".
allowed-tools: Read Bash Write
metadata:
  tier: capability
  lifecycle-phase: cross-cutting
  dependencies: []
  consumes: []
  standards: []
  shared-components:
    core: []
    platforms: [databricks, airflow]
---

# Scaffold Repo Structure

Owns the canonical data product repo layout (see `references/repo-structure.md`).
Other build-phase skills cite that reference for path resolution. The skill
itself can also emit the empty directory tree on request — but the layout
document is the load-bearing artifact.

## When to invoke

- **Greenfield**: a team is starting a new data product repo and wants the
  Catalyst-standard directory tree scaffolded. The skill emits empty
  `data_products/<product>/` + `data_products/<product>/datasets/<dataset>/`
  + the per-dataset subdirectories per the canonical layout.
- **Lookup**: any skill or human asks "where does file X live in a Catalyst
  data product repo?" — answer is in `references/repo-structure.md`.

## How other skills consume this

| Skill | What it uses |
|---|---|
| `/setup-dbt-project` | Path conventions for `dbt_project.yml`, `dbt_profiles/`, `variables/`, `shared/` |
| `/setup-databricks-asset-bundle` | Path conventions for `databricks.yml`, `datasets/<dataset>/bundle/<dataset>.job.yml`, `variables/` |
| `/configure-sql-warehouse` | Path convention for the compute DAB (`<scope>-compute.databricks.yml`) |
| `/setup-monitoring-and-logging` | UC Volume path conventions for log destinations |
| `/generate-dag` | Path conventions for `datasets/<dataset>/airflow/<dataset>.dag-factory.yml` and shared `airflow/` |

Skills cite this reference the same way `/setup-dbt-project` cites
`skills/dbt-best-practices/references/catalog-architecture.md`.

## Steps (when invoked to scaffold)

1. Ask for `<product-name>` and one or more `<dataset-name>` values.
2. Confirm target directory (defaults to `data_products/<product-name>/`).
3. Refuse to overwrite an existing directory unless `--force` is supplied.
4. Emit the empty directory tree per `references/repo-structure.md`:
   - `data_products/<product>/` (with `databricks.yml`, `dbt_project.yml`,
     `dbt_profiles/`, `variables/`, `shared/`, `init_scripts/`, `python/<pkg>/`
     as placeholders or empty)
   - For each dataset: `datasets/<dataset>/{contract,dbt,runtime,bundle,airflow}/`
   - Note: the dbt wrapper (`dbt_wrapper.py`) lives at the **repo root**, not
     under `python/<pkg>/`. `/write-dbt-wrapper` owns that file.
5. Add a top-level `.catalyst-build.yml` stub (consumed by Phase 4 skills).
6. Report the tree that was created.

## Steps (when invoked to look up a path)

Read `references/repo-structure.md` and quote the relevant entry. Don't
guess from memory — the reference is authoritative.

## What this skill does NOT do

- Does NOT scaffold dbt project content (that's `/setup-dbt-project`).
- Does NOT emit `databricks.yml` content (that's `/setup-databricks-asset-bundle`).
- Does NOT scaffold dataset-specific files (contract, dbt models, DAGs) — those
  belong to their respective skills.
- Does NOT enforce the layout retroactively. Lift-and-shift detection is each
  consuming skill's job.
