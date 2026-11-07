---
name: write-dbt-source
description: |
  Render a dbt sources YAML file at
  `data-products/{domain}/datasets/{product}/dbt/{layer}/_{layer}__sources.yml`
  declaring Unity Catalog external source tables. Each table gets a
  `loaded_at_field` placeholder and a `freshness` block. Compliance:
  external tables only (SQL-DBSQL-005); snake_case source / layer
  names (PY-NAMING-*); catalog defaults to
  `specs/product.yaml meta.uc_catalog` when present, otherwise the
  product `domain`.
  Trigger phrases: "write a dbt source", "scaffold a dbt sources yml",
  "declare a dbt source", "author dbt sources".
allowed-tools: Read Bash Write
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  dependencies:
    - setup-dbt-project
    - register-data-contract
  consumes:
    - data-contract
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    - SQL-DBSQL-005
    - PY-NAMING-*
---

# write-dbt-source

Render a SQL-DBSQL-005 compliant dbt sources YAML for a data product.

## When to use

A domain team adds a new upstream system (Salesforce, Fivetran feed,
Kafka landing zone) and needs a dbt `sources` declaration scaffolded
against the Catalyst SQL-DBSQL-005 rule (external tables only) without
hand-rolling the YAML.

## Inputs

CLI flags:

- `--product` (required) — path to `data-products/{domain}/datasets/{product}/`.
- `--source-name` (required) — snake_case source identifier, e.g. `salesforce`.
- `--layer` (optional) — dbt model layer; default `staging`.
- `--catalog` (optional) — Unity Catalog catalog. Defaults to
  `specs/product.yaml meta.uc_catalog`; falls back to the product
  `domain` when meta is absent.
- `--schema` (required) — Unity Catalog schema containing the source
  tables.
- `--tables` (required, repeatable) — table names to declare. Pass
  the flag multiple times to add additional tables.

## Outputs

- `<product>/dbt/<layer>/_<layer>__sources.yml` — single YAML
  file with `version: 2` and a `sources:` block listing every table
  with `loaded_at_field` and `freshness`.

## Standards

- `SQL-DBSQL-005` — sources are declared as Unity Catalog external
  tables via the `external.location` field; the file is documented as
  such in its description.
- `PY-NAMING-*` — `--source-name` and `--layer` are validated as
  snake_case (lowercase letters, digits, underscores; must start with
  a letter).

## Loaded by

- `authoring-dbt-on-dbsql` — document-tier reasoning for SQL-DBSQL-*
  rules, including the source declaration pattern.

## Procedure

1. Load `<product>/specs/product.yaml` (`domain`, `product`, `owner`).
   Missing file → exit 2.
2. Validate `--source-name` and `--layer` against snake_case.
3. Resolve catalog from `--catalog`, else `meta.uc_catalog`, else
   `domain`.
4. Render `templates/sources.yml.tmpl` with the table list, each table
   getting an `external.location` placeholder, `loaded_at_field`, and
   a `freshness` block.
5. Write the file at
   `<product>/dbt/<layer>/_<layer>__sources.yml`, creating parent
   directories. Reruns overwrite cleanly.
6. Print the written path and the rule IDs satisfied.

## Failure modes

- Missing `specs/product.yaml` → exit 2.
- Non-snake_case `--source-name` or `--layer` → exit 2.
- Missing required `--schema` or `--tables` → argparse error (exit 2).
