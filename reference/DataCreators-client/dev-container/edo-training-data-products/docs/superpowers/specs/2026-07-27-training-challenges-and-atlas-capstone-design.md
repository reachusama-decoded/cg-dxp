# Training Challenges in the Devcontainer + Atlas Paved-Path Capstone — Design

> Status: **DRAFT — pending review.** Design only; no implementation.
> Scope: the full 5-step training challenge track. **Part 1** ports challenges
> 00–03 into the shared devcontainer; **Part 2** builds the capstone (04) as a real
> paved-path data product and retires `atlas_elt_demo`. The two parts share a thin
> foundation and one verification environment, so they are one phased effort (see
> "Execution approach").

## Context

The training program teaches building **data products** — dbt transformations on
Databricks, deployed as Databricks jobs, orchestrated by Airflow. The hosts authored a
5-step challenge track in a separate `preflight` repo:

| # | Challenge | Teaches |
|---|-----------|---------|
| 00 | `environment-check` | Toolchain/readiness (git/gh, Python, dbt+databricks, Astro, Databricks CLI, network). |
| 01 | `docker-intro` | Docker image vs container: complete a `Dockerfile`, build/run a Python image over `holdings.csv`. |
| 02 | `dbt-pipeline` | End-to-end dbt on Databricks: sources → staging → intermediate → marts, tests. |
| 03 | `airflow-orchestration` | Orchestrate the dbt pipeline with Airflow + Cosmos (`DbtTaskGroup`), freshness gate, retries. |
| 04 | `atlas-capstone` | Build a full data product **the CG paved-path way** (Part 2). |

Today challenges 02/03/04 ship their **own** `.devcontainer`, `setup-databricks-dbt.sh`,
and standalone dbt project; 01 assumes a bare Docker host; 00 is a laptop preflight.
Trainees will instead use the **one** devcontainer built by `edo-training-data-products`.

### The shared devcontainer (evidence)

- Privileged devcontainer with Docker-in-Docker; forwards ports `8020/8080/6563`;
  lifecycle `postCreate: mise run setup`, `postStart: dpc-check` (`.devcontainer/*`).
- **OAuth-first Databricks:** `mise run setup:databricks` writes a non-secret env
  contract to `~/.config/dpc/databricks.env`; `.mise/env.sh` mints a short-lived
  `DBT_ACCESS_TOKEN`; an OAuth-refresh loop upserts the `databricks_default` Airflow
  connection. PAT is an explicit `--pat` fallback.
- **Env-driven dbt profiles:** `data_products/*/dbt_profiles/profiles.yml` read
  `DBT_HOST`/`DBT_HTTP_PATH`/`DATABRICKS_SCHEMA`/`DBT_ACCESS_TOKEN`, catalog defaulting
  to `training_dev`; dbt runs via `mise run dbt:*`.
- **Native Astro project `edo-training`, Airflow 3.x + `astronomer-cosmos 1.15`**; the
  compose override mounts `./data_products` → the Airflow dags folder and
  `~/.databrickscfg` into every Airflow service.
- **Verification:** `dpc-check`, `pytest tests/local_env/offline`,
  `mise run verify:local-dev`.

Two facts make this cheap: (1) challenges and repo already target the same
`training_dev` catalog + personal `training_<user>` schema; (2) challenge 03's Cosmos
DAG already reads the `databricks_default` connection the native Astro provides.

The repo also already holds `data_products/atlas_elt_demo`: the *same* Atlas domain and
seed data as the capstone, scaffolded into the paved-path shell but with every model a
`select *` passthrough. Part 2 supersedes it.

## Goal

A trainee opens the devcontainer, runs `mise run setup:databricks` **once**, and works
the whole track: challenges 00–03 each with a one-command PASS/FAIL verify, and the 04
capstone builds a real paved-path data product (`data_products/atlas_elt`) — all on the
repo's existing dbt/Databricks/Astro config, with no per-challenge devcontainer or auth
and without breaking native flows.

## Non-Goals

1. Changing what 00–03 teach (Docker basics, dbt medallion, Cosmos orchestration).
2. Converting 00–03 to the repo's native idioms — only the capstone 04 adopts the
   paved path.
3. Touching other data products or the dev+/prod deploy pipelines — `atlas_elt`'s
   bundle uses the `local` target only.

## Approach

Preserve each challenge's teaching content; standardize the environment on the shared
devcontainer. The work is a **thin shared foundation** + two parts:

- **Foundation:** `challenges/` home, one OAuth auth, the `challenge:*` mise tasks, and
  first-class tests.
