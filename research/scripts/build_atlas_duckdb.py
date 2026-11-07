#!/usr/bin/env python3
"""Port the v1 04-atlas-capstone solution (data_products/atlas_elt) to dbt-duckdb so the
instructor can build the expected results locally. Writes courseware/day5-capstone/support/atlas_duckdb/."""
import pathlib, shutil, textwrap
ROOT = pathlib.Path(__file__).resolve().parents[2]
CLIENT = ROOT / "reference/DataCreators-client/dev-container/edo-training-data-products"
SOL = CLIENT / "challenges/v1/04-atlas-capstone/solution"
PROD = CLIENT / "data_products/atlas_elt"
DST = ROOT / "courseware/day5-capstone/support/atlas_duckdb"
if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SOL / "datasets", DST / "datasets")
shutil.copy(PROD / "datasets/sources.yml", DST / "datasets/sources.yml")
shutil.copytree(PROD / "seeds", DST / "seeds")
shutil.copytree(PROD / "tests", DST / "tests")
shutil.copytree(PROD / "shared/macros", DST / "shared/macros")
shutil.copytree(PROD / "shared/snapshots", DST / "shared/snapshots")
for p in DST.rglob(".gitkeep"):
    p.unlink()
(DST / "macros").mkdir()

def w(rel, text):
    p = DST / rel; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text).lstrip("\n"))

w("dbt_project.yml", """
    # Atlas ELT — instructor copy of the capstone solution on DuckDB. Same model names,
    # folders and alignment tags as data_products/atlas_elt, minus the Databricks bundle,
    # the shared Caspian package and the Volume target path.
    name: 'atlas_elt'
    version: '1.0.0'
    config-version: 2
    profile: 'atlas_elt'

    model-paths: ["datasets"]
    test-paths: ["tests"]
    seed-paths: ["seeds"]
    macro-paths: ["macros", "shared/macros"]
    snapshot-paths: ["shared/snapshots"]
    target-path: "target"
    clean-targets: ["target", "dbt_packages"]

    models:
      atlas_elt:
        +materialized: view
        # Alignment tags by layer folder, as in the learners' project:
        #   dbt run --select tag:source-aligned | tag:domain-aligned | tag:consumer-aligned
        advisors:
          dbt:
            staging:     {+tags: ["source-aligned"]}
            integration: {+tags: ["domain-aligned"]}
        clients:
          dbt:
            staging:     {+tags: ["source-aligned"]}
            integration: {+tags: ["domain-aligned"]}
        fund_holdings:
          dbt:
            staging:     {+tags: ["source-aligned"]}
            integration: {+tags: ["domain-aligned"]}
        fund_nav:
          dbt:
            prepared:    {+tags: ["consumer-aligned"]}
        funds:
          dbt:
            staging:     {+tags: ["source-aligned"]}
            integration: {+tags: ["domain-aligned"]}
        instruments:
          dbt:
            staging:     {+tags: ["source-aligned"]}
            integration: {+tags: ["domain-aligned"]}
        market_daily:
          dbt:
            integration: {+tags: ["domain-aligned"]}
            prepared:
              +tags: ["consumer-aligned"]
              ts_daily_market_incremental:
                # DuckDB: make the re-run of a day replace rather than append.
                +incremental_strategy: delete+insert
        portfolio_perf:
          dbt:
            prepared:    {+tags: ["consumer-aligned"]}
        portfolios:
          dbt:
            staging:     {+tags: ["source-aligned"]}
            integration: {+tags: ["domain-aligned"]}
        segment_aum:
          dbt:
            prepared:    {+tags: ["consumer-aligned"]}
        trades:
          dbt:
            staging:     {+tags: ["source-aligned"]}
            integration: {+tags: ["domain-aligned"]}

    # Seeds land in the target schema, where datasets/sources.yml points. (The learners'
    # project routes them through a Caspian schema macro; one schema is the same idea.)
    seeds:
      atlas_elt:
        +quote_columns: false
    """)

w("profiles.yml", """
    atlas_elt:
      target: local
      outputs:
        local:
          type: duckdb
          path: "{{ env_var('ATLAS_DUCKDB_PATH', 'warehouse/training_dev.duckdb') }}"
          schema: "{{ env_var('ATLAS_SCHEMA', 'training_demo') }}"
          threads: 4
    """)

src = DST / "datasets/sources.yml"
src.write_text(src.read_text().replace(
    'loaded_at_field: "cast(timestamp_seconds(ts) as timestamp)"',
    'loaded_at_field: "to_timestamp(ts)"  # DuckDB spelling of Spark\'s timestamp_seconds(ts)'))

w(".gitignore", "target/\ndbt_packages/\nlogs/\nwarehouse/\n")
w("build.sh", """
    #!/usr/bin/env bash
    # Build the whole Atlas solution on DuckDB, layer by layer as the capstone guide does.
    set -euo pipefail
    cd "$(dirname "$0")"
    export ATLAS_DUCKDB_PATH="${ATLAS_DUCKDB_PATH:-$PWD/warehouse/training_dev.duckdb}"
    export ATLAS_SCHEMA="${ATLAS_SCHEMA:-training_demo}"
    mkdir -p warehouse
    step() { printf '\\n\\033[1;34m== %s ==\\033[0m\\n' "$*"; }
    step "debug"                         ; dbt debug
    step "seed the seven Atlas extracts" ; dbt seed --full-refresh
    step "source-aligned layer"          ; dbt run --select tag:source-aligned
    step "domain-aligned layer"          ; dbt run --select tag:domain-aligned
    step "consumer-aligned layer"        ; dbt run --select tag:consumer-aligned
    step "all tests"                     ; dbt test
    step "snapshot (Phase 2, C11)"       ; dbt snapshot
    step "incremental twin, second run (Phase 2, C10)"; dbt run --select ts_daily_market_incremental
    step "docs"                          ; dbt docs generate
    step "done"
    """)
print("written", DST)
