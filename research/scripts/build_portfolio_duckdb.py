#!/usr/bin/env python3
"""Port the v1 02-dbt-pipeline solution to a dbt-duckdb project for instructor demos.
Writes courseware/day3-dbt/demos/portfolio_analytics/. Re-runnable (overwrites)."""
import pathlib, shutil, textwrap
ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "reference/DataCreators-client/dev-container/edo-training-data-products/challenges/v1/02-dbt-pipeline"
DST = ROOT / "courseware/day3-dbt/demos/portfolio_analytics"
if DST.exists():
    shutil.rmtree(DST)
(DST / "models").mkdir(parents=True)
# models, tests and seeds come from the verified solution / starter
shutil.copytree(SRC / "solution/models", DST / "models", dirs_exist_ok=True)
shutil.copytree(SRC / "solution/tests", DST / "tests")
shutil.copytree(SRC / "dbt/seeds", DST / "seeds")
shutil.copy(SRC / "dbt/models/sources.yml", DST / "models/sources.yml")
for p in DST.rglob(".gitkeep"):
    p.unlink()
(DST / "macros").mkdir(); (DST / "snapshots").mkdir(); (DST / "tests/generic").mkdir(); (DST / "models/stretch").mkdir()

def w(rel, text):
    p = DST / rel; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text).lstrip("\n"))

w("dbt_project.yml", """
    # Portfolio Analytics — instructor demo copy of challenge 02, running on DuckDB.
    # Same project name, layers, tags and models as the learners' Databricks project, so
    # every command in the challenge README can be shown here with the same output shape.
    name: 'portfolio_analytics_challenge'
    version: '1.0'
    profile: 'portfolio_analytics_challenge'
    config-version: 2

    model-paths: ["models"]
    seed-paths: ["seeds"]
    test-paths: ["tests"]
    macro-paths: ["macros"]
    snapshot-paths: ["snapshots"]
    target-path: "target"
    clean-targets: ["target", "dbt_packages"]

    # Layers are separated by +tags, not +schema, exactly as in the training catalog
    # (one pre-provisioned schema per learner). Select a layer with --select tag:staging.
    models:
      portfolio_analytics_challenge:
        staging:
          +materialized: view
          +tags: ["staging"]
        intermediate:
          +materialized: view
          +tags: ["intermediate"]
        marts:
          +materialized: table
          +tags: ["marts"]
          # On Databricks the learners' project runs `OPTIMIZE {{ this }} ZORDER BY (...)`
          # after each mart. That is a Delta feature, so the macro below emits it only when
          # target.type is databricks and a harmless no-op on DuckDB. Open macros/optimize_mart.sql.
          +post-hook: "{{ optimize_mart(this) }}"
        stretch:
          +tags: ["stretch"]

    # The five *_raw seeds carry an authored May 2026 _extracted_at. Refreshing it to "now"
    # on load is what lets `dbt source freshness` (and Day 4's freshness gate) pass on a
    # fresh seed. The macro uses dbt's cross-database current_timestamp().
    seeds:
      portfolio_analytics_challenge:
        holdings_raw:
          +post-hook: "{{ refresh_extracted_at(this) }}"
        positions_raw:
          +post-hook: "{{ refresh_extracted_at(this) }}"
        prices_raw:
          +post-hook: "{{ refresh_extracted_at(this) }}"
        refdata_raw:
          +post-hook: "{{ refresh_extracted_at(this) }}"
        fx_rates_raw:
          +post-hook: "{{ refresh_extracted_at(this) }}"
    """)

w("profiles.yml", """
    # DuckDB stands in for Databricks. The database name is the file stem (training_dev) and
    # the schema mirrors the learners' training_<username>, so relation names look the same:
    # training_dev.training_demo.stg_holdings. Override with PA_DUCKDB_PATH / PA_SCHEMA.
    portfolio_analytics_challenge:
      target: local
      outputs:
        local:
          type: duckdb
          path: "{{ env_var('PA_DUCKDB_PATH', 'warehouse/training_dev.duckdb') }}"
          schema: "{{ env_var('PA_SCHEMA', 'training_demo') }}"
          threads: 4
    """)

