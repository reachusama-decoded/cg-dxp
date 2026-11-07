# Challenge changes & why

These training challenges were originally written by someone else and ported into this
repo. This doc lists the **deliberate changes we made** and the **reason for each**, so
the changes are easy to explain and defend.

Most changes fall into three buckets: (1) making a solved challenge actually build/run in
*this* repo and devcontainer, (2) meeting Capital Group platform rules (security,
governance), and (3) consolidating the preflight's multi-file guide/runner layout into one
`README.md` + one `verify.sh` per challenge. Full technical detail is in the
"Implementation notes (as-built)" section of
`docs/superpowers/specs/2026-07-27-training-challenges-and-atlas-capstone-design.md`.

## Challenge 02 — dbt pipeline

| Change | Why |
|---|---|
| The six raw source tables now ship as **dbt seeds** (`dbt/seeds/*_raw.csv`), loaded automatically. | The preflight created them with a manual `provision-raw-sources.sql` script (run once, by hand, before verify). That script wasn't ported, so nothing in this repo created the tables and even a correct pipeline couldn't build. The seeds carry **that script's exact data**, but load automatically (via `verify.sh` / `mise run challenge:seed 02`), land in the trainee's dbt schema, and match how challenge 04 ships its data. |
| `sources.yml` now pins each source's `database`/`schema` to the dbt target. | Without it, `source('custodian', …)` resolves to a schema named `custodian` (which doesn't exist) instead of the trainee's own schema where the seed lands. |
| `verify.sh` now **seeds → runs → tests** (and there's a `mise run challenge:seed 02`). | It has to load the seed data before building. |
| Guide checks that used `show --inline "<SQL>"` (Sections 1, 5, 6) now use `show --select <seed/model>` or the build-log materialization label. | `mise run challenge:dbt 02 -- … --inline "select …"` passes the SQL through a mise variadic that **word-splits on spaces** (and `select *` glob-expands to the repo file listing), so every inline peek errored with *"Got unexpected extra arguments (Dockerfile GETTING_STARTED.md …)"*. Same fix as challenge 03. |
| The `models:` block (folder `+tags`, `+materialized`, and the marts `OPTIMIZE … ZORDER` post-hook) was **restored to `dbt_project.yml`, and the complete `dbt_project.yml` now ships in `stubs/` too**. | The port dropped the `models:` block, so `--select tag:staging` (S5), the view/table lesson (S6), and the ZORDER post-hook (C9) had nothing to act on. And because `challenge:reset` copies `stubs/` over `dbt/`, the minimal `stubs/dbt_project.yml` **clobbered** the seed post-hook on reset, breaking `source freshness` (S3). Shipping the full project in both keeps reset safe. |
| `marts/schema.yml` now **ships** (fct + agg generic tests); `staging/schema.yml` lives in `solution/` only. | The port dropped both. C5 says the marts schema "ships … read it and run it", so it must exist; S8 is an authoring task ("Create dbt/models/staging/schema.yml"), so that one belongs in the solution reference, not the starter. |
| The capstone mart (`agg_fund_daily_exposure`) and its `reconcile_daily_exposure` test are **no longer shipped** (the trainee creates them in C10); `assert_nav_within_tolerance` ships as a failing stub. | C10 says "Create" these and S2 counts **ten** models — shipping the capstone as an 11th stub broke C7's full build (the placeholder mart can't run the marts ZORDER post-hook, and the pre-solved reconcile test referenced columns the placeholder lacks). C6 says "Complete" the NAV test, so it ships as a stub the trainee fills in. |
| Guide config snippets use the real project namespace `portfolio_analytics_challenge:` (was `portfolio_analytics:`), solution references point to the shipped `dbt/dbt_project.yml`, and the full-build summary says **eight** seeds (was two). | A `models:`/`seeds:` block keyed on the wrong project name is silently ignored by dbt; the referenced `solution/dbt/dbt_project.yml` didn't exist; and `dbt build` seeds eight files, not two. |

The seed values are chosen so the NAV-reconciliation test passes within 1 basis point —
the fixtures are internally consistent, not random.

These fixes were **verified in the devcontainer**: a fresh `challenge:reset 02` → author →
`mise run challenge:verify 02` runs green (8 seeds, 11 models, 17 tests); `source freshness`
passes on all five feeds; `--select tag:staging` lists the staging layer; and C7's full
build passes with the capstone still un-created (10 models), so the incremental flow never
dead-ends before Challenge 10.

## Challenge 03 — airflow orchestration

