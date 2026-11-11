# dbt: the commands, and how to use them well

One line per command. The flags listed are the ones that matter in practice; `dbt <command> --help` has the rest. Run every `dbt` command from the folder that holds `dbt_project.yml`. In the training repository that is `challenges/v1/02-dbt-pipeline/dbt`, in the dev container's terminal, and the commands run against Databricks. The first part lists the commands by what you are trying to do; the second covers selecting models, the files dbt reads and writes, the Jinja you meet, and the habits that keep a project trustworthy.

# Part 1 — The commands, by what you are trying to do

## Check that dbt is set up

| Command | What it does |
|---|---|
| `dbt --version` | Prints the dbt version and the installed adapter (databricks). The first check when a command is "unknown". |
| `dbt debug` | Finds `dbt_project.yml` and `profiles.yml`, checks both are valid, and opens the connection. "All checks passed" means dbt can reach the warehouse. |
| `dbt debug --config-dir` | Prints where dbt looks for `profiles.yml`. |
| `dbt parse` | Reads every file in the project and reports YAML and Jinja errors, without touching the warehouse. The quickest check after editing YAML. |
| `dbt deps` | Downloads the packages listed in `packages.yml` into `dbt_packages/`. Run it once after cloning, and again when the list changes. |
| `dbt init NAME` | Scaffolds a new, empty project folder and asks for connection details. Not needed in the challenges: the project is already there. |

## Load the raw data

| Command | What it does |
|---|---|
| `dbt seed` | Loads every CSV in `seeds/` into the warehouse as a table. In training, seeds stand in for the feeds that other tools would land. |
| `dbt seed --select NAME` | Loads one seed. |
| `dbt seed --full-refresh` | Drops and recreates the seed tables. Use it after changing a CSV's columns. |
| `dbt source freshness` | For each source with a `loaded_at_field`, checks how old the newest row is against the `warn_after` and `error_after` thresholds. |

## Build models

| Command | What it does |
|---|---|
| `dbt run` | Builds every model: compiles the Jinja, wraps each SELECT in `create view` or `create table`, and runs them in graph order. |
| `dbt run --select MODEL` | Builds one model. See "Choose what runs" below for everything `--select` accepts. |
| `dbt run --full-refresh` | Rebuilds incremental models from scratch instead of adding only new rows. Use it after changing an incremental model's logic. |
| `dbt snapshot` | Runs the snapshots: records how rows in a source or model changed since the last run (slowly changing dimension, type 2). |
| `dbt compile` | Renders the Jinja into plain SQL under `target/compiled/` and builds nothing. Use it to read what the warehouse would receive. |

## Test

| Command | What it does |
|---|---|
| `dbt test` | Runs every data test and unit test. Each data test is a query for the rows that break a rule; no rows means PASS. |
| `dbt test --select MODEL` | Runs the tests attached to one model. |
| `dbt test --select test_type:generic` | Only the tests declared in YAML: `not_null`, `unique`, `accepted_values`, `relationships`. |
| `dbt test --select test_type:singular` | Only the tests written as SQL files in `tests/`. |
| `dbt test --select test_type:unit` | Only the unit tests: the model's logic run on made-up input rows. |
| `dbt test --store-failures` | Saves the failing rows of each test to a table, so you can query them. |

## Build and test together

| Command | What it does |
|---|---|
| `dbt build` | Runs seeds, models, snapshots and tests in graph order. When a model's test fails, everything downstream of it is skipped. The command to use by default. |
| `dbt build --select MODEL+` | One model and everything downstream of it, with their tests. The usual command after editing a model. |
| `dbt build --fail-fast` | Stops at the first failure instead of carrying on with unrelated models. |
| `dbt retry` | Reruns only what failed or was skipped in the previous command. |

## Look at the result

| Command | What it does |
|---|---|
| `dbt show --select MODEL` | Runs the model's query and prints the first five rows, without building anything. `--limit 20` for more. |
| `dbt show --inline "select ..."` | Runs any query, Jinja included, and prints the rows. Quote the whole query. |
| `dbt ls` | Lists everything in the project: models, tests, seeds, sources. Runs nothing. |
| `dbt ls --resource-type model` | Lists only the models. |
| `dbt ls --select +MODEL` | Lists a model and everything upstream of it: the quick way to check a selection before running it. |

## Document

| Command | What it does |
|---|---|
| `dbt docs generate` | Builds the documentation site into `target/`: descriptions from the YAML, columns from the warehouse, and the lineage graph from `ref()` and `source()`. |
| `dbt docs serve` | Serves that site on your machine. In the dev container use `dbt docs serve --host 127.0.0.1 --port 8081`. |

## Tidy up and one-off jobs

