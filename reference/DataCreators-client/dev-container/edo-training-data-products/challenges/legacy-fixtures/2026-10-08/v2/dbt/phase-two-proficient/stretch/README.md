# dbt: optional stretch selection

**Optional small-fixture follow-up.** The assigned course route is the supplied Portfolio Analytics pipeline on dbt-databricks/Astro. This preserved fixture supports separate further practice and its original command contract; it is not a second mandatory assignment.

Legacy Phase2supportingmodels, returns, adapter-specificOPTIMIZE/ZORDER, and new-mart exercises remain available under v1/02-dbt-pipeline (each 30–90 minutes). These require the corresponding prepared baseline; actual adapter operations need connected verification.

These routes are separate from core completion. Record timing exceptions rather than shortening an exercise during the audit. Instructor review should select one follow-up based on the learner goal and available environment.

## Full legacy advanced reference

The following is the preserved legacy advanced route. Its workspace/commands target **v1**; do not run it against the v2 workspace. Core-equivalent topics are retained here for complete teaching coverage, not additional core assignments.

## Phase 2: Intermediate, Marts, Tests & Docs

Phase 1 left you with a running baseline: sources declared with freshness, five staging models cleaned and typed, the staging layer built green on Databricks. That was setup. Phase 2 is the build proper. Here you write the **intermediate** joins, the two **curated marts**, the **generic and singular tests** that enforce the contract, generate the **docs and lineage graph**, wire the Databricks `OPTIMIZE` performance post-hook, and finish with a capstone that adds a new mart end to end.

Every challenge is self-contained. Each defines the dbt or SQL idea it uses before you apply it, so you are never assumed to have met it before. The shape is always:

- **Concept** — the idea, in plain English.
- **Goal** — the business outcome in one line.
- **Authoring task** — exactly what you write, and into which stub file.
- **How to check** — a command to run, or an observable result.

Write your own answer first; a worked **Solution** follows each challenge for you to compare against. Budget roughly ~10 min per challenge — a pacing target, not a deadline. Work the challenges in order: they build on each other, and Challenge 10 ties the marts together into a new end-to-end deliverable.

---

## Phase 2 — Challenge 1: The enrichment join — `int_holdings_enriched`

**Concept.** The **intermediate** layer is where joins live; staging stayed 1:1 with its sources precisely so this layer can combine them without re-cleaning. `int_holdings_enriched` joins the cleaned holdings to prices and FX so each position carries a base-currency market value. The key move is the currency conversion: a holding is valued in its local currency, and to roll funds up you need a common base. `mv_base_ccy = mv_local_ccy * coalesce(fx_rate, 1.0)`. The FX feed ships a `GBP → GBP` rate of `1.0` alongside the `USD → GBP` and `EUR → GBP` rates, so a GBP holding converts through a real matched row; the `coalesce` is the safety net for the other case — a left join that finds **no** rate for that currency and date returns `null`, and multiplying by `null` would silently wipe the value out. Defaulting to `1.0` keeps the holding at its local value instead of losing it. The output grain is unchanged from `stg_holdings`: one row per (fund, date, instrument).

**Goal.** One intermediate model that values every holding in the GBP base currency, ready for the marts to aggregate.

**Authoring task.** Complete `dbt/models/intermediate/int_holdings_enriched.sql`. Read `ref('stg_holdings')`, `ref('stg_prices')`, and `ref('stg_fx_rates')`. Left join prices on `(instrument_id, date)` and FX on `(local_ccy → GBP, date)`. Select the holding columns plus `close_price`, `fx_rate_to_base`, and the computed `mv_base_ccy`. Keep the grain at (fund, date, instrument) — left joins, so a holding with no price or FX row still appears.

**How to check.**

```bash
dbt build --select int_holdings_enriched
dbt show --select int_holdings_enriched --limit 10
```