| Change | Why |
|---|---|
| The freshness-gate and publish tasks use **`PythonOperator`** instead of **`BashOperator`**. | **Security / governance.** CG's Cimon cluster policy **blocks arbitrary-shell operators** (`BashOperator`, `SSHOperator`, `DockerOperator`, …) as high-risk. A `BashOperator` DAG is rejected and won't run; `PythonOperator` is the approved pattern. |
| The DAGs now carry `usage-id` / `cost-center` tags. | CG governance (Cimon) **requires** these tags — without them the DAG is rejected. We reused the repo's existing tag convention. |
| The Cosmos `DbtTaskGroup` points at the Astro image's dbt (via `ExecutionConfig`). | The Astro image keeps dbt in an isolated venv (to avoid dependency clashes with Airflow), so Cosmos couldn't find `dbt` and the DAG failed to load. |
| A small local-only `airflow_local_settings.py` adds each product's folders to `sys.path`. | The product is mounted in a nested folder, so its `callbacks` / `include` modules weren't importable and the DAG failed to load. |
| `verify.sh` does a **fast static check of the DAG wiring** instead of a full Airflow run. | A full run renders the Cosmos graph via `dbt ls`, which only works inside a fully-configured Airflow environment. The static check validates the actual lesson — the wiring — instantly. Running it for real is still in the guide's `astro dev start` steps. |
| The guide now teaches `PythonOperator` (was `BashOperator`). | Keep the lesson consistent with the change above, so trainees learn the pattern that actually passes CG governance. |
| The dbt profile defines a **`local` target** (identical token target to `dev`). | Guide step 3's check `mise run challenge:dbt 03 -- debug` passes `--target local` (the repo-wide convention every other profile follows), but this profile only defined `dev`, so the very first dbt command failed with *"profile does not have a target named 'local'"*. |
| **`.astro/test_dag_integrity_default.py`** is committed. | Guide step 2's check `astro dev parse` requires it; it is a standard astro scaffold file that was missed when `.astro/` was committed, so a fresh clone hit *"does not exist. Please run `astro dev init`"* and could not parse DAGs. |
| Challenge 03's `sources.yml` pins each source's `database`/`schema` to the dbt target. | Without it, `source('custodian', …)` resolves to a schema literally named `custodian` (which doesn't exist) instead of your training schema, so the DAG's freshness gate and every staging model hit `TABLE_OR_VIEW_NOT_FOUND`. (Same latent bug we fixed in challenge 02 — it was unfixed here.) |
| Challenge 03 provisions its raw feeds by **reusing challenge 02's seed step** (`mise run challenge:seed 02`), and 02's five `*_raw` seeds now **refresh `_extracted_at` to `current_timestamp()` on load** (a seed post-hook). | The DAG reads the same four raw feeds challenge 02 builds on, so rather than duplicate the data we reuse 02's seeds into the same schema. The authored CSV timestamps are static (May 2026), so without the refresh the DAG's freshness gate reads the feed as stale and fails; the post-hook makes a freshly seeded feed pass on a green run. |
| The DAG's **freshness gate authenticates with the `databricks_default` connection token** (via a token-auth `airflow` dbt target). | The gate shelled `dbt source freshness` through the static `auth_type: oauth` profile, which in the astro container falls back to **interactive browser OAuth and hangs the task**. Reusing the fresh connection token (as Cosmos does) makes it non-interactive. |
| `docker-compose.override.yml` **forwards `DBT_SCHEMA` / `DBT_CATALOG`** into the astro containers. | Without them the DAG resolved the schema to `training_student` instead of `training_<user>`, so Cosmos and the gate looked in the wrong schema. |
| The DAG's Databricks config (`http_path`, catalog, schema) is captured from the shell env **at `astro dev start` time**, so the guide now boots the stack in the **Prerequisites** (right after `setup:databricks` + seeding), warns to start it only **once setup has finished**, and says to run `astro dev restart` on a cold start. The freshness gate now **surfaces dbt's real error** and distinguishes a cold-start connection failure from a genuine stale-feed breach. | Cosmos needs `http_path` at DAG **parse** time and the gate needs it at run time; both read it (plus catalog/schema) from env vars written by `mise run setup:databricks` into `~/.config/dpc/databricks.env`. Starting the stack before setup finished — easy to do during the devcontainer's multi-minute first-run init — left the containers with an empty env, so Cosmos and the gate failed with *"The config 'http_path' is required"*. The gate used to report **"breached error_after" for _every_ failure**, sending trainees to chase a stale feed when the stack just needed `astro dev restart`. |
| The Cosmos `DbtTaskGroup` now reads the dbt profile via **`profiles_yml_filepath`** (was `DatabricksTokenProfileMapping`), and the freshness gate picks its target at runtime. | Runtime `BaseHook.get_connection` lookups intermittently failed to resolve `databricks_default` during Airflow-3 local `dags test`, so parse/exec now reads the repo profile directly and injects host/token from the connection only when available. |
| The `local`/`dev` dbt targets use **token auth** (`DBT_ACCESS_TOKEN`) instead of `auth_type: oauth`; `threads: 1` and `connection_parameters._disable_pandas: true` were added. | `profiles_yml_filepath` runs `--target dev` inside the astro container, where `auth_type: oauth` falls back to interactive browser OAuth and hangs; `.mise/env.sh` already mints `DBT_ACCESS_TOKEN` from OAuth. `_disable_pandas` disables the pandas/pyarrow deserialization path that flaked on `dbt show`; `threads: 1` removes result-fetch concurrency races. |
| The DAG carries `max_active_tasks=1` and runs Cosmos tests **after all builds** (`TestBehavior.AFTER_ALL`). | Serialize local task execution to avoid Airflow-3 supervisor start/heartbeat races, and stop relationship tests from referencing marts before they are built. |
| A local-only `airflow_local_settings.py` adds **version-guarded, opt-in** compatibility shims for Airflow 3.1 (cimon listener hookspec; transient supervisor heartbeat/start-race handling). | Airflow 3.1's local `dags test` raised a `PluginValidationError` and killed tasks on transient queued→running conflicts, failing §8–9 nondeterministically. The shims are mounted only into the devcontainer and no-op on untested versions. |
| The guide's **CLI commands use `astro dev run …`** (was bare `airflow …`) and the parity check uses `show --select <model>` (was `show --inline "<SQL>"`). | Airflow runs inside the astro containers, so bare `airflow` isn't on the devcontainer `PATH`; `mise run challenge:dbt -- show --inline "<SQL>"` breaks because mise word-splits the quoted SQL; and some commands needed Airflow 3 syntax (e.g. `dags list-runs <dag>` positional, not `-d`). |
| Phase 2's `test_dag_structure.py` (live/stub/solution) is a **static** ast/text test (no DagBag/airflow), checking the tiered callbacks + SLA + no-secrets. | The DagBag version needed airflow (only in the astro containers, not the trainee's `python`), the three copies had diverged, and its `test_primary_dag_is_stubbed_for_training` **failed the moment a trainee solved the DAG**. The static test runs with a plain `pytest`, passes on the stub and the solution alike (callbacks/SLA are pre-wired), and the wiring chain stays the learner gate in `verify.sh`. |
| Phase 2's guide checks use bare `pytest` and a `grep` panel count (was `python -m pytest` / `python -c "import yaml"`). | The trainee's default `python` (`.venv`) lacks pytest and PyYAML (deps install `--system` into `/opt/venv`), so those commands errored. |
| Phase 2's "no Slack/vendor" greps are scoped to real usage (SDK / URL / `alert_channel`), not the bare word. | The files legitimately **document** the anti-goal ("Slack-free", "Microsoft Teams webhook"), so a bare `grep slack`/`teams` matched the docs and the check never printed "good". |
| Guide **section 2's parse check is a static `python -c "import ast; ast.parse(…)"`** (was `astro dev parse`). | `astro dev parse` doesn't mount `data_products`, so it found **0 DAGs and passed vacuously**; and even baked into the image it can't render the Cosmos `DbtTaskGroup` offline — that needs the `databricks_default` connection, which only exists after `astro dev start`. The static check validates DAG **syntax** offline; the full DagBag load (imports + Cosmos) happens at `astro dev start` (section 9), where `astro dev run dags list-import-errors` is the real gate. |
| Guide **sections 4 and 5 dropped their leading `astro dev parse`** — the checks are now just `astro dev run tasks test/list …`. | Same vacuous-parse reason as section 2. Those checks exercise the real task against the **running** scheduler (`astro dev run` execs into it), which is why the stack is now booted in the Prerequisites rather than first at section 9. |

