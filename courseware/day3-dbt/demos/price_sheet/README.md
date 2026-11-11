# price_sheet: dbt from zero (Day 3, section 1 and the 13:00 advanced part)

The smallest useful dbt project, on Day 2's price data and DuckDB. It starts as two raw CSVs in `seeds/`; the Day 3 anchor notebook writes every other file with a `%%writefile` cell and runs the dbt command that uses it, so the room sees each file appear and what dbt does with it.

| Step in the anchor | File the cell writes | Command | What the room sees |
|---|---|---|---|
| 1 The project is a folder | `dbt_project.yml`, `profiles.yml` | `dbt debug` | The two files dbt needs, and a green connection |
| 2 The raw data | none (the seeds are here) | `dbt seed` | 36 price rows, 9 FX rates; `gbp` in lower case; Apple delivered twice on 4 November |
| 3 Source and first model | `models/sources.yml`, `models/stg_prices.sql` | `dbt run` | One view; the compiled SQL beside the Jinja |
| 4 A second model with `ref()` | `models/stg_fx_rates.sql`, `models/prices_usd.sql` | `dbt run` | Three models in graph order; HSBC's dollar price is empty |
| 5 Tests | `models/schema.yml` | `dbt test` | Two tests fail, on the three HSBC rows |
| 6 Fix, then build | `models/stg_prices.sql` (currency cleaned) | `dbt build` | Seeds, models and tests in one command, all green |
| 7 A singular test | `tests/assert_one_price_per_instrument_per_day.sql`, `models/stg_prices.sql` (deduplicated) | `dbt test`, `dbt build` | Red on the Apple re-delivery, then green; 35 rows |
| 8 Docs and lineage | none | `dbt docs generate` | The catalog and the lineage graph from the same files |
| 13:00 A loop | `models/prices_by_ccy.sql` | `dbt show` | Four columns written by a `for` loop |
| 13:00 A macro | `macros/to_usd.sql`, `models/prices_usd.sql` | `dbt build` | The macro call expanded in the compiled SQL |

`bash reset.sh` returns the folder to its starting point (it deletes everything except `seeds/`, this README and `reset.sh`); the notebook's first cell of the section runs it. To serve the docs site: `dbt docs serve --host 127.0.0.1 --port 8082` from this folder.