Every row should carry an `mv_base_ccy`. All eight bundled holdings are quoted in GBP, so each one matches the `GBP → GBP` rate of `1.0` and its `mv_base_ccy` equals its `mv_local_ccy` — that equality is the check that the join worked, not a sign it was skipped. To see a rate other than `1.0` actually bite, use the optional variation below. No row should be dropped — the count matches `stg_holdings`.

Docs: dbt `ref()`: <https://docs.getdbt.com/reference/dbt-jinja-functions/ref>.

**Try a variation (optional).** The FX feed already carries `USD → GBP` at `0.78`, but no bundled holding is quoted in USD, so that rate never gets used. Prove the conversion works by running a one-off query that re-points a holding at USD — no file edits, nothing to undo:

```bash
dbt show --inline "select mv_local_ccy, mv_local_ccy * (select fx_rate from {{ ref('stg_fx_rates') }} where from_ccy = 'USD' and rate_date = '2026-05-20') as mv_if_usd from {{ ref('stg_holdings') }} where position_date = '2026-05-20'" --limit 5
```

`mv_if_usd` comes back at 78% of `mv_local_ccy` — the same arithmetic `int_holdings_enriched` performs, now with a rate that is not `1.0`.

Worked answer 1 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

## Phase 2 — Challenge 2: The two supporting intermediate models

**Concept.** Not every intermediate model is a big join. The other two are small, focused re-shapes that the marts need. `int_fund_attributes` selects the **active** funds and their reporting attributes — filtering to `is_active = true` once here means no mart has to remember that filter. `int_positions_dated` rolls cash and accrued interest into one `cash_plus_accrued` figure per (fund, day). Each model does one job, named in its filename, so the marts read a clean, purpose-built input rather than re-deriving it.

**Goal.** Two ready-to-join intermediate models: one of active funds, one of cash per fund-day.

**Authoring task.** Complete two stubs. In `dbt/models/intermediate/int_fund_attributes.sql`, select `fund_id`, `fund_name`, `inception_date`, `base_ccy`, `strategy_code` from `ref('stg_funds')` where `is_active = true`. In `dbt/models/intermediate/int_positions_dated.sql`, select `fund_id`, `position_date`, `local_ccy`, and `cash_balance + accrued_interest as cash_plus_accrued` from `ref('stg_positions')`.

**How to check.**

```bash
dbt build --select int_fund_attributes int_positions_dated --indirect-selection=cautious
dbt show --select int_fund_attributes --limit 10 --indirect-selection=cautious
```

`int_fund_attributes` should return only active funds. In the bundled raw fund master all four rows are active, so all four appear; the filter is still intentional and would exclude inactive fixture rows such as `PEF-LEGACY-X` from `seed_funds`. `int_positions_dated` returns one row per (fund, day) with a single `cash_plus_accrued` column.

**Why `--indirect-selection=cautious` here.** When you select a model, dbt also picks up the tests attached to it — that is *indirect selection*, and its default mode (`eager`) pulls in a test as soon as **any one** of the test's inputs is selected. The shipped `models/marts/schema.yml` declares a `relationships` test that checks `fct_portfolio_returns.fund_id` against `int_fund_attributes.fund_id`, so that test has **two** inputs. Selecting `int_fund_attributes` is enough for `eager` to run it — but `fct_portfolio_returns` is still the untouched `select 1 as placeholder` stub until Challenge 4, so the test asks for a `fund_id` column that does not exist yet and fails with `UNRESOLVED_COLUMN ... Did you mean [placeholder]`. `cautious` runs a test only when **all** of its inputs are selected, which skips that not-yet-buildable test and leaves you with just the two models you actually wrote. Drop the flag once you finish Challenge 4 — from then on both inputs are real and the test passes on its own.

Docs: indirect selection: <https://docs.getdbt.com/reference/node-selection/test-selection-examples#indirect-selection>.

Docs: dbt SQL models: <https://docs.getdbt.com/docs/build/sql-models>.

Worked answer 2 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