These fixes were **verified end to end in the astro runtime**: `astro dev parse` reports
zero import errors, and a full `astro dev start` + trigger runs the DAG **green (24/24
tasks**: freshness gate → Cosmos `dbt_pipeline` → publish), landing the marts in the
trainee's schema — provided the stack is started **after** `setup:databricks` finishes so it
inherits the Databricks env (a cold start now fails with an actionable "run `astro dev
restart`" message rather than a misleading stale-feed error).

## Challenge 04 — atlas capstone

A trainee walkthrough (a fresh-eyes subagent executing every step) surfaced fixes the port
needed for the capstone to run end to end:

| Change | Why |
|---|---|
| `dbt_project.yml` now declares **medallion-alignment tags** (`source-aligned` / `domain-aligned` / `consumer-aligned`) folder-by-folder in its `models:` block. | The guide's entire build flow selects by `dbt run --select tag:source-aligned` (then domain-, then consumer-aligned), but the port shipped a bare `models: {+materialized: view}` with **no tags** — so every tag selector matched **0 nodes**, nothing built, and every downstream section failed `TABLE_OR_VIEW_NOT_FOUND`. Tags are folder-level (not in the model bodies) so a trainee's authored SQL inherits its layer tag. |
| Guide §4/§6 peeks use `show --select <seed/model>` instead of `show --inline "<SQL>"`. | `mise run challenge:dbt 04 -- … --inline "select …"` word-splits the SQL under mise (and `select *` glob-expands to the repo file listing), erroring with *"Got unexpected extra arguments"*. Same fix as challenges 02 and 03. |
| `verify.sh` runs `databricks bundle validate` as a **non-fatal warning**. | `bundle validate` shells out to Terraform, which fails with *"openpgp: key expired"* in the future-dated sandbox — an environment/clock artifact, not a challenge defect. Under `set -e` it aborted the whole verify gate; now it warns and the dbt parse/compile gate still passes. |
| The guide now verifies **only** via `mise run challenge:verify 04` — the bare `bash challenges/v1/04-atlas-capstone/verify.sh` command was removed (challenges 02 and 03 already verified this way). | `verify.sh` runs dbt with `--target local`, whose Databricks token comes from `.mise/env.sh`. That file is sourced only by mise (the interactive-prompt hook or a `mise run` task), so a *standalone* `bash verify.sh` has an empty `DBT_ACCESS_TOKEN`; dbt-databricks then falls back to OAuth and dies with *"auth_type: oauth is required when not using access token"* — even though `mise run challenge:dbt 04 -- build` connects fine in the same shell. Routing verification through the mise task loads the env and the gate passes. |

Everything else the subagent flagged (exposures, the relationship test, the reconciliation
tests, the later marts) was **downstream of the missing tags** or a step the trainee authors
inline (exposures.yml, generic/relationship tests) — all pass once the tags exist and the
step is actually authored. Verified in the devcontainer: full `dbt build` runs **40/40
green** (`Completed successfully`), and `mise run challenge:verify 04` passes. A later
business-persona walkthrough re-confirmed the only genuine guide defect was the standalone
`verify.sh` invocation above; its other reported failures were unauthored Phase-2 marts or a
transient Databricks *"Error during request to server"* that cleared on retry.

## Guide & file structure (all challenges)

The preflight challenges shipped several per-challenge docs and scripts; we consolidated
them to one guide + one gate per challenge.

| Change | Why |
|---|---|
| The lesson files (`CHALLENGES.md`, `CHALLENGES-PHASE2.md`, and 04's `-STRETCH`) are merged into a single **`README.md`** per challenge. | One guide per folder is the repo convention (the folder's `README.md` is its entry point and renders on GitHub). The phases are kept as sections. |
| `RUN.md` and `START_HERE.md` are **dropped**. | They were preflight-runner instructions (its own devcontainer, "run `provision-raw-sources.sql` first", "sources already provisioned"). In this repo every challenge runs one way — `mise run challenge:verify` / `challenge:dbt` in the shared devcontainer — so those commands live in the README, and the old runner notes would be misleading. |
| `provision-raw-sources.sql` (02) is **replaced by dbt seeds** (see Challenge 02 above). | Same data, loaded automatically by the challenge tooling instead of a manual "run this SQL first" step. |
| The several `verify-with-*.sh` variants become one **`verify.sh`** per challenge. | One command, one PASS/FAIL gate. |
| 04's extra preflight docs (`DATA-EXPLAINER.md`, `REFERENCE.md`, `WRAP-UP.md`, `DESIGN-SESSION.md`) are folded into the README or dropped. | They were preflight-session artifacts; the trainee-facing content lives in the one README. |

## Across all challenges

| Change | Why |
|---|---|
| `verify.sh` is the trainee's **self-check**: it fails (red) on the unsolved starter and passes (green) once solved. | Makes "did I do it right?" the meaning of a green run. |
| Challenge dbt commands run through the repo's `dbt_wrapper.py` with an explicit interpreter. | Avoids failures from the wrong `dbt` being on `PATH` in the devcontainer. |