| Command | What it does |
|---|---|
| `dbt clean` | Deletes the folders listed under `clean-targets` in `dbt_project.yml`, usually `target/` and `dbt_packages/`. |
| `dbt run-operation MACRO` | Runs one macro by name, for a job that is not a model. `--args '{key: value}'` passes arguments. |

## Flags that work on most commands

| Flag | What it does |
|---|---|
| `--select`, `-s` | Chooses what the command acts on. See the next section. |
| `--exclude` | Removes things from the selection. |
| `--target NAME`, `-t` | Uses another target from `profiles.yml`, for example `prod` instead of `dev`. |
| `--vars '{name: value}'` | Sets project variables for this run, read in models with `var('name')`. |
| `--threads N` | How many models run at once. |
| `--full-refresh` | Rebuilds seeds and incremental models from scratch. |
| `--fail-fast`, `-x` | Stops at the first failure. |
| `--quiet`, `-q` | Prints only errors and the command's own output. |
| `--debug`, `-d` | Prints every SQL statement dbt sends. Use it when a failure makes no sense. |

# Part 2 — Use dbt well

## Choose what runs: `--select`

| Selector | What it selects |
|---|---|
| `stg_prices` | One model, by name. |
| `+fct_prices_usd` | The model and everything upstream of it. |
| `stg_prices+` | The model and everything downstream of it. |
| `+int_prices_usd+` | The model, everything upstream and everything downstream. |
| `1+fct_prices_usd` | The model and only its direct parents. A number limits how far the `+` reaches. |
| `tag:staging` | Every model tagged `staging`. In the challenge each layer folder has a tag. |
| `staging` or `path:models/staging` | Every model in that folder. |
| `source:vendor_feed+` | Everything that depends on a source. |
| `test_type:unit` | By kind of test: `generic`, `singular`, `unit`. |
| `config.materialized:table` | Every model built as a table. |
| `stg_prices stg_fx_rates` | Separated by a space: either one (union). |
| `tag:marts,config.materialized:table` | Separated by a comma: both must be true (intersection). |
| `state:modified+ --state PATH` | What changed compared with an earlier run's `manifest.json`, and what depends on it. What CI uses to build only the changes. |

Check any selection with `dbt ls --select ...` before running it.

## The files dbt reads

| File or folder | What it is for |
|---|---|
| `dbt_project.yml` | The project's name, which profile it uses, and defaults per folder of models: materialisation, tags, hooks. The name is fixed. |
| `profiles.yml` | The connection: one entry per target (dev, prod) with the warehouse type and where the models land. The name is fixed. It holds no secrets in the training repository: the token comes from the environment. |
| `models/` | One SELECT per `.sql` file; the file name is the model's name. In the challenge: `staging/` (`stg_`), `intermediate/` (`int_`), `marts/` (`fct_`, `agg_`). |
| YAML files under `models/` | Any name, `.yml` or `.yaml`. dbt reads the keys inside: `sources:` for raw tables, `models:` for descriptions and tests, `unit_tests:`. By habit `sources.yml` and `schema.yml`. |
| `seeds/` | CSV files that `dbt seed` loads. |
| `tests/` | Singular tests: one query per file that returns the rows breaking a rule. |
| `macros/` | Jinja macros: SQL written once and called from many models, and custom generic tests. |
| `snapshots/` | Snapshot definitions. |
| `packages.yml` | Packages for `dbt deps` to install. |

## The files dbt writes

| File or folder | What it holds |
|---|---|
| `target/compiled/` | Each model and test as plain SQL, after the Jinja is rendered. Read this when a model misbehaves. |
| `target/run/` | The statement dbt actually sent, with the `create view` or `create table` around your SELECT. |
| `target/manifest.json` | The whole project as dbt understands it: every model, test and dependency. What Airflow's Cosmos and `state:modified` read. |
| `target/run_results.json` | What the last command did: each node, its status and how long it took. |
| `target/catalog.json`, `target/index.html` | The documentation site from `dbt docs generate`. |
| `logs/dbt.log` | The full log of recent commands, including every SQL statement. |
| `dbt_packages/` | Installed packages. |

None of these is edited by hand, and none is committed: they belong in `.gitignore`.

## The Jinja you meet

| You write | It means |
|---|---|
| `{{ source('vendor_feed', 'vendor_prices_raw') }}` | A raw table declared under `sources:`. dbt fills in the catalog and schema. |
| `{{ ref('stg_prices') }}` | Another model in the project. dbt fills in its name and learns the build order from it. |
| `{{ config(materialized='table') }}` | A setting for this one model. It overrides the folder's setting in `dbt_project.yml`. |
| `{{ this }}` | The table or view the current model builds. Used in hooks, such as `OPTIMIZE {{ this }}`. |
| `{{ var('name') }}` | A project variable, from `dbt_project.yml` or `--vars`. |
| `{{ target.name }}`, `{{ target.schema }}` | The target the command is running against. |
| `{{ my_macro(arguments) }}` | Calls a macro from `macros/`; its SQL text is placed here. |
| `{% if ... %} ... {% endif %}`, `{% for x in list %} ... {% endfor %}` | Logic that writes SQL. It runs when dbt compiles, never in the warehouse. |
| `{% if is_incremental() %}` | True on the second and later runs of an incremental model: the place for the "only new rows" filter. |
| `{# a comment #}` | A comment that does not reach the compiled SQL. |