w("macros/optimize_mart.sql", """
    {#- Post-hook for mart tables. Databricks: Delta OPTIMIZE + ZORDER, as in the learners'
        project. Anything else: a no-op statement, so the same project runs on DuckDB. -#}
    {% macro optimize_mart(relation) -%}
      {%- if target.type == 'databricks' -%}
        optimize {{ relation }} zorder by (fund_id, position_date)
      {%- else -%}
        select 1 as optimize_mart_noop_on_{{ target.type }}
      {%- endif -%}
    {%- endmacro %}
    """)

w("macros/refresh_extracted_at.sql", """
    {#- Seed post-hook: stamp the raw feed as extracted "now" so freshness checks pass. -#}
    {% macro refresh_extracted_at(relation) -%}
      update {{ relation }} set _extracted_at = {{ dbt.current_timestamp() }}
    {%- endmacro %}
    """)

w("macros/to_base_ccy.sql", """
    {#- A small reusable macro: convert a local-currency amount with an optional FX rate.
        Used by the stretch model so learners see where a macro earns its place. -#}
    {% macro to_base_ccy(amount_col, rate_col) -%}
      cast(cast({{ amount_col }} as decimal(19, 2)) * coalesce({{ rate_col }}, 1.0) as decimal(18, 2))
    {%- endmacro %}
    """)

w("tests/generic/test_non_negative.sql", """
    {#- Custom generic test: fails on any row where the column is negative.
        Usage in YAML:  tests: [non_negative]  -#}
    {% test non_negative(model, column_name) %}
    select *
    from {{ model }}
    where {{ column_name }} < 0
    {% endtest %}
    """)

w("snapshots/fund_master_snapshot.sql", """
    {% snapshot fund_master_snapshot %}
    {{ config(
        unique_key='fund_cd',
        strategy='check',
        check_cols=['fund_name', 'base_ccy', 'strategy_code', 'is_active']
    ) }}
    -- SCD type 2 history of the fund master: every change to a checked column closes the
    -- current row (dbt_valid_to) and opens a new one. Day 4's bitemporal demo builds on this.
    select * from {{ source('product_ref', 'fund_master_raw') }}
    {% endsnapshot %}
    """)

w("models/stretch/agg_fund_daily_exposure_incremental.sql", """
    -- Stretch: the same (fund, date) rollup as agg_fund_daily_exposure, built incrementally.
    -- First run: full load. Later runs: only dates after the latest already in the table,
    -- replaced with delete+insert on the unique key so a re-delivered day is idempotent.
    {{ config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key=['fund_id', 'position_date']
    ) }}

    with holdings as (
        select * from {{ ref('int_holdings_enriched') }}
    )

    select
        fund_id,
        position_date,
        sum({{ to_base_ccy('mv_local_ccy', 'fx_rate_to_base') }}) as total_exposure_base_ccy,
        count(*)                                                   as positions
    from holdings
    {% if is_incremental() %}
    where position_date > (select coalesce(max(position_date), date '1900-01-01') from {{ this }})
    {% endif %}
    group by 1, 2
    """)

w("models/stretch/stretch.yml", """
    version: 2

    models:
      - name: agg_fund_daily_exposure_incremental
        description: "Incremental twin of agg_fund_daily_exposure (stretch demo)."
        columns:
          - name: fund_id
            tests: [not_null]
          - name: position_date
            tests: [not_null]
          - name: total_exposure_base_ccy
            tests:
              - non_negative

    # A dbt unit test: run the model's SQL on rows you make up, compare with rows you expect.
    # No warehouse data involved, so it checks the transformation logic itself.
    unit_tests:
      - name: stg_holdings_cash_fallback_and_cleaning
        description: "A null ISIN becomes CASH_<ccy>; fund codes are trimmed and upper-cased."
        model: stg_holdings
        given:
          - input: source('custodian', 'holdings_raw')
            rows:
              - {fund_cd: ' pef-large-cap ', pos_dt: '2026-05-20', isin: null, qty: 1, mkt_val_lc: 100.00, ccy_cd: 'gbp', _extracted_at: '2026-05-20 18:00:00'}
              - {fund_cd: 'PEF-LARGE-CAP', pos_dt: null, isin: 'GB00B3M9JJ78', qty: 1, mkt_val_lc: 100.00, ccy_cd: 'GBP', _extracted_at: '2026-05-20 18:00:00'}
        expect:
          rows:
            - {fund_id: 'PEF-LARGE-CAP', instrument_id: 'CASH_GBP', local_ccy: 'GBP'}
    """)

