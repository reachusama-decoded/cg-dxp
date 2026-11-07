---
authors: RBLW
state: published
discussion: https://github.com/cg-open-itg/catalyst/pull/95
labels: skills, dbt, databricks-sql, standards
---

# RFD 0013 dbt on Databricks SQL Standards and Skills Suite

## Problem

dbt on Databricks SQL is a primary path for transformation work, but
projects across teams diverge on adapter configuration, materialization
defaults, incremental strategy, table location (managed vs external),
VACUUM policy, and test coverage. Performance findings are ad-hoc.
There is no enumerated standard for what a compliant dbt-on-DBSQL
project looks like, and no skills suite that authors and validates
against that standard.

This RFD records the standards (the `SQL-DBSQL-*`, `SQL-PERF-DBT-*`,
and `SQL-PERF-DBSQL-*` rule categories in RFD 0008) and the dbt
skills suite.

## Background

Catalyst already defines:

- RFD 0003 — repository layout
- RFD 0006 — skill tiers and the production quality bar
- RFD 0008 — engineering standards as enumerated rule IDs, including
  `SQL-*` (general SQL hygiene), `DBX-UC-*` (Unity Catalog), and
  `DBX-SEC-*` (OAuth only)
- RFD 0009 — ODCS data contracts

The transformation runtime is `dbt-databricks` against Databricks
SQL warehouses. The pre-PR-95 dbt skills covered parts of the workflow
but did not bind to enumerated rule IDs and did not produce
performance findings.

## Proposal

### Standards: three rule categories

Canonical homes in RFD 0008:

- `rfd/0008/sql/dbsql.md` — nine `SQL-DBSQL-*` rules covering adapter
  config, materializations, location, and lifecycle.
- `rfd/0008/sql/perf-dbt.md` — `SQL-PERF-DBT-*` performance rules
  covering project structure (model layering, test selection, run
  ergonomics).
- `rfd/0008/sql/perf-dbsql.md` — `SQL-PERF-DBSQL-*` warehouse-side
  query performance rules.

Key `SQL-DBSQL-*` requirements:

| ID | Rule |
|---|---|
| SQL-DBSQL-001 | `dbt-databricks` adapter with `auth_type: oauth` (cross-ref DBX-SEC-002) |
| SQL-DBSQL-002 | `+materialized` default declared per layer in `dbt_project.yml` |
| SQL-DBSQL-003 | Incrementals use merge strategy with `unique_key` |
| SQL-DBSQL-004 | Sources declared with `loaded_at_field` and freshness thresholds |
| SQL-DBSQL-005 | External tables only (cross-ref DBX-UC-003) |
| SQL-DBSQL-006 | Test coverage minimum: `not_null` and `unique` on declared primary keys |
| SQL-DBSQL-007 | Catalog and schema set per environment, never hardcoded in models |
| SQL-DBSQL-008 | No PATs in `profiles.yml`; OAuth M2M only |
| SQL-DBSQL-009 | Standard VACUUM `RETAIN 168 HOURS` for managed lifecycle |

### Skills suite

Authoring:

- **`scaffold-data-product`** — creates a data-product subtree per
  RFD 0003 layout (airflow/, bundle/, dbt/, contract/, specs/).
- **`setup-dbt-project`** — initializes the dbt project for a data
  product, writing `dbt_project.yml`, `profiles.yml`, and the
  standard `compute.yml` reference.
- **`write-dbt-source`** — declares a source against an ODCS contract
  (RFD 0009).
- **`write-dbt-model`** — authors a model conforming to
  `SQL-DBSQL-*`; declares rule coverage in metadata.
- **`register-data-contract`** — creates or updates the ODCS contract
  for the data product (binds RFD 0009).

Validation and execution:

- **`run-dbt-on-databricks`** — invokes `dbt run`/`dbt test` against
  the DBSQL target resolved from `promotions.yml`. dbt-side validation
  (`dbt parse` + `sqlfluff`) runs from CI; there is no validate-dbt
  skill in this PR. A skill-form validate-dbt is tracked as follow-up
  (A2) once the parse-time error-surfacing pattern is settled.

Orchestration:

- **`dplc-build`** — drives setup-dbt-project / write-dbt-source /
  write-dbt-model end-to-end for a data product.

Performance:

- **`optimize-dbsql-query`** — findings against `SQL-PERF-DBSQL-*`.

The optimize skill produces findings (suggestions with rule IDs and
locations); it does not silently mutate models. A counterpart
`optimize-dbt-model` against `SQL-PERF-DBT-*` is a follow-up (A3).

### Authoring vs running split

Authoring skills (`write-*`, `scaffold-*`, `setup-*`) are adaptive.
Execution (`run-dbt-on-databricks`) is deterministic. Optimize skills
are advisory.

### Governance

- Owners: Data Platform (SQL track) and the Skills team.
- Review cadence: quarterly.
- Cross-RFD bindings: 0003, 0006, 0008, 0009.

## Alternatives

**Use SQLMesh instead of dbt.** Rejected: dbt is the existing
investment, the team has the muscle memory, and `dbt-databricks` is
well-supported. Reconsidering the transformation engine is a separate
RFD.

**Allow managed tables for `staging` layer only.** Rejected: same
reason as RFD 0012 — managed tables in any layer break the external-
table assumption that DBX-UC-003 codifies.

**Skip enumerated performance rules; rely on review.** Rejected:
performance findings need to be reproducible and reference-able.
Enumerated rule IDs let `optimize-*` skills emit specific, fixable
findings rather than prose suggestions.

## Impact

- **Transformation authors** — get a rule set and a skills suite
  that produces a compliant dbt project by default.
- **Reviewers** — review against rule IDs, not taste.
- **Platform team (SQL track)** — owns the rule categories and the
  dbt validate/run skills.
- **Existing dbt projects** — comply on next touch; no big-bang
  migration.
- **Migration path** — PR 1 (rule files), PR 2 (skills), PR 3 (this
  RFD).