## Phase 2 — Challenge 3: First curated mart — `agg_fund_exposure`

**Concept.** A **mart** is the consumer-facing layer: it trades row-level detail for a report-ready shape and materialises as a table for fast reads. `agg_` is the prefix for a pre-aggregated mart — measures grouped by reporting dimensions. `agg_fund_exposure` rolls the enriched holdings up to one row per (fund, date, strategy), summing base-currency exposure, counting distinct instruments, and isolating the cash-only slice with a `case` inside the `sum`. Compliance reads it for concentration alerts: how much is each fund exposed to, by strategy, and how much of that is cash.

**Goal.** A per-(fund, date, strategy) exposure aggregate compliance can read for concentration.

**Authoring task.** Complete `dbt/models/marts/agg_fund_exposure.sql`. Read `ref('int_holdings_enriched')` and join `ref('int_fund_attributes')` for the `strategy_code`. Group by `(fund_id, position_date, strategy_code)` and produce: `exposure_base_ccy` (sum of `mv_base_ccy`), `instrument_count` (`count(distinct instrument_id)`), and `cash_exposure_base_ccy` (the sum of `mv_base_ccy` only where `instrument_id like 'CASH_%'`).

**How to check.**

```bash
dbt build --select agg_fund_exposure
dbt show --select agg_fund_exposure --limit 10
```

Each row is one (fund, date, strategy). `exposure_base_ccy` should be a positive GBP figure — with the bundled holdings it lands around 0.9–1.5 billion, since each fund holds a single large position — and `instrument_count` a small positive integer. The bundled holdings have no cash-only rows, so `cash_exposure_base_ccy` is `0`; if you add `CASH_<ccy>` holdings, cash exposure should never be larger than total exposure.

Docs: dbt marts: <https://docs.getdbt.com/best-practices/how-we-structure/4-marts>.

Worked answer 3 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

## Phase 2 — Challenge 4: Second curated mart — `fct_portfolio_returns`

**Concept.** `fct_` is the prefix for a **fact** table — one row per event or measurement, at a fine grain. `fct_portfolio_returns` is the published daily-grain fact: one row per (fund, date, instrument), carrying the base-ccy MV and a calculated NAV-per-unit. NAV-per-unit is total fund market value divided by units outstanding; here units are synthesised (a real feed ships them), so you roll the per-instrument MV up to a per-fund total in a CTE, divide by units, and join that back to the instrument grain. This is the mart the RM dashboard, compliance, and the client app all read.

**Goal.** A daily-grain fact carrying each position's base-ccy value and the fund's calculated NAV-per-unit.

**Authoring task.** Complete `dbt/models/marts/fct_portfolio_returns.sql`. Read `ref('int_holdings_enriched')` and `ref('int_fund_attributes')`. In a `fund_mv` CTE, `sum(mv_base_ccy)` per (fund, date). In a `with_units` CTE, add `100000000.0 as units_outstanding` and keep the total. The final select is at the instrument grain: carry the holding columns through, join `fund_name` from the fund attributes, and compute `calc_nav_per_unit = total_mv_base / units_outstanding`.

**How to check.**

```bash
dbt build --select fct_portfolio_returns
dbt show --select fct_portfolio_returns --limit 10
```

One row per (fund, date, instrument), each with an `mv_base_ccy` and a `calc_nav_per_unit`. The NAV-per-unit should land in a believable range — single digits to low tens (the bundled funds run about 9 to 15), close to the custodian NAVs in `seed_custodian_nav.csv` — not zero and not millions.

Docs: dbt SQL models: <https://docs.getdbt.com/docs/build/sql-models>.

Worked answer 4 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

## Phase 2 — Challenge 5: Generic tests on the marts

