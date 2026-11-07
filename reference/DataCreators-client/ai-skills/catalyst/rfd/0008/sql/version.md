# SQL-VERSION: Version

dbt, Databricks Runtime, and SQLFluff version policy.

## SQL-VERSION-001 — dbt Core 1.8+

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory (enforced via `dbt_project.yml` `require-dbt-version`)

**Decision.** All projects use dbt Core 1.8 or later.

**Why.** Unit testing support is a hard dependency (introduced in 1.8).
Earlier versions force back-channel testing of business logic.

**Exception.** None for new projects.

## SQL-VERSION-002 — Databricks Runtime 14.3 LTS+

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Warehouse and cluster configurations target Databricks
Runtime 14.3 LTS or later.

**Why.** Predicate-pushdown improvements, Photon coverage, Unity Catalog
features, and the Delta optimizations Catalyst relies on all assume
14.3+.

## SQL-VERSION-003 — SQLFluff 3.0+

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** SQLFluff 3.0 or later. Earlier versions lack Databricks
dialect support.

### Formatting
