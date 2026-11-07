# Rule severity by mode

Same rule list, different per-mode severity. Build skills consult this table to decide whether to enforce, warn, or skip a check.

| RFD 0008 / evaluator rule | Prototype | Production | Lift-and-shift |
|---|---|---|---|
| SQL-NAMING-001 (`stg_` / `int_` / `fct_` / `dim_` prefixes) | advisory | error | warn-and-fix |
| SQL-MODEL-002 (never hardcode table names) | error | error | error |
| SQL-MODEL-004 (schema.yml co-located) | error | error | warn |
| SQL-TEST-001 (`unique` + `not_null` on every PK) | advisory | error | warn-and-fix |
| SQL-TEST-002 (`not_null` + `relationships` on FKs) | advisory | error | warn-and-fix |
| SQL-TEST-003 (`accepted_values` on enums) | skip | warn | skip |
| SQL-INCR-002 (`merge` strategy on Databricks) | error | error | error |
| SQL-INCR-006 (incremental works on `--full-refresh`) | skip | error | warn |
| DBX-DELTA-001 (use Delta format) | error | error | error |
| Evaluator: Hard Coded References | error | error | error |
| Evaluator: Documentation Coverage | skip | required | warn |
| Evaluator: Public-without-contract | skip | error | warn |
| Evaluator: DAG Fanout > N | skip | warn | warn |
| Evaluator: Source Fanout | skip | warn | warn |
| Evaluator: Rejoining of Upstream Concepts | skip | warn | warn |

## Priority order for input signals (artifact → dbt element)

When multiple DPLC artifacts could inform a dbt-element decision, consult in this priority order. See the spec's "Q3 multi-source mapping matrix" for the full list. Highlights:

| dbt element | Primary | Secondary | Fallback |
|---|---|---|---|
| schema.yml column `description` | consumer-use-case-map (consumer vocabulary) | data-contract `Description` | data-profiling sample values |
| Materialization | data-model.md | nfr-specification | profiling row count → dbt-best-practices default |
| `unique_key:` for incremental | data-contract PK + data-model | data-contract PK | profiling (100% unique + 0 nulls) |
| `source.freshness` | data-contract SLA | discover-data observed cadence | skip + warn |
| Test severity | data-contract DQ severity column | requirements-AC criticality | default `warn` |