- **Part 1 (00–03):** a light port into the devcontainer; challenge 03's DAG + dbt
  live natively under `data_products/portfolio_analytics/`.
- **Part 2 (04):** build the `atlas_elt` paved-path product and retire `atlas_elt_demo`.

Part 2 depends on the foundation, and both parts share one devcontainer + Databricks
schema + local Astro — so this is one coupled, phased effort (see "Execution approach").

## Shared foundation

### Location

Guides (and the no-DAG challenges 00/01/02's runnable files) live under `challenges/` —
they aren't data products, so they stay out of `data_products/` (which would break its
tooling/CI). Airflow-bearing challenges place their runnable artifacts **top-level in
`data_products/`** (like `asset_reference_data`) so the native Astro discovers the DAGs
directly: 03 → `data_products/portfolio_analytics/`, 04 → `data_products/atlas_elt/`.
They are **not** nested under a `data_products/training_environment/` namespace — that
folder doesn't exist (the `.sqlfluffignore` reference is stale, and `training_environment`
is actually a bundle *variable value*, not a directory).

### One auth

Every challenge uses the devcontainer's single OAuth session
(`mise run setup:databricks`) + the repo's env-var contract (`DBT_HOST`/`DBT_HTTP_PATH`/
`DATABRICKS_SCHEMA`/`DBT_ACCESS_TOKEN`, catalog `training_dev`). Each challenge's own
`setup-databricks-dbt.sh` (which overwrites `~/.dbt/profiles.yml`) is dropped.

### One command each + first-class tests

`mise run challenge:verify <NN>` (+ `verify-all`), plus `challenge:dbt` and
`challenge:reset`. Challenge checks join the repo's normal suite using its existing
offline/live discipline (`pytest.ini` markers `integration`/`airflow`;
`tests/local_env/{offline,live}`; live gated by `CERT_INTEGRATION_TESTS=1`):

- **Offline (default, in CI):** required files present; `verify`/`reset` executable;
  `challenge:*` tasks register; dbt projects **parse**; DAGs **import** cleanly; the
  `atlas_elt` `ref()` graph compiles. Under `tests/challenges/offline`.
- **Live (opt-in, marked `integration`):** `dbt build` on Databricks, `bundle
  validate`/`deploy`, a triggered DAG run. Under `tests/challenges/live`; fold the
  verifiers into `mise run verify:local-dev`.

**One gate, two readings — by *who* runs it against *what*.** The underlying question is
always "does the pipeline build green and pass its tests?":

