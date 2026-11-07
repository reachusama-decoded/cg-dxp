# Day 5 support

- `atlas_duckdb/` is the capstone solution (`challenges/v1/04-atlas-capstone/solution` plus the product's seeds, macros, tests and snapshot) as a dbt-duckdb project. `bash build.sh` builds it layer by layer with the same tag selectors the learners use.
- `expected-results.py` writes `expected-results.md` from that build: row counts per model, the advisor leaderboard, segment and region AUM, and the reconciliation totals. Compare a team's Databricks numbers with it.
- The Day 5 anchor notebook embeds the expected results and queries the DuckDB file for live comparisons.

Adaptations from the learners' project: no Databricks Asset Bundle, no shared package, seeds land in the target schema, the incremental twin uses `delete+insert`, and the source freshness field uses DuckDB's `to_timestamp`.