**Concept.** dbt's four built-in **generic tests** turn your assumptions into executable checks: `not_null` and `unique` for keys, `accepted_values` for a closed set of categories, and `relationships` for referential integrity (every foreign-key value exists in a parent model). You attach them by column in a YAML file next to the model — zero bad rows means pass. On a mart they guard the contract: a `not_null` on a grain column catches a join that dropped a key, a `relationships` test catches an orphaned fund id, an `accepted_values` test catches a new strategy code that slipped in unmapped.

**Goal.** The two marts guarded by generic tests so a broken build fails loudly rather than shipping wrong numbers.

**Authoring task.** The marts' `dbt/models/marts/schema.yml` ships with the test declarations already in place — read it and run it. On `fct_portfolio_returns`: `not_null` on `fund_id`, `position_date`, `instrument_id`, `mv_base_ccy`, plus a `relationships` test from `fund_id` to `ref('int_fund_attributes')`. On `agg_fund_exposure`: `not_null` on `fund_id` and `position_date`, plus an `accepted_values` test on `strategy_code` (`EQ-LC`, `EQ-EM`, `EQ-GC`, `FI-IG`). Confirm you understand each, then run them.

**How to check.**

```bash
dbt test --select fct_portfolio_returns agg_fund_exposure
```

Every attached column produces a test like `not_null_fct_portfolio_returns_fund_id` and `relationships_fct_portfolio_returns_fund_id__...`, all `PASS`. To prove the `accepted_values` test bites, drop `FI-IG` from the list and run `dbt test --no-partial-parse --select agg_fund_exposure` to watch the fixed-income fund fail the test, then restore it.

Docs: generic data tests: <https://docs.getdbt.com/docs/build/data-tests>.

Worked answer 5 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

## Phase 2 — Challenge 6: A singular reconciliation test — NAV within tolerance

**Concept.** A **singular test** is a single hand-written SQL file in `tests/` that fails when its query returns any rows. Unlike a generic test it is not attached to a column — it tests one specific assertion across whatever models it references. The powerful case is **reconciliation**: your calculated number must agree with an independent source. `assert_nav_within_tolerance` compares the `calc_nav_per_unit` your `fct_portfolio_returns` produces against the custodian-reported NAV in `seed_custodian_nav.csv`, and returns a row only when they differ by more than **1 basis point** (1bp = 0.0001 fractional). Because a singular test returning any rows is a failure, this halts the pipeline if the calculated NAV ever drifts from the custodian's.

**Goal.** Prove the calculated NAV-per-unit reconciles to the custodian NAV within 1bp, enforced as a test.

**Authoring task.** Complete `dbt/tests/assert_nav_within_tolerance.sql`. In a `calc` CTE, select `fund_id, position_date, calc_nav_per_unit` from `ref('fct_portfolio_returns')` where it is not null. In a `custodian` CTE, select `fund_id, position_date, nav_per_unit` from `ref('seed_custodian_nav')`. Join them on `(fund_id, position_date)`, compute `variance_bps = (calc - custodian) / custodian * 10000`, and return rows where `abs(variance_bps) > 1.0`.

**How to check.**

```bash
dbt build --select fct_portfolio_returns seed_custodian_nav
dbt test --select assert_nav_within_tolerance
```

The test should PASS (zero rows). To see it fire with the bundled data, temporarily change the final comparison to `>= 0.0` so even zero variance trips it, confirm it FAILS, then set it back to `> 1.0`.

Docs: singular data tests: <https://docs.getdbt.com/docs/build/data-tests>.

Worked answer 6 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

## Phase 2 — Challenge 7: The full build — `dbt build`

**Concept.** `dbt build` runs seed → run → test in dependency order across the whole project. Crucially, if a model's upstream test fails, downstream models are **skipped** — you do not propagate bad data. This is the command CI and scheduled jobs run, and it is your end-to-end proof that the pipeline is whole: seeds loaded, all ten models built, every generic and singular test passing.

**Goal.** One green end-to-end run: seeds, all ten models, every test.

**Authoring task.** Nothing new to write — run the full build and read the summary:

```bash
dbt build
```

Read the final summary line and confirm every resource passed with no errors and no skips.

**How to check.** The summary should end like:

```text
Completed successfully
Done. PASS=N WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=N
```

`N` covers the eight seeds, ten models, and every test. `ERROR=0` and `SKIP=0` together mean nothing failed and nothing was skipped for a failed upstream.

To run the full verified gate: `mise run challenge:verify 02`

Docs: dbt build: <https://docs.getdbt.com/reference/commands/build>.

Worked answer 7 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

## Phase 2 — Challenge 8: Docs and the lineage graph

**Concept.** dbt generates a documentation site from your model and source descriptions plus the DAG it infers from every `ref()` and `source()` call. `dbt docs generate` writes the metadata; `dbt docs serve` serves an interactive site with column docs, the compiled SQL for each model, and a **lineage graph** you can click through. The lineage graph is the payoff of declaring sources and using `ref()` everywhere: it shows, end to end, that `fct_portfolio_returns` is fed by the intermediate holdings, which are fed by the staging models, which read the sources — so you can see exactly what breaks if you change any one of them.

**Goal.** A browsable docs site whose lineage graph shows the full `source → staging → intermediate → marts` DAG.

**Authoring task.** Generate and serve the docs:

```bash
dbt docs generate
dbt docs serve --host 127.0.0.1 --port 8081
```

`dbt docs serve` holds the terminal until you stop it with **Ctrl-C** — open a second terminal if you want to keep working. Two flags matter here and are easy to miss:

- **`--host 127.0.0.1` is required in this devcontainer.** `dbt docs serve` takes its bind address from the `DBT_HOST` environment variable, and this repo sets `DBT_HOST` to your Databricks workspace URL (the dbt *profiles* use it as the warehouse host). Without the flag, dbt tries to bind a local socket to `https://…databricks.com` and dies with `socket.gaierror: [Errno -2] Name or service not known`.
- **Port 8081, not dbt's default 8080.** Challenge 03 runs the Airflow UI on 8080; if Airflow is up, 8080 gives you `OSError: [Errno 98] Address already in use`.

Then, in the served site, find the lineage graph for `fct_portfolio_returns` and
trace it back to the four source tables used by that mart. The separately built
`stg_positions → int_positions_dated` branch is visible in the project graph but
does not feed this mart.

**How to check.** `dbt docs generate` writes `target/manifest.json` and
`target/catalog.json` and prints a "Catalog written" line. In the served site,
the lineage graph for `fct_portfolio_returns` should show it fed by
`int_holdings_enriched` and `int_fund_attributes`, those fed by the staging
models, and those staging models fed by four source tables.

Docs: dbt docs and lineage: <https://docs.getdbt.com/docs/collaborate/documentation>.

Worked answer 8 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

## Phase 2 — Challenge 9: The Databricks performance post-hook — `OPTIMIZE … ZORDER`

**Concept.** A dbt **post-hook** is SQL that runs after a model is built. On Databricks, `OPTIMIZE <table> ZORDER BY (cols)` is a Delta-table optimisation: it compacts small files and co-locates rows by the columns most queries filter on, so reads prune faster. The marts in this project query by `fund_id` and `position_date`, so z-ordering on those two columns speeds up every dashboard and compliance query that filters on a fund or a date. The post-hook is set once at the folder level in `dbt_project.yml`, so every mart inherits it — and because it is a table optimisation, it only makes sense on the mart tables, not the staging views.

**Goal.** Every mart table z-ordered on its query columns so reads prune efficiently.

**Authoring task.** The post-hook ships in `dbt/dbt_project.yml` on the `marts` folder — read it and confirm it runs. Confirm the `marts` block carries `+post-hook: "OPTIMIZE {{ this }} ZORDER BY (fund_id, position_date)"`, then rebuild a mart and watch the `OPTIMIZE` statement run after the table is created.

**How to check.**

