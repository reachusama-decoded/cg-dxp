---
name: scaffold-data-product
description: |
  Scaffold a data-product subtree under `data-products/{domain}/datasets/{product}/`
  per RFD 0003: airflow/, bundle/, dbt/, contract/, specs/ with placeholder
  README.md, databricks.yml stub, dbt_project.yml stub, and empty contract
  directory. Enforces lowercase-snake-case naming on domain and product.
  Trigger phrases: "scaffold a data product", "create dataset directory",
  "bootstrap data product", "initialize data product layout".
allowed-tools: Read Bash Write
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: []
  standards:
    - PY-NAMING-*
    - SQL-NAMING-*
    - SQL-MODEL-*
---

# scaffold-data-product

Write a data-product subtree per RFD 0003.

## When to use

- A domain team adds a new dataset (data product) to an existing domain repo.
- An existing data product needs the five RFD 0003 subdirectories created.

## Inputs

- `--domain` (required) -- domain name; lowercase snake_case.
- `--product` (required) -- data product / dataset name; lowercase snake_case.
- `--team` (required) -- owning team alias, written into the README.
- `--target-dir` (default `.`) -- where to write the tree (the domain repo root).
- `--force` (flag) -- regenerate over an existing tree.

## Outputs

```
<target-dir>/data-products/<domain>/datasets/<product>/
├── README.md
├── airflow/                  # empty subdir; created on disk, not tracked by git
├── bundle/databricks.yml      # stub with `bundle: name: <domain>_<product>`
├── dbt/dbt_project.yml        # stub with name + profile = <domain>_<product>
├── contract/                 # empty subdir; created on disk, not tracked by git
└── specs/                    # empty subdir; created on disk, not tracked by git
```

The three otherwise-empty subdirectories (`airflow/`, `contract/`, `specs/`)
are created on disk so the layout is visible, but no `.gitkeep` marker is
emitted — git picks them up naturally when the next skill (`/generate-dag`,
`/data-contract`, etc.) writes its first artifact there.

## Standards

- `PY-NAMING-*` -- enforces snake_case on domain/product so emitted Python
  package names (Airflow DAG ids, dbt model refs) comply.
- `SQL-NAMING-*` -- the dbt model name and DAB bundle name are derived from
  `<domain>_<product>` and inherit naming compliance.
- `SQL-MODEL-*` -- the dbt scaffold (`dbt_project.yml` `name`/`profile`)
  matches the model-naming convention used by `write-dbt-model`.

## Procedure

1. Validate `--domain` and `--product` against `^[a-z][a-z0-9_]*$`; exit on
   uppercase or hyphens with a clear error pointing at PY-NAMING-*.
2. Compute the target subtree under
   `<target-dir>/data-products/<domain>/datasets/<product>/`.
3. If any file in that subtree exists and `--force` is not set, exit
   non-zero and write nothing.
4. Create the five subdirectories and render the three Jinja2 templates
   (`README.md`, `databricks.yml`, `dbt_project.yml`). No `.gitkeep`
   markers — the three otherwise-empty subdirs are present on disk as
   an affordance only.

## Failure modes

- Invalid name (uppercase / hyphen / leading digit) -> exit 2, `ValueError`.
- Tree exists and `--force` not passed -> exit 1, nothing written.
- Template render failure -> exit 1 with the template path.

## Composes

- Chains to `scaffold-domain-repo` once per repo; this skill is invoked once
  per dataset within that repo.