- **Trainee → completion.** Runs `challenge:verify <NN>` **live against their own working
  tree** (plus the guide's per-section "How to check" while authoring). Stubs pass offline
  but build **red**, so a green run means "I did it right." This is the ported preflight
  learner gate (`verify-with-databricks.sh`, `verify.sh`, `check-dag-load.sh`, …).
- **Builder / CI → health.** The **offline** subset runs hermetically on every change (no
  Databricks/Astro; passes on stubs) → "the challenge is still well-formed"; running the
  gate **live against the retained solution** confirms "still solvable." A broken challenge
  is this repo's highest-severity regression, so this belongs in CI.

### Trainee artifact — fill-in-the-blank stubs

Each challenge is delivered to trainees as **fill-in-the-blank stubs**: the files the
trainee is meant to author — a challenge's dbt models, or (for challenge 03) its
orchestration DAG — are placeholders (`select 1 as placeholder` + a `-- TODO`) they
complete; authoring the solution *is* the lesson. Any already-complete scaffolding is
left intact. The complete reference **solution**
is retained so the one-command `verify` always has a green baseline and trainees can
compare against it. `mise run challenge:reset <NN>` re-blanks the working tree back to
stubs (to start over, or to prep the repo for a fresh cohort). (The capstone product
ships complete and is reset to stubs on demand — see Part 2.)

### Non-interference

- `.dbtignore` / `.sqlfluffignore` ignore `challenges/` so 00/01/02's dbt SQL isn't
  built or linted by native tooling; `clone-sources` must not sweep their sources.
- Challenge **tests** are first-class (above), not excluded.
- The native `data_products/` entries (`portfolio_analytics`, `atlas_elt`) are
  intentionally in CI.

Acceptance: `mise run verify:local-dev` and `pre-commit run --all-files` stay green;
the challenge **offline** tests pass by default.

### Discoverability

`challenges/README.md` (the 00→04 path + the one prerequisite); a short "Optional:
Training Challenges" pointer in `GETTING_STARTED.md`; new `mise` tasks
`challenge:{verify,verify-all,dbt,reset}`.

**Challenge ↔ product mapping.** Challenges 03 and 04 keep their artifacts under
`data_products/` with real domain names (`portfolio_analytics`, `atlas_elt`) — the
folder/product name is **not** prefixed with the challenge number, because that name
propagates into the dbt project, bundle, and Databricks **job** names and would undercut
the capstone's "real product" lesson. Challenge membership is instead signalled by
(i) a marker `README.md` header in the product folder pointing back to its
`challenges/NN-*` guide, (ii) a machine-readable challenge tag in the product's
`dbt_project.yml` `meta` (also handy for the Part 1 §03 CI-relax caveat), and (iii) the
mapping listed in `challenges/README.md`. The exact marker wording and tag format are an
implementation detail.

## Part 1 — Challenges 00–03 (devcontainer port)

### 00 — environment check

Rebase on `dpc-check` + `databricks auth describe --profile DEFAULT` + workspace/Astro
reachability. Preserves the "know your toolchain" lesson, aligned to the devcontainer
(tools pre-installed) instead of a BYOD laptop.

### 01 — docker

Runs `docker build`/`docker run` on the devcontainer's dockerd. Keep `Dockerfile`,
`app/`, and `verify.sh` unchanged — the app builds its own `python:3.11-slim` image,
independent of the devcontainer's Python 3.13.

### 02 — dbt

Keep the challenge's dbt project (that *is* the lesson), but replace its `profiles.yml`
with the shared env-contract profile (same shape as `data_products/*/dbt_profiles/
profiles.yml`). Run via `mise run challenge:dbt 02 -- <args>`; the challenge's
`verify-with-databricks.sh` (dbt debug + build) then works unchanged on the shared
credentials. Version note: the devcontainer ships dbt-databricks 1.11 and the models
are Databricks SQL, so a `dbt build` smoke check is the acceptance gate.

**Source data (as-built).** The six raw sources (`custodian.holdings_raw`, …) were
provisioned in the preflight by a manual `provision-raw-sources.sql` script (run by hand
before verify); that script was not ported, so the tables existed in no catalog. Its data
now ships **as CSV seeds** (`challenges/02-dbt-pipeline/dbt/seeds/*_raw.csv`) — the same
author-sized values (NAV reconciles to `seed_custodian_nav` within 1 bp), delivered
through the dbt/mise flow instead of a manual SQL step. Each source in `sources.yml` pins
`database`/`schema` to the dbt target so `source()` resolves to where the seed lands.
`mise run challenge:verify 02` seeds → runs → tests; `mise run challenge:seed 02` loads
them ad-hoc. See "Implementation notes (as-built)".

### 03 — airflow (native placement)

Challenge 03's Cosmos DAG + dbt live under `data_products/portfolio_analytics/`. The
native Astro discovers the `.py` DAG directly (the compose override mounts
`data_products/` as its dags folder) and Cosmos resolves the co-located dbt project;
the DAG reuses the OAuth-refreshed `databricks_default` connection it already expects.
No activation or toggling — the artifacts are simply native and in CI.

Must-fix during the port: the DAG was authored for Airflow 2.10 / cosmos 1.14; the
runtime is Airflow 3.x / cosmos 1.15 (e.g. `schedule_interval` → `schedule`, provider
import paths, any `DbtTaskGroup` API changes). Acceptance: zero DAG import errors + one
green triggered run.

Additional must-fix (as-built): making the DAGs actually register in the astro runtime
also required a `sys.path` bootstrap for the product's `callbacks`/`include` packages,
pointing Cosmos at the Astro cosmos-venv dbt, CG-governance (`Cimon`) tags, and replacing
`BashOperator` (a Cimon-blocked operator) with `PythonOperator`. And because a full
DagBag load renders the Cosmos graph via `dbt ls` — only viable inside the configured
astro runtime — the offline `challenge:verify 03` is a fast **static wiring check**, not
a DagBag load. See "Implementation notes (as-built)".

CI note (resolved): `portfolio_analytics` is a plain Cosmos project, not a paved-path
product — and that needs no special handling. The Harness pipeline does per-product
Databricks work only through a `for … in data_products/*/databricks.yml` bundle loop (and
runs no pytest/sqlfluff), so a product with **no `databricks.yml` is skipped
automatically** — no shell, no exclusion. Its only obligation is that the DAG imports
cleanly under Airflow 3.x (the astro-deploy stage pushes all DAGs), already covered by the
DAG-load acceptance above.

### Per-challenge summary

| # | Keep (curriculum) | Drop (plumbing) | Rewire | Verify |
|---|-------------------|-----------------|--------|--------|
| 00 | Toolchain checklist | Laptop/BYOD framing | Base on `dpc-check` + auth/reachability | `challenge:verify 00` |
| 01 | `Dockerfile`, `app/`, `verify.sh` | (none) | Run on devcontainer dockerd | `challenge:verify 01` |
| 02 | dbt project + `CHALLENGES*.md` | own `.devcontainer/`, `setup-databricks-dbt.sh` | `profiles.yml` → shared env contract | `challenge:verify 02` |
| 03 | Cosmos DAG, `include/`, structure tests, dbt project | own `.devcontainer/`, `setup-databricks-dbt.sh` | Live in `data_products/portfolio_analytics/`; Airflow-3/cosmos-1.15 fixes; reuse `databricks_default` | `challenge:verify 03` |

## Part 2 — Capstone 04: `atlas_elt` paved-path product + retire `atlas_elt_demo`

Challenge 04 teaches building a data product **the CG paved-path way** — the native
pattern across `edo-training-data-products` and other CG data-product repos: dbt
**medallion** transformations per dataset, deployed as **Databricks Asset Bundle
jobs**, orchestrated by **Airflow via YAML `*.dag.yml` blueprint DAGs**, with **DQ
jobs** and **ODCS data contracts**. It supersedes `atlas_elt_demo`, replacing that
shell's `select *` passthroughs with a real product on the same data.

**Port, not curriculum rewrite.** The *product* becomes a real paved-path product —
every dataset ships with its own contract, bundle job, YAML DAG, and DQ, exactly like a
real CG product. But challenge 04 keeps its **original focus**: seed the source data,
build the source→domain→consumer dbt models, and understand the project. The paved-path
plumbing (contracts, bundle jobs, `*.dag.yml`, DQ) **ships complete as scaffolding** —
the trainee authors the **dbt models**, not the plumbing. (A shipped
`contract/<d>.odcs.yaml` therefore doubles as the *spec* the trainee's gold model must
match, so the contracts and the reference solution must stay in sync.)

### Why it converts cleanly

`atlas_elt_demo` already proved the paved-path **shell** works in the training
workspace: `databricks.yml` `local` target (jobs prefixed `[dev <initials>]` from
`databricks_job_prefix`), `variables/clusters.yml` singleNode job clusters,
`init_scripts/`, `dbt_profiles/`, `python/run_data_notify.py`, ODCS contracts, and the
blueprint DAG chain `dag_exec_check → databricks_run_now (dbt) → databricks_run_now
(dq) → mock_xcom → kafka_notify`. Its only gap is **content**. So the build is **reuse
that proven shell + drop in the capstone's real analytical models**, then retire the
demo name — not building the paved path from scratch.

### Target — `data_products/atlas_elt`

A real paved-path product, copied from the `atlas_elt_demo`/`asset_reference_data`
shell (product-level `dbt_project.yml`, `databricks.yml`, `dbt_profiles/`,
`variables/`, `init_scripts/`, `python/`, `datasets/sources.yml`, seeds). It **must**
live under `data_products/` because only that path is served by the paved-path tooling
(`databricks bundle deploy`, the DAG loaders, `mise run dbt:*`, `mise run contract:*`).
It ships **complete** (a green baseline and the repo's reference paved-path example);
`challenges/04-atlas-capstone/` holds the guide, a `reset` that blanks **only its dbt
models** to `TODO` stubs for a class, and the paved-path `verify`.

### Dataset decomposition (resolved)

**Framing — CG's two-catalog model.** Per *"Data Product Publish Pattern: App Catalog →
Domain Catalog"* (Confluence · IntegrationArchitecture): a product is **built and
validated in an App Catalog** (`training_dev` here), where **all** transformation lives;
a **separate governance step** (Deep Clone) then publishes validated outputs to a
consumer-facing **Domain Catalog**. Consequence: **how we split the product into datasets
is a transformation-layer choice, not dictated by publishing** — so we optimize for
port-fidelity and teaching, with no "one-published-table-per-dataset" mandate.

**Decision — entity-centric, ~10–12 datasets.** Reuse `atlas_elt_demo`'s **7 foundation
entity datasets** (`advisors, clients, funds, fund_holdings, instruments, portfolios,
trades`; derived `latest_price`/`positions` fold into `trades`) + **a few consumer-mart
datasets** (e.g. `fund_nav`, `portfolio_perf`, `market_daily`, `segment_aum`), each
`dag_exec_check`-ing its foundation dependencies. The capstone's alignment-named models
are placed by **refinement role** (per CG's Medallion doc): `src_*` → `staging` (bronze, "source as-is"), conformed
`dom_*` → `integration` (silver / "Foundation" — standardized business entities), and the
use-case marts → `prepared` (gold / "Consumption" — fit-to-purpose). **Fold
internal rollups into `integration`, not standalone datasets** — `rpt_portfolio_summary`
(5 marts depend on it) and the `rpt_advisor_leaderboard ← rpt_advisor_book ←
rpt_portfolio_summary` chain are transformation layers, not published endpoints.

Rationale: realistically sized (real products here have 2–7 datasets; ~20 would be
unusually large), reuses the existing shell, keeps the **port** faithful (the trainee
still authors every source/domain/consumer model — only the folder grouping changes),
and teaches every paved-path mechanism incl. cross-dataset `dag_exec_check`. A concrete
`capstone model → dataset/layer` table is produced when building; keep consumer-dataset
names distinct from the challenge-03 product `portfolio_analytics` and the foundation
dataset `portfolios`.

**Terminology (grounded in Confluence).** Medallion (`staging`/`integration`/`prepared`)
is the **within-product** refinement stage (*Design Principles — Medallion Architecture*,
IntegrationArchitecture). Source-/domain-/consumer-**aligned** are **product *types*** in
the CG mesh — a source-aligned product is "a governed mirror" of a source, conformed into
domain-aligned products, then shaped into consumer-aligned products (*Data Product and
Definition of Done*, IntegrationArchitecture). These are **different axes**, so this
training capstone deliberately **collapses the mesh into one product** with medallion
layers, placing the capstone's alignment models by refinement role (above). A full-mesh
version — Atlas as separate source/domain/consumer-aligned *products* — is truer to CG
but a much bigger structural change, so it is out of scope for this port.

**Out of scope:** the App→Domain Deep Clone publish (a separate governance step) — the
capstone builds/validates in the App Catalog; worth a one-line awareness note in the guide.

### Per-dataset artifacts (shipped scaffolding — only the `dbt/` models are trainee-authored)

Each dataset's set, following the demo/`currency` shapes:
`dbt/{staging,integration,prepared}` + `dbt/<d>.yml`; `bundle/<d>.job.yml` +
`<d>_dq.job.yml` (a `spark_python_task` running `dbt_wrapper.py`);
`airflow/<d>.dag.yml` (the blueprint chain, with prefixed `job_name`s);
`contract/<d>.odcs.yaml` + `runtime/dq_verify.py`.

### Orchestration — provided YAML blueprint DAGs

The product's DAGs are per-dataset `*.dag.yml` specs that the repo's
`blueprints_loader.py` renders at runtime, replacing the preflight capstone's
hand-written `atlas_elt_dag.py` / `@task.bash` DAGs — so the product orchestrates the CG
paved-path way, and the native Astro discovers them directly.

### Databricks permissions — contract publish is out of scope (resolved)

The challenge's green pipeline **never runs Flyway.** dbt materializes **managed** tables
in the trainee's own schema (`training_dev.training_<user>`) — verified: no model uses an
external `location_root`, so nothing writes into a contract table — and the DQ job and DAG
read those dbt-built tables. `mise run contract:migrate` (Flyway → an `external: true`
Delta table + read **grants**) is a **separate publish step** (the App→Domain governance
boundary held out of scope above), so it is **instructor/setup-only, never a trainee
step**; the contracts still ship as `contract/<d>.odcs.yaml` **spec files** (the shape the
gold model must match). Trainee Databricks scope therefore reduces to the already-confirmed
`dbt:run/test`, `databricks bundle deploy -t local`, and triggering the DAG — no
`contract:migrate`, no grant management.

### Verify (challenge 04)

`mise run challenge:verify 04` follows the track's offline/live discipline:

- **Offline (default):** `dbt parse`, the `atlas_elt` `ref()` graph compiles, the
  `atlas_elt_*` DAGs import cleanly, and `databricks bundle validate -t local` passes.
  (`bundle validate` shells out to Terraform; a corp-mirror/clock failure there is
  environmental, not a challenge defect — see "Implementation notes (as-built)".)
- **Live (marked `integration`):** `mise run dbt:run/test atlas_elt` on Databricks,
  `databricks bundle deploy -t local`, and a triggered DAG run. (No `contract:migrate` —
  see Databricks permissions above.)

### Removing `atlas_elt_demo`

Small, contained change:

- **Delete** `data_products/atlas_elt_demo/`.
- **`docker-compose.override.yml`** — default `AIRFLOW_VAR_DATA_PRODUCT_NAME` →
  `atlas_elt`.
- **`.devcontainer/README.md`** — repoint the `clients_job` troubleshooting example to
  an `atlas_elt` dataset.
- **`data_products/test_atlas_local_runtime_contract.py`** and
  **`test_devcontainer_dind_wiring.py`** — repoint the ~14 structural `atlas_*` tests to
  `data_products/atlas_elt/` (they encode good paved-path shape); drop any that assert
  the demo's `select *` passthrough shape.
- Historical `docs/` referencing `atlas_elt_demo` stay as history.

Acceptance: `pytest data_products -q` and `mise run verify:local-dev` are green, and no
functional `atlas_elt_demo` reference remains outside historical docs.

## Open decisions — none remaining

All decisions are resolved: challenge home (`challenges/` + top-level `data_products/`),
dataset decomposition (entity-centric ~10–12), medallion-vs-alignment placement,
one-product capstone (Option A), first-class offline/live tests, contract-publish scope
(instructor-only), and challenge-03 CI (no handling needed — CI keys off `databricks.yml`).
The design is ready to become a phased implementation plan (see Execution approach).

## Risks

1. **Airflow 2.10 → 3.x drift.** Both challenge 03's Cosmos DAG and challenge 04's
   blueprint DAGs must load under Airflow 3.x / cosmos 1.15 — verify DAG load early
   (zero import errors + one green triggered run).
2. **Trainee Databricks scope.** The challenge needs only `dbt:run` + `bundle deploy` +
   DAG trigger (all confirmed); contract publish via Flyway is deliberately out of scope,
   so grant permissions can't block it.
3. **dbt version drift (02/04).** Mitigate with a `dbt build` smoke check on the shared
   adapter.
4. **Removing `atlas_elt_demo` breaks its tests.** Repoint them to `atlas_elt` as part
   of the same change.
5. **Native-flow regression.** Mitigate with the `challenges/` ignore set and a
   before/after `verify:local-dev` parity check.

## Success criteria

1. Fresh devcontainer + one `mise run setup:databricks` → each of 00–03 is green via a
   single command, with no per-challenge auth setup.
2. `data_products/atlas_elt` builds (medallion) on Databricks, its Asset Bundle
   validates (deploys if permitted), and its `atlas_elt_*` blueprint DAGs load with
   zero import errors; `atlas_elt_demo` is removed with all functional references
   repointed.
3. Native data products/DAGs are unchanged; the challenge **offline** suite passes by
   default; **live** checks run only under `CERT_INTEGRATION_TESTS=1`; `pre-commit`
   stays green.

## Execution approach

Because the two parts are coupled (Part 2 uses the foundation, and both share one
devcontainer + Databricks schema + local Astro on port 8080), this is **one phased
effort by one agent using subagents** (`superpowers:subagent-driven-development`) — not
two parallel Copilot windows, which would contend over the single workspace and edit
the same shared files. Suggested phasing:

- **Phase 0 — Foundation:** `challenges/` home, `challenge:*` mise tasks, the
  `tests/challenges/{offline,live}` scaffold, ignores, docs pointer.
- **Phase 1 — Challenges 00–03** (Part 1).
- **Phase 2 — Capstone + retire `atlas_elt_demo`** (Part 2).

One implementation plan, written once these designs are approved.

## Implementation notes (as-built, 2026-07-28)

Refinements discovered while implementing the plan. These correct and extend the
sections above; the challenge READMEs and `verify.sh` scripts are the source of truth,
and `tests/challenges/offline/` locks the contracts below.

**Verify scripts are the learner gate (all challenges).** `challenge:verify <NN>` builds
the trainee's own working tree — it must go **RED on unsolved stubs and GREEN when
solved**. Challenge dbt runs go through `dbt_wrapper.py` with an explicitly resolved
interpreter so they don't depend on whichever `dbt` is on `PATH`.

**02 — raw sources ship as dbt seeds.** The preflight provisioned the six raw sources with
a manual `provision-raw-sources.sql` script that was never ported, so they existed in no
catalog. Its data now ships as CSV seeds (`challenges/02-dbt-pipeline/dbt/seeds/*_raw.csv`)
— the author's own values (NAV reconciles to `seed_custodian_nav` within 1 bp), delivered
through the dbt/mise flow instead of a manual SQL step; `sources.yml` pins each source's
`database`/`schema` to the dbt target so `source()` resolves to the seeded relation.
`verify.sh` seeds → runs → tests; `mise run challenge:seed 02` loads them ad-hoc.

**02 — scaffolding restore (as-built, trainee walkthrough).** A later trainee walkthrough
found the port had also dropped the dbt project's `models:` block and both `schema.yml`
files, so several steps failed even on a fresh clone. Restored: the `models:` block
(`+tags` for `--select tag:staging` in S5, `+materialized` view/table for S6, and the marts
`OPTIMIZE … ZORDER` post-hook for C9) — shipped in `dbt/` **and** `stubs/` so
`challenge:reset` no longer clobbers the seed post-hook (whose loss had been erroring
`source freshness` STALE in S3); `marts/schema.yml` (ships, per C5); and `staging/schema.yml`
(authored in S8, so `solution/` only). The capstone mart `agg_fund_daily_exposure` and its
`reconcile_daily_exposure` test are now trainee-created in C10 rather than shipped as stubs
(the placeholder capstone couldn't run the marts ZORDER post-hook and the pre-solved
reconcile test referenced columns it lacked, so C7's full build broke; and S2 counts ten
models); `assert_nav_within_tolerance` ships as a failing stub (C6 "Complete"). The three
`show --inline "<SQL>"` guide checks (mise word-splits the quoted SQL; `select *`
glob-expands to the repo listing) became `show --select` / build-log materialization checks,
matching challenge 03. Verified in the devcontainer: `verify 02` green (8 seeds, 11 models,
17 tests), freshness passes on all five feeds, and C7 passes with the capstone un-created.

**03 — verify is a static wiring gate.** A full Airflow DagBag load renders the Cosmos
`DbtTaskGroup` via `dbt ls`, which only completes inside the configured astro runtime (a
working OAuth `databricks_default` connection). So `challenges/03-airflow-orchestration/
verify.sh` statically checks the authored wiring (`start → source_freshness_check →
dbt_pipeline → publish_to_catalog → end`) with `ast` — fast, deterministic, and with no
Airflow/Cosmos/dbt/auth dependency. Running the pipeline for real stays in the guide's
`astro dev start` / trigger steps.

**03 — astro-runtime fixes (so the DAGs load + run).** Registering
`portfolio_analytics_daily` and `portfolio_analytics_submit_run` in astro required four
fixes (verified in a running astro: 0 import errors, both DAGs registered):
1. **sys.path** — `data_products/` mounts as the dags folder, so a product's sibling
   packages (`callbacks`, `include.alerting`) aren't importable. A local-only
   `airflow_local_settings.py` (mounted via `docker-compose.override.yml`) adds each
   product's dir + `dags/` to `sys.path`.
2. **Cosmos dbt path** — the Astro image keeps dbt in an isolated venv
   (`/home/astro/.venv/cosmos`); the `DbtTaskGroup` sets
   `ExecutionConfig(dbt_executable_path=…)` (env-overridable).
3. **Cimon required tags** — DAGs carry `usage-id`/`cost-center` tags (repo convention,
   `data_products/blueprints_loader.py`).
4. **Cimon-blocked operators** — `BashOperator` is on Cimon's high-risk block-list (with
   `SSHOperator`/`DockerOperator`/…); the freshness gate + publish task use
   `PythonOperator` callables. The guide teaches the `PythonOperator` pattern accordingly.

**03 — full DAG run in astro (as-built, beyond parse).** Registration (0 import errors) is
necessary but not sufficient: a real `astro dev start` + trigger surfaced more issues that
had to be fixed for a green end-to-end run (now verified — the DAG runs **24/24 tasks
green**: freshness gate → Cosmos `dbt_pipeline` → publish):
5. **Freshness-gate auth** — the gate shelled `dbt source freshness` through the static
   `auth_type: oauth` profile, which in the astro container falls back to interactive
   external-browser OAuth and **hangs the task**. It now reads the fresh OAuth access token
   from the `databricks_default` connection (kept current by the token refresher) and runs
   dbt against a token-auth `airflow` profile target — the same credential Cosmos uses.
6. **Cosmos profile mapping** — `DatabricksOauthProfileMapping` is for M2M service
   principals and needs `client_id`/`client_secret`; the local connection carries only a
   bearer token, so Cosmos raised *"Could not find a value for secret field client_id"* and
   the pipeline never ran. Switched to `DatabricksTokenProfileMapping`, passing `http_path`
   in `profile_args` (the local connection has none in its extras).
   > **Superseded 2026-07-31:** the DAG now reads the profile directly via
   > `ProfileConfig(profiles_yml_filepath=...)` (no profile mapping). Even the token mapping
   > did a task-time `BaseHook.get_connection` lookup that intermittently failed in
   > Airflow-3 local `astro dev run dags test`; reading `profiles.yml` (target `dev`, token
   > auth) avoids it. See
   > `docs/superpowers/specs/2026-07-31-portfolio-airflow3-dag-stability-review-design.md`
   > and the Challenge-03 rows in `challenges/CHANGES.md`.
7. **Schema env into containers** — `docker-compose.override.yml` now forwards
   `DBT_SCHEMA`/`DBT_CATALOG` so the DAG resolves the trainee's `training_<user>` schema
   instead of falling back to `training_student`.
8. **Data provisioning** — the DAG's four raw feeds are provisioned by reusing challenge
   02's seed step (`mise run challenge:seed 02`) into the same schema, with a seed
   post-hook refreshing `_extracted_at` to `current_timestamp()` so the freshness gate
   passes on a green run.
9. **Cold-start env capture** — items 6–7's `http_path`/`DBT_SCHEMA`/`DBT_CATALOG` are read
   from the shell environment **at `astro dev start` time** (Cosmos needs `http_path` at DAG
   **parse** time, and parse-time connection reads are deliberately avoided for DagBag
   safety). Starting the stack before `mise run setup:databricks` finished writing
   `~/.config/dpc/databricks.env` — easy to do during the devcontainer's multi-minute
   first-run initialization — leaves the containers with an empty env, so Cosmos and the
   gate fail with *"The config 'http_path' is required"*. Mitigations: the guide boots the
   stack in the **Prerequisites** (after setup + seeding), warns to start it only once setup
   has finished, and says to run `astro dev restart` on a cold start; and the freshness gate
   now captures dbt's output and reports a connection failure (missing `http_path`) with an
   actionable restart hint, distinct from a genuine stale-feed breach — it previously
   reported "breached error_after" for **every** failure.

**03 — guide CLI commands (as-built).** The guide's Airflow CLI examples were bare
`airflow …` (Airflow runs inside the astro containers, so it is not on the devcontainer
PATH) and Airflow-2 syntax; they now use `astro dev run …` with Airflow-3 syntax (e.g.
`dags list-runs <dag>` positional, not `-d`). The step-9 parity check uses `dbt show
--select <model>` because `mise run challenge:dbt -- show --inline "<SQL>"` word-splits the
quoted SQL.

**03 — Phase 2 checks (as-built).** The production-ops sub-challenges verify via `pytest`,
`grep`, and `mise run challenge:verify 03`. Fixes so they run for a trainee: (1)
`test_dag_structure.py` is now a **static** ast/text test (no DagBag — Airflow lives only in
the astro containers) that checks the callbacks + SLA + no-secrets and passes on the stub
and the solution alike; the wiring chain stays the `verify.sh` learner gate. The three
copies (live/stub/solution) are identical, and the old `test_primary_dag_is_stubbed_for_training`
(which failed once the DAG was wired) is dropped — the "ship a stub" contract lives in
`tests/challenges/offline/test_ch03.py`. (2) The guide's `python -m pytest` becomes bare
`pytest` and the `python -c "import yaml"` panel count becomes a `grep`, because the
trainee's default `python` (`.venv`) lacks pytest/PyYAML (deps install `--system`). (3) The
"no Slack/vendor" greps are scoped to real usage (SDK / URL / `alert_channel`), not the bare
word the files use to document the anti-goal.

**04 — trainee walkthrough (as-built).** A fresh-eyes subagent walkthrough of the capstone
surfaced the real gaps. The port shipped `dbt_project.yml` with a bare
`models: {+materialized: view}` and **no alignment tags**, so the guide's
`--select tag:source-aligned|domain-aligned|consumer-aligned` build flow matched 0 nodes and
the whole capstone cascaded into `TABLE_OR_VIEW_NOT_FOUND`. Fixed by declaring the medallion
tags folder-by-folder (`datasets/<ds>/dbt/{staging,integration,prepared}` → source- / domain-
/ consumer-aligned) so a trainee's authored SQL inherits its layer tag; a full `dbt build`
then runs 40/40 green. Guide §4/§6 `show --inline "<SQL>"` → `show --select` (mise word-split,
same as 02/03). And `databricks bundle validate` → Terraform `openpgp: key expired` is an
environment/clock artifact (not a challenge defect); `verify.sh` now runs it as a **non-fatal
warning** so it no longer aborts the gate, letting the dbt parse/compile checks pass.
Everything else the subagent flagged was downstream of the missing tags or an inline-authored
step (exposures, generic/relationship tests) that passes once authored.
