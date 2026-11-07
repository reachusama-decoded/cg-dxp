# Project setup: Portfolio Analytics

Use the supplied training container and its managed environments. The terminal and Astro worker each need a working dbt-databricks connection. Follow the prepared environment setup before running a project.

## Terminal boundary and ownership

Open the training project in the dev container, run `pwd`, and locate the extracted learner bundle. From the bundle root, set `DC_RUNTIME` to the absolute `practice/portfolio-runtime` directory. After changing into an attempt, use that absolute path. Preparation always refuses an existing destination. Each checkpoint is independent; the instructor baseline supplies earlier models without requiring a completed previous attempt.

Sign in before recording using the delivered `mise run setup:databricks`. After starting Astro, use `mise run databricks:oauth-refresh`. The helper reads `DBT_ACCESS_TOKEN` at execution time; do not save it in evidence or copy `.env` into delivery. Validate Python and installed dbt-core/dbt-databricks versions at both terminal and worker boundaries. The source Dockerfile selects Runtime `3.1-17-base` and `/home/astro/.venv/cosmos/bin/dbt`; check the running worker rather than inferring its installed versions from the Dockerfile.

Use the approved pre-provisioned catalog/schema and warehouse. Reconcile `DBT_SCHEMA`, `DATABRICKS_SCHEMA` and `V2_DB_SCHEMA` to the same value; reconcile `DBT_HOST` with `DATABRICKS_HOST`, `DBT_HTTP_PATH` with `DATABRICKS_HTTP_PATH`, and catalog aliases. `ready` refuses missing/conflicting aliases. There is no username, catalog or warehouse fallback. Set a unique `DC_RELATION_PREFIX`, for example `dc_alex_a01`; choose a different prefix for each simultaneous attempt. All raw seeds, models and snapshots use that prefix in the one assigned schema. Extra-schema configs fail compilation.

From the extracted learner bundle root, in the prepared terminal:

```bash
export DC_RUNTIME="$PWD/practice/portfolio-runtime"
export DC_RELATION_PREFIX=dc_alex_a01
python "$DC_RUNTIME/lab.py" prepare .local/dbt-foundations --checkpoint foundations
cd .local/dbt-foundations
python "$DC_RUNTIME/lab.py" ready .
dbt seed --project-dir . --profiles-dir . --target local --target-path target --full-refresh
dbt build --project-dir . --profiles-dir . --target local --target-path target
python "$DC_RUNTIME/lab.py" check .
```

