# Findings, run 20261005T141153Z (session 2)

F-01 to F-05 are in `readiness.md`. Status: **fixed** (changed and re-verified),
**open** (tracked in devc.md), **workaround** (documented, not fixed at source).

| ID | Area | Finding | Status | Evidence / fix |
|---|---|---|---|---|
| F-06 | v2 tools | A container rebuild keeps `.local/v2-tools` and `.local/v2-airflow` on the bind mount but deletes uv's Python 3.11 (`/root/.local/share/uv/python`), so both venvs dangle. Rerunning `setup-v2-tools.sh` then failed: uv 0.11 refuses an existing venv. | fixed | `uv venv --clear` in `scripts/setup-v2-tools.sh`; rerun passes in 36 s |
| F-07 | dbt connected route | All 14 v2 `profiles.yml` used `auth_type: oauth`, which starts dbt-databricks' own browser login and hangs in the container. The repo's contract is the `DBT_ACCESS_TOKEN` delivered by `mise`. | fixed | profiles use `token: env_var('DBT_ACCESS_TOKEN')`; dbt p1/p2 and capstone p1/p2 pass live |
| F-08 | Git p2 | Zscaler returns 403 (HTML block page) for GitHub's REST contents `PUT`, so the "colleague" upstream edit can't be made through `gh api`. `git push` and GraphQL (`gh pr create`) work. | workaround | git-p2-04 now tells learners in their own sandbox to push the colleague change from a second clone |
| F-09 | verifier | Connected-route blind spot: the assigned schema keeps relations from earlier runs, so an untouched dbt p1 starter **passed** live (it read an old `fund_exposure`). | fixed | `drop_checked_relations()` before connected dbt/capstone/Astro runs; starter journeys now fail live (`suite.tsv`) |
| F-10 | verifier | Airflow p2 and Kafka p1 ship a starter identical to the solution (the tasks are operational). `verify` re-runs the chain itself, so it proves the runtime, not that the learner performed and recorded the run. | open | needs a learner evidence file (run ID, receipt, offset) that `verify` checks against Airflow/broker state |
| F-11 | Airflow Astro route | The company Astro runtime's Cimon DAG policy rejects the v2 DAG: required tag keys `usage-id`, `cost-center`. | fixed | tags added to the 5 v2 DAG files; Airflow p1 hint explains it; Airflow p1/p2 pass on Astro |
| F-12 | Astro auth | After the rebuild the OAuth→Airflow refresher was not running; `databricks_default` held an expired token and dbt in the worker got 403 on OpenSession. `dpc-check` only WARNs ("refresher heartbeat"). | workaround | `mise run databricks:oauth-refresh` before Astro runs. Open: start the refresher with `astro dev start` / post-start |
| F-13 | dbt p1 text | dbt-p1-05 "All tests must pass on a fresh build": on an empty database `dbt build` alone fails because sources don't depend on seeds. | fixed | Check text, manifest and instructor README now say `dbt seed`, then `dbt build` |
| F-14 | learner text | Fresh-context reconstruction (dbt p1, Docker p1, see below) found gaps: `workspace/evidence.md` location is ambiguous (16+ tasks); starter READMEs cite an "authored-file list" that doesn't exist; the dbt-p1-05 hint cites "YAML examples" not in the pack; querying DuckDB isn't taught; `docker run -it` has no non-TTY fallback; the `python:3.11-slim` pre-pull isn't checkable by learners; the negative-fixture copy in dbt-p1-05 is unspecified. | open | `.local/live/20261005T141153Z/journeys/reconstruction/{dbt,docker}-phase-one-certified/evidence.md` |
| F-15 | verifier | Git p2 live accepted any PR with reviews; it didn't bind the PR to the learner repo or exclude self-review. | fixed | requires PR head = learner `HEAD`, ≥2 commits, a review by another account; otherwise blocked (77) |
| F-16 | verifier | `airflow dags list-import-errors` exits 1 whenever any DAG has errors; the verifier treated that as failure and hid the real error. | fixed | parse the JSON, report only this workspace's errors |
| F-17 | verifier | Statement Execution API omits `columns` for an empty result. | fixed | tolerate a missing column list |
| F-18 | Astro | dbt 1.12 in the Astro worker probes `https://https://…` when `DATABRICKS_HOST` keeps its scheme. | fixed | live binding strips the scheme, as `portfolio_analytics_daily` does |
| F-19 | courseware | `designer/generated/*` is stale after the Git p2, dbt p1 and Airflow p1 text changes; `sync-v2-course.py` isn't ported (section 4) and its check needs pandoc, which the rebuild removed. | open | regenerate after porting |
| F-20 | capstone p2 solution | On Databricks `fees_paid / traded * 10000` divides two `decimal(38,6)` values, keeps 6 places and rounds `fee_bps_realized` to 0.01 bps: 944 of 1,028 portfolios were off by up to 0.005 bps from the raw-CSV oracle. DuckDB hid it. | fixed | solution and stretch README multiply first (`fees_paid * 10000 / traded`); diagnosis `.local/live/20261005T141153Z/diag_fee_bps.py` |
| F-21 | learner text | Fresh-context reconstruction of Git p1 and Airflow p1 (both pass) found: git-p1-03 calls the Owner/Grain edits "compatible" but the lines are adjacent, so the second merge conflicts before p1-04 teaches conflicts; lab folder name, escalation text and Owner value unspecified; Airflow p1 never tells learners to run `airflow db migrate` and `airflow dags reserialize` before `dag.test()` (it fails otherwise); receipt name/location, DuckDB inspection command, `--profiles-dir` and `dag.test()` exiting 0 on a failed run aren't covered; the Phase 1 "Starter behavior" text mixes in Phase 2. | open | reconstruction `evidence.md` in `journeys/reconstruction/{git,airflow}-phase-one-certified` |
| F-22 | learner text | The capstone p2 stretch README (learner pack) carries inherited `<details>Solution` blocks with complete SQL. | open | move assessed answers to `v2-solutions` (live prompt §7) |
| F-23 | verifier | Failures with an empty assertion message were reported as `"error": ""`. | fixed | reports now carry the exception type and failing line (`at`) |
| F-24 | connected route | One transient `Error during request to server` from the warehouse on the incremental `arrival_ledger` (dbt p2 solution journey); the same row passed on rerun. | observed | `suite.tsv` row marked `rerun:` |
| F-25 | verifier | The Astro live binding needs the DAG ID `v2_training_pipeline`, but no README names it; a learner DAG with its own ID passes offline and fails live. | open | bind whatever single `dag_id` the learner declares; reconstruction row in `results.tsv` |
| F-26 | dbt p2 text/verifier | dbt-p2-02 doesn't name the repaired mart's columns; the verifier queries `holdings` and `exposure` and also hard-codes `seeds/fund_labels.csv` and the `reconcile_exposure` test. The fresh-context learner's correct `fund_id, fund_name, market_value` mart fails offline and live. | open | name the columns in the README (they are Phase 1's) or make the verifier discover them; reconstruction rows in `results.tsv` |

## Fresh-context reconstruction (subagent, no access to solutions)

| Phase | Verifier | Wall time | Estimate |
|---|---|---|---|
| dbt p1 (DuckDB) | pass (A 2/150, B 2/100, C 1/0) | ~33 min | 75–110 min |
| Docker p1 (live) | pass (image built and run) | ~26 min | 60–90 min |
| Git p1 (local) | pass (9 commits, conflict merge with both parents) | ~20 min | 60–90 min |
| Airflow p1 (local `dag.test`) | pass (success, drill failure, repair) | ~25 min | see README |

Agent time isn't junior learner time; both remain unpiloted. Neither verifier reads `evidence.md`, so explanations, the negative test and the interactive shell task need instructor review.

## Git phase 2 remote route

Repository `CONMHAB_capgroup/dc-git-training` (private, created for this run with `gh`).
PR https://github.com/CONMHAB_capgroup/dc-git-training/pull/1: branch push, PR, review-response commit,
colleague commit on `main` (`350b6ec`), real conflict, merge (`7fb6d15`) with the upstream commit as
ancestor, push. Live verify: **blocked**, no review from another account. The PR is left open.