w("models/exposures.yml", """
    version: 2

    # An exposure documents who consumes a mart. It shows up in `dbt docs` lineage and lets
    # `dbt build --select +exposure:compliance_concentration_dashboard` build what a consumer needs.
    exposures:
      - name: compliance_concentration_dashboard
        label: "Compliance concentration dashboard"
        type: dashboard
        maturity: medium
        url: https://dashboards.example.internal/compliance/concentration
        description: "Daily concentration alerts by fund and strategy."
        depends_on:
          - ref('agg_fund_exposure')
          - ref('agg_fund_daily_exposure')
        owner:
          name: Compliance analytics
          email: compliance-analytics@example.internal
    """)

w(".gitignore", """
    target/
    dbt_packages/
    logs/
    warehouse/
    """)

w("demo.sh", """
    #!/usr/bin/env bash
    # End-to-end run of the Day 3 dbt demo on DuckDB. Mirrors the challenge's section order.
    # Usage: bash demo.sh            (full run)      bash demo.sh stretch   (adds the stretch pieces)
    set -euo pipefail
    cd "$(dirname "$0")"
    export PA_DUCKDB_PATH="${PA_DUCKDB_PATH:-$PWD/warehouse/training_dev.duckdb}"
    export PA_SCHEMA="${PA_SCHEMA:-training_demo}"
    mkdir -p warehouse
    step() { printf '\\n\\033[1;34m== %s ==\\033[0m\\n' "$*"; }

    step "S0  dbt debug: profile, connection, project"           ; dbt debug
    step "S1  seed the six raw feeds and two reference seeds"     ; dbt seed --full-refresh
    step "S2  list the models before building anything"          ; dbt ls --resource-type model --exclude tag:stretch
    step "S3  source freshness (5 of 6 tables carry a load field)"; dbt source freshness
    step "S4  build one model and look at it"                    ; dbt build --select stg_holdings; dbt show --select stg_holdings --limit 5
    step "S5-S7 build the whole staging layer by tag"            ; dbt build --select tag:staging
    step "S8  a staging test is just a query that must return no rows"; dbt test --select stg_holdings
    step "C1-C7 full build: intermediate, marts, generic + singular tests"; dbt build --exclude tag:stretch
    step "C8  docs and lineage (open target/index.html)"         ; dbt docs generate
    step "C10 the capstone mart and its reconciliation"          ; dbt show --select agg_fund_daily_exposure --limit 10
    if [[ "${1:-}" == "stretch" ]]; then
      step "X1  snapshot the fund master (SCD2)"                 ; dbt snapshot
      step "X2  incremental mart, run twice"                     ; dbt run --select agg_fund_daily_exposure_incremental; dbt run --select agg_fund_daily_exposure_incremental
      step "X3  custom generic test + unit test"                 ; dbt test --select agg_fund_daily_exposure_incremental stg_holdings,test_type:unit
    fi
    step "done"
    """)

# DuckDB adaptation: DECIMAL(18,2) * DECIMAL(18,8) overflows DuckDB's 64-bit decimal path,
# so the enrichment model widens the market value to DECIMAL(19,2) before multiplying.
# The learners' Databricks SQL is unchanged; the comment in the model explains the difference.
enr = DST / "models/intermediate/int_holdings_enriched.sql"
enr.write_text(enr.read_text().replace(
    "        h.mv_local_ccy * coalesce(f.fx_rate, 1.0)   as mv_base_ccy",
    "        -- DuckDB demo copy: widened to decimal(19,2) so decimal * decimal stays in range.\n"
    "        -- The learners' Databricks version reads: h.mv_local_ccy * coalesce(f.fx_rate, 1.0)\n"
    "        cast(cast(h.mv_local_ccy as decimal(19, 2)) * coalesce(f.fx_rate, 1.0) as decimal(18, 2)) as mv_base_ccy"))
assert "decimal(19, 2)" in enr.read_text(), "patch did not apply"
print("written", DST)