The unfinished starter must fail completion checks. Author its required files first. `local`, `dev` and `airflow` all mean Databricks in this adapted profile. The CG capstone has separate workspace/profile checks in [its project guide](../../../cg-public-products/project/README.md#your-working-folder). Never assume `/Volumes/training_dev/cspn_sys/dbt_state` is a mounted local directory.

## Inputs, dates and evidence

The eight Portfolio CSVs include six raw tables. Seeding only the product's two supplementary files cannot prepare its raw sources. `lab.py prepare` copies all eight exact supplied CSVs into each attempt. Sources reference prefixed raw seed tables in the target catalog/schema. No new schema is required.

Historical business dates are 20–21 May 2026. `_extracted_at` means ingestion observation time, not the position date. Before a freshness demonstration, restore baseline and record a new sample ingestion time explicitly:

```bash
python "$DC_RUNTIME/lab.py" restore . --observed-at 2026-10-08T09:00:00Z
dbt seed --project-dir . --profiles-dir . --target local --target-path target --full-refresh
dbt source freshness --project-dir . --profiles-dir . --target local --target-path target
```

Use the actual preparation time rather than copying the example timestamp months later. This labelled teaching variation changes only load timestamps and retains a `preparation.json` record. Stale historical timestamps are an intended failure without this preparation. Presence, schema and population are separate from freshness.

`reference` computes expected values independently from copied CSVs using decimal arithmetic. `check` requires dbt artifacts and compares actual warehouse rows, keys and values. Retain `evidence.md`, the contract hash, selected configuration without credentials, run results, independent query outputs and observed versions. Check merge, snapshot and scheduled-run behavior in the actual Databricks/Astro environment.

## Astro boundary

The supplied compose override mounts `data_products/` at `/usr/local/airflow/dags`. Verify the actual running mounts with Docker before staging. A terminal attempt elsewhere is not worker-visible. Prepare an Airflow checkpoint, complete its graph/tasks, then stage that attempt into a new `data_products/<prefix>` using `stage-astro --astro-root` and the exact prepared Astro project root. Never overwrite an existing destination. The staged project uses its own `project/`, `runtime/`, `target/` and `evidence/`. The helper enables worker writes only in that owned project’s target/log directories and its evidence directory; code and source fixtures retain their original read permissions. Inspect actual worker write access and the configured host before scheduling; the DAG ID is `<prefix>_portfolio_daily`. The worker's `DC_RELATION_PREFIX` and catalog/schema/warehouse must match the terminal seed route. `DC_WORKER_DBT_BIN` selects the inspected worker executable.

The assigned classroom DAG uses a two-minute scheduled timetable, catchup=False and one active run, so success/failure/repair can be rehearsed within the protected block. The historical May business partition stays explicit. A daily production cadence is a separate design choice. Unpause only the owned DAG while collecting evidence and pause it afterward. From the actual prepared Astro root, use `astro dev run dags unpause "${DC_RELATION_PREFIX}_portfolio_daily"` and afterward `astro dev run dags pause "${DC_RELATION_PREFIX}_portfolio_daily"`. The assigned DAG uses the delivered scheduled runtime and the delivered noninteractive connection. Host/token are templated from `databricks_default` into task arguments, resolved at execution time. Token refresh, expiry and restart must be rehearsed; a fresh CLI token alone does not authenticate a worker. Only run/partition identifiers go through XCom. Tables remain in Databricks. The final task writes publication evidence after independent checks; it does not issue grants, notify consumers or publish a product.

Inspect a fresh *scheduled* run in graph/grid/log and retain its exact ID and task states. Use the connected API checker with `DC_AIRFLOW_API_URL` and an ephemeral `DC_AIRFLOW_API_TOKEN`. Demonstrate success, intentional quality failure with evidence task blocked, repair, same-business-date replay and correction. A `dag.test()` or import success cannot close this gate. The fixed fixture partition parameter is explicit; the scheduled logical date is retained separately and does not manufacture newer holdings.

## Bounded variations and cleanup

`mutate --drill correction` adds 1,000 GBP to one copied holding. Reseed, run the incremental model twice, and inspect the original key: one row, corrected value, no duplicate. Baseline synthetic-unit value reconciliation is expected to fail on that variation because the reference synthetic-unit comparison fixture is unchanged. `missing-fx` removes the 20 May GBP rate: matched-enrichment checks must fail and downstream evidence must be blocked. `fund-change` changes a copied fund name: snapshot before and after, prove the original closed validity interval and one current row. Baseline input has no pre-existing correction or snapshot history.

Restore using `restore`, reseed and build. Restoring CSVs does not erase snapshot history. Use a new prefix/attempt for a fresh history sequence. `cleanup-sql` emits statements only for manifest-recorded owned relations after validating catalog/schema/prefix; review and execute them in the assigned namespace. Remove only the staged directory whose `ownership.json` matches this attempt; delete only its DAG metadata after retaining evidence. For shared-runtime checks, use two prefixes. Confirm token refresh and restart recovery, then remove attempt A while verifying attempt B still works.

## Canonical v2 preparation and evidence

Prepare v2 attempts from the training project root using mise. Use `mise run challenge:v2:prepare dbt phase-one-certified`, `mise run challenge:v2:prepare airflow phase-one-certified`; advanced uses `phase-two-proficient`. Direct dbt commands run inside that copied attempt. The checkpoint helper commands above prepare the same supporting projects; follow the phase README for your assignment. The Portfolio support download alone does not install the managed container or replace the full updated client project.

For Airflow, prepare and seed inside the copied `project/`, then stage the owned root through `runtime/lab.py stage-astro`. Supply a real recorded extraction observation time if freshness needs a timestamp-only refresh. Each tiny build refreshes both May dates; checked receipts select four fund/date rows for the explicit partition. Use `mise run challenge:v2:airflow-evidence` with three fresh scheduled IDs and the rehearsal start time before live phase verification. Keep the API report, worker logs and warehouse comparison together. Record any authentication, restart or isolation check you could not complete.