```bash
dbt build --select agg_fund_exposure
```

In the dbt run log, after the `OK created sql table model ... agg_fund_exposure` line you should see the post-hook execute the `OPTIMIZE ... ZORDER BY (fund_id, position_date)` statement against that table. Staging models, being views, run no such hook.

**dbt does not print hook SQL to the console** — at the default log level you only see the `OK created sql table model` line, so it looks like nothing ran. The statement is recorded in the debug log. Confirm it with either of these, run from `challenges/v1/02-dbt-pipeline/dbt`:

```bash
grep "ZORDER BY" logs/dbt.log | tail -1
```

```bash
dbt --debug build --select agg_fund_exposure 2>&1 | grep "ZORDER BY"
```

You should see `OPTIMIZE \`training_dev\`.\`training_<username>\`.\`agg_fund_exposure\` ZORDER BY (fund_id, position_date)`.

Docs: dbt hooks: <https://docs.getdbt.com/docs/build/hooks-operations>; Databricks OPTIMIZE/ZORDER: <https://docs.databricks.com/aws/en/delta/data-skipping>.

Worked answer 9 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

## Phase 2 — Challenge 10: Capstone — add a new mart end to end

This is the integrative challenge. Earlier challenges each added one piece; here you compose the pattern into a new deliverable of your own and prove it is correct. You will add a new mart, a test that guards it, and confirm it lands in the lineage graph — the full `model + test + docs` loop you have been building.

**Concept.** A new consumer question arrives: "what is each fund's total base-currency exposure per day, across all strategies?" `agg_fund_exposure` is at (fund, date, strategy) grain — one grain too fine for this. The answer is a new mart, `agg_fund_daily_exposure`, at (fund, date) grain, built by re-aggregating the strategy-level mart up one level. Building it from `agg_fund_exposure` rather than from scratch reuses work and means the new total must reconcile to the strategy-level total — which gives you a natural reconciliation test.

**Goal.** A per-(fund, date) total-exposure mart, tested and visible in lineage, that reconciles to the strategy-level aggregate.

**Authoring task.** Three pieces:

1. Create `dbt/models/marts/agg_fund_daily_exposure.sql`: read `ref('agg_fund_exposure')`, group by `(fund_id, position_date)`, and sum `exposure_base_ccy` into `total_exposure_base_ccy` (plus a `sum(cash_exposure_base_ccy) as total_cash_base_ccy`).
2. Add a `not_null` test on `fund_id` and `position_date` for the new mart in `dbt/models/marts/schema.yml`.
3. Create a singular reconciliation test `dbt/tests/reconcile_daily_exposure.sql` that returns a row when `sum(total_exposure_base_ccy)` from the new mart differs from `sum(exposure_base_ccy)` from `agg_fund_exposure` by more than a small tolerance (`0.01`).

**How to check.**

```bash
dbt build --select agg_fund_daily_exposure
dbt test --select reconcile_daily_exposure
dbt docs generate
```

`agg_fund_daily_exposure` returns one row per (fund, date) with a `total_exposure_base_ccy` that, for a single-strategy fund, equals that fund's strategy-level exposure. `reconcile_daily_exposure` should PASS (zero rows) — that passing test is the integration proof. After `dbt docs generate`, the new mart appears in the lineage graph fed by `agg_fund_exposure`.

Docs: singular tests and marts: <https://docs.getdbt.com/docs/build/data-tests>, <https://docs.getdbt.com/best-practices/how-we-structure/4-marts>.

Worked answer 10 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

## Done

You built the full pipeline: the enrichment join, the two supporting intermediate models, the two curated marts, generic tests on the marts, a singular NAV reconciliation, a green full build, the docs and lineage graph, the Databricks `OPTIMIZE` post-hook, and a new mart of your own with its reconciliation test. That is a complete, tested, documented dbt product running on Databricks.

Run the full verification gate at any time:

```bash
mise run challenge:verify 02
```