Two curly braces print a value into the SQL. A curly brace and a percent sign run logic and print nothing.

## Materialisations

| Materialisation | What dbt creates | Use it for |
|---|---|---|
| `view` | A saved query, run each time it is read. | Staging and intermediate models: cheap, always fresh, nobody reads them directly. |
| `table` | A table, rewritten on every run. | Marts: fast for the consumers and dashboards that read them. |
| `incremental` | A table that gains only the new rows on each run. | Large fact tables where a full rebuild is too slow or too costly. |
| `ephemeral` | Nothing: the SQL is pasted into the models that use it. | A small shared step you never need to query. |
| snapshot | A history table with validity dates for each version of a row. | Dimensions whose values change and whose history matters. |

Set it per folder in `dbt_project.yml` with `+materialized:`, and override it in one model with `config()`.

## In the training repository

| Command | What it does |
|---|---|
| `mise run setup:databricks` | Signs you in to Databricks from the browser and puts the token in your environment. Run it once, and again if dbt cannot find your credentials. |
| `mise run challenge:verify 02` | Seeds, builds and tests the dbt challenge; green means solved. Runs from anywhere in the repository. |
| `mise run challenge:reset 02` | Puts every challenge file back to its blank stub. It deletes your work: never use it to "start clean". |
| `dbt docs serve --host 127.0.0.1 --port 8081` | The docs site in the dev container. The flags are needed because `DBT_HOST` there holds the Databricks address. |

## Habits that keep a project trustworthy

| Habit | Why |
|---|---|
| `dbt build`, not `dbt run` | A run that finishes says the SQL executed, not that the answer is right. Build runs the tests with the models and stops what is downstream of a failure. |
| Build what you changed and what depends on it | `dbt build --select my_model+` after every edit: fast, and it shows what your change broke. |
| Read the compiled SQL | When a result surprises you, open the model under `target/compiled/` and run that SQL yourself. |
| `source()` and `ref()`, never a typed table name | A hard-coded name hides a dependency from dbt: the build order, the lineage and the dev and prod targets all stop working for that model. |
| Fix the model, not the data | When a test fails, the correction goes in the SQL, so it holds on the next run too. |
| Give every model a key test | `not_null` and `unique` on the key of each model catch the duplicate rows that a bad join creates. |
| Clean in staging, join later | Rename, cast and tidy codes once, in the staging model. Joins on untidy values silently drop rows. |
| Describe as you build | A description in the YAML takes a minute while you still remember what the column means. |
| Keep secrets out of the project | No tokens in `profiles.yml` or in any committed file; the profile reads them from the environment. |
| Review generated code in graph order | Sources, then staging, then joins, then tests: the same order whether a person or Copilot wrote it. |

## When something goes wrong

| What you see | Likely cause | What to do |
|---|---|---|
| `Could not find profile named ...` | `profile:` in `dbt_project.yml` does not match a name in `profiles.yml`, or you are in the wrong folder. | `dbt debug`; run from the folder with `dbt_project.yml`. |
| `auth_type: oauth is required when not using access token` | The token did not reach this terminal. | Open a new terminal, or `mise run setup:databricks`. |
| `Compilation Error ... depends on a node named 'x' which was not found` | A `ref()` names a model that does not exist, or the name is misspelt. | `dbt ls --resource-type model` to see the real names. |
| `Compilation Error ... source named 'a.b' which was not found` | The source is not declared, or the names differ from the YAML. | Check the `sources:` block: source name, then table name. |
| A YAML parse error with a line number | Indentation: a tab, or a key at the wrong level. | Two spaces per level; `dbt parse` to check. |
| `Database Error` in a model | The SQL is wrong for the warehouse: a column, a type, a function. | Open the file under `target/compiled/`, run it, read the warehouse's message. |
| `--select tag:staging` selects nothing | The `models:` block in `dbt_project.yml` is missing, or its project name does not match `name:`. | Compare the two names; they must be identical. |
| A test fails | The data breaks the rule, or the rule is wrong. | Run the test's SQL from `target/compiled/` to see the rows, then decide which. |
| A model still returns the old result | You built a different model, or the model is a view over a table that was not rebuilt. | `dbt build --select +my_model`. |
| `dbt docs serve` cannot start | The default address is taken by `DBT_HOST`. | `dbt docs serve --host 127.0.0.1 --port 8081`. |
