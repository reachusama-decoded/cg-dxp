# Portfolio-Analytics Airflow-3 DAG Stability Fix — Review & Design

> Status: **REVIEW — not ready to merge.** Analysis of branch
> `feature/portfolio-airflow3-dag-stability` (commits `ecacaa1` "Stabilize portfolio DAG
> execution and dbt auth in Airflow 3", `ad13664` "Fix challenge dbt show instability in
> portfolio profile") against `main`.
> Purpose: the branch attempts to fix a **Windows trainee's failure in Challenge 03
> (airflow orchestration), steps 8–9**. This document records what the branch changes,
> what was verified by running tests in the repo, the issues found, and the remediation
> required before merge.

## Why this document is structured this way

The order is: intent → change inventory → in-repo verification → evidence-backed findings
→ verdict → remediation. This lets a reviewer trace every verdict back to a concrete test
result or file citation rather than to opinion, and separates *confirmed blockers* from
*concerns* and from an initial finding that testing actually **corrected**. It complements — does not
duplicate — the existing `docs/superpowers/specs/2026-07-27-training-challenges-and-atlas-capstone-design.md`
(the challenge-port design) and `challenges/CHANGES.md` (the change-and-why log); those
describe the *pre-branch* state, which this branch partially reverses.

## Context — the failure being fixed

Challenge 03 §8 ("Retries and exponential backoff") and §9 ("First full run") both execute
a full local Airflow 3.1 run of the DAG inside the astro devcontainer
(`astro dev run dags test|unpause|trigger portfolio_analytics_daily`) — see
`challenges/03-airflow-orchestration/README.md` lines 623–711. A Windows trainee hit an
error at these steps. Airflow 3.1's local `dags test` execution model is known to surface
transient supervisor/heartbeat races and a listener-hookspec change, so the branch targets
that runtime plus dbt result-fetch stability.

Two structural facts about Challenge 03 matter for the verdict:

1. **The trainee's single authored deliverable is the dependency wiring.** README §6 and
   the overview state the starter `data_products/portfolio_analytics/dags/portfolio_analytics_daily.py`
   "ships complete and parseable — every task is already built. The single `# TODO` is the
   dependency wiring you add in section 6" (README lines 18–24, 166–168, 504–524). The
   wiring chain is "the learner deliverable" checked by `mise run challenge:verify 03`
   (README lines 1307–1308).
2. **Three copies of the DAG exist and must stay in their roles.** The live/working copy
   `data_products/portfolio_analytics/dags/portfolio_analytics_daily.py`; the pristine
   starter `challenges/03-airflow-orchestration/stubs/dags/portfolio_analytics_daily.py`
   (carries the `# TODO`, restored by reset); and the reference
   `challenges/03-airflow-orchestration/solution/dags/portfolio_analytics_daily.py`
   (carries the finished wiring). `mise run challenge:reset 03` overwrites the live copy
   from the stub: `cp -R "$DIR/stubs/." data_products/portfolio_analytics/` (`.mise.toml:260`).

## Change inventory (branch vs `main`, 4 files)

| File | Change | Intent |
|---|---|---|
| `airflow_local_settings.py` (+226 lines) | Three runtime monkey-patches: (a) cimon listener `on_task_instance_failed/success` made compatible with the Airflow-3.1 listener hookspec (drops the removed `session` param); (b) `ActivitySubprocess._send_heartbeat_if_needed` softened to swallow transient `queued→running` and `failed/up_for_retry` heartbeat conflicts; (c) `ActivitySubprocess._on_child_started` retries transient start errors and neutralizes duplicate-start conflicts by `SIGKILL` + force-marking the launcher `SUCCESS`. Loaded via `docker-compose.override.yml:8` mount to `/usr/local/airflow/airflow_local_settings.py`. | Stop local Airflow-3.1 `dags test` from failing nondeterministically on supervisor/heartbeat races and a plugin-validation error. |
| `data_products/portfolio_analytics/dbt/profiles.yml` | `threads: 4→1`; add `connection_parameters: {_disable_pandas: true}`; strip URL scheme from `host`; switch `local` and `dev` from `auth_type: oauth` to `token: "{{ env_var('DBT_ACCESS_TOKEN', env_var('DATABRICKS_TOKEN','')) }}"`. | Reduce concurrency/result-fetch flakiness; make the adapter build a valid host; align auth with the token the runtime injects. |
| `challenges/02-dbt-pipeline/dbt_profiles/profiles.yml` | Add `connection_parameters: {_disable_pandas: true}` to all three targets. | Same dbt result-fetch stability for challenge 02. |
| `data_products/portfolio_analytics/dags/portfolio_analytics_daily.py` | Cosmos `DatabricksTokenProfileMapping` → `profiles_yml_filepath`; add `_build_dbt_runtime_env()` reading host/token from `databricks_default`; freshness gate picks target dynamically with try/except; `max_active_tasks=1`; `RenderConfig(test_behavior=TestBehavior.AFTER_ALL)`; `operator_args["env"]=DBT_RUNTIME_ENV`. **Also replaces the `# TODO` with the real wiring line** `start >> source_freshness_check >> dbt_pipeline >> publish_to_catalog >> end` (line 202). | Avoid intermittent `BaseHook` connection lookups at task-execution time; run tests after all builds; and (side effect of end-to-end testing) wire the chain. |

## In-repo verification performed

All tests were run on the macOS host against this branch's working tree. dbt-core /
databricks-sql-connector are not installed on the host, so the two dbt/runtime-dependent
questions were answered from authoritative source (repo env wiring; the connector's own
source), not by executing dbt.

| # | Question | Command / evidence | Result |
|---|---|---|---|
| T1 | Does the shipped (wired) starter make the challenge gate pass with no trainee work? | `mise run challenge:verify 03` | **PASS** — `[pass] DAG parses and wires: start -> … -> end`. Confirms the deliverable is pre-solved on a fresh clone. |
| T2 | Does the stub that `reset` restores fail the gate (i.e., does reset re-break it)? | `PORTFOLIO_ANALYTICS_DAG=…/stubs/dags/portfolio_analytics_daily.py bash challenges/03-airflow-orchestration/verify.sh` | **FAIL (exit 1)** — "The DAG is not wired correctly. Missing dependencies …". The stub is unwired *and* carries none of the stability fixes (see T5). |
| T3 | Is `airflow_local_settings.py` import-safe when airflow/cimon are absent (clone-safe)? | `python3 -c "runpy.run_path('airflow_local_settings.py')"` with no airflow installed | **PASS** — executed with no unhandled exception; the `try/except` guards no-op cleanly. |
| T4 | Is `_disable_pandas` a real, accepted connection parameter (pinned `databricks-sql-connector==4.1.5`, `.devcontainer/requirements.txt:7`)? | Source: `databricks/databricks-sql-python` → `src/databricks/sql/client.py`: `self.disable_pandas = kwargs.get("_disable_pandas", False)` + unit tests `test_disable_pandas_respected/_path` | **VALID** — accepted flag that disables the pandas/pyarrow deserialization path. Underscore-prefixed = private/unstable API. |
| T5 | Do the stub and solution DAGs carry the branch's stability fixes? | `grep -E "DBT_RUNTIME_ENV|TestBehavior|max_active_tasks|profiles_yml_filepath" stubs/… solution/…` | **NO** — none present in either; only the live copy has them. Live diverges 60 lines from stub and 66/118 from solution. |
| T6 | Under `mise`, does the OAuth→token profile switch still authenticate? | `.mise/env.sh:74` `export DBT_ACCESS_TOKEN="$_oauth_token"` (minted from `databricks auth token` in OAuth mode), with `~/.databrickscfg` fallback at `.mise/env.sh:85–86` | **YES** — `DBT_ACCESS_TOKEN` is populated on every mise run, so `token: env_var('DBT_ACCESS_TOKEN', …)` resolves. (Downgrades the auth concern — see R1.) |

## Findings

### Blockers (training integrity — confirmed)

**B1 — The branch leaks the learner's single deliverable.** The wiring line
`start >> source_freshness_check >> dbt_pipeline >> publish_to_catalog >> end` is committed
into the shipped starter (`data_products/portfolio_analytics/dags/portfolio_analytics_daily.py:202`),
replacing the `# TODO` that Challenge 03 §6 asks the trainee to author. **T1 confirms** a
fresh clone passes `mise run challenge:verify 03` with zero trainee work, so §6 is
pre-solved. Why it matters: §6 is the *only* authored deliverable in Phase 1; shipping it
solved defeats the challenge.

**B2 — The fix is not clone-safe: `reset` wipes it and the reference copies are stale.**
`mise run challenge:reset 03` restores the live DAG from the stub (`.mise.toml:260`).
**T5** shows the stub carries none of the stability fixes and **T2** shows it also fails
the wiring gate — so any trainee who resets (the documented recovery path) loses the entire
fix *and* re-enters the exact broken state the branch set out to repair. The `solution/`
copy is likewise un-updated, so the reference a trainee compares against now differs from
the live DAG by 66/118 lines. Why it matters: the memory contract for this repo is that
"challenge fixes must work on a fresh clone, not just the current machine"; a fix that only
lives in the live copy violates that.

### Concerns (should fix before merge)

**C1 — Docs not updated; now internally contradictory.** No `.md` changed on the branch and
both commit messages are bare titles. `challenges/CHANGES.md` still asserts (a) Cosmos uses
`DatabricksTokenProfileMapping` and (b) `local`/`dev` are "identical OAuth target[s]" — both
reversed by this branch. README §3 still teaches the OAuth targets. Why it matters: the repo
convention is to record *what changed and why* in `CHANGES.md`/docs; leaving them stale
misleads the next reader and breaks the "defend every deliberate change" intent of that log.

**C2 — Monkey-patches are fragile and can produce a false green.** `airflow_local_settings.py`
patches **private** Airflow SDK internals (`airflow.sdk.execution_time.supervisor`) that are
version-locked to Airflow 3.1 and will drift silently on upgrade. The highest-risk path,
`_patched_on_child_started`, force-sets a task instance to `SUCCESS` (`exit_code=0`) on a
detected duplicate-start conflict; if that heuristic misfires, a task that never ran is
reported green — dangerous in §9, whose lesson is "confirm the run lands green and the marts
are populated." Mitigations confirmed: **T3** shows the file is import-safe when deps are
absent, and it is mounted **only** into the local astro devcontainer
(`docker-compose.override.yml:8`), so the blast radius is the local training runtime, not
production. Why it matters: acceptable as a *local* training aid, but it needs a version
guard and a comment tying it to the exact Airflow version, and the SUCCESS-forcing branch
should be narrowed or removed.

**C3 — The fix is not verified end-to-end.** `mise run challenge:verify 03` is a *static*
AST/wiring check (see `challenges/03-airflow-orchestration/verify.sh`); **T1/T2 exercise
only parsing**, never the runtime supervisor path that was failing. Nothing in the branch
demonstrates that the real §8–9 `astro dev run dags test` now passes on the target setup.
Why it matters: the very failure being fixed lives in a code path the repo's gate cannot
reach, so "verify is green" is not evidence the Windows error is resolved.

### Corrected during review (was flagged, testing resolved it)

**R1 — OAuth→token profile switch is *not* a functional break.** Initial read flagged
switching `local`/`dev` from `auth_type: oauth` to a `DBT_ACCESS_TOKEN` token as a
regression for OAuth-only setups, because `mise run challenge:dbt 03` uses `--target local`
and that is §9's own parity check. **T6 disproves the break:** `.mise/env.sh:74` mints
`DBT_ACCESS_TOKEN` from the OAuth session on every mise run (with a `~/.databrickscfg`
fallback), and token-driven profiles are the repo-wide convention. Residual issue: it is an
**undocumented reversal** of the documented OAuth design (feeds C1) and marginally lowers
auth resilience by depending on the minted token / `.databrickscfg` fallback rather than
native u2m OAuth. Not a blocker.

### Verified low-risk / acceptable

`_disable_pandas: true` (**T4** — valid, disables the pandas/pyarrow fetch path; note it is
a private flag on the pinned `databricks-sql-connector==4.1.5`), `threads: 1`, host
scheme-strip, `RenderConfig(test_behavior=AFTER_ALL)` (tests run after all builds so
relationship tests don't reference not-yet-built marts), `max_active_tasks=1`, and the
challenge-02 `_disable_pandas` addition. The cimon-listener hookspec patch is a reasonable
Airflow-3.1 compatibility shim.

## Merge verdict

**Do not merge as-is.** The intent is sound and the runtime hardening is largely
reasonable, but **B1** (leaks the deliverable) and **B2** (reset wipes the fix; stale
reference copies) are training-integrity blockers, and **C1–C3** must be addressed. The
auth switch (R1) and the dbt result-fetch changes are acceptable once documented.

## Remediation plan (to make it mergeable)

1. **Un-leak §6 and keep the three copies consistent.** Apply the runtime fixes (profile
   handling, `_build_dbt_runtime_env`, `max_active_tasks`, `TestBehavior.AFTER_ALL`,
   freshness-gate target logic) to **all three** DAG copies — stub, live, and solution — but
   **revert the wiring line** in the stub and the shipped live copy back to the `# TODO`, so
   §6 remains the trainee's authoring task. Keep the finished `>>` chain **only** in
   `solution/dags/portfolio_analytics_daily.py`. Verify: `mise run challenge:verify 03`
   should now **FAIL** on a fresh clone until the trainee wires it (matching T2), and
   `mise run challenge:reset 03` must leave a stub that still contains the stability fixes.
2. **Guard the monkey-patches (C2).** Gate `airflow_local_settings.py` on an explicit
   Airflow version check, add a comment pinning the exact version the private
   `supervisor` internals were copied from, and narrow or remove the
   `_on_child_started` branch that force-marks a task `SUCCESS` so a misfire cannot mask a
   task that never ran.
3. **Document the change and its rationale (C1, R1).** Add a Challenge-03 row to
   `challenges/CHANGES.md` covering the Cosmos `profiles_yml_filepath` switch, the
   `local`/`dev` token-auth change, `_disable_pandas`, `max_active_tasks=1`,
   `TestBehavior.AFTER_ALL`, and the `airflow_local_settings.py` runtime patches; update
   README §3 if it still teaches OAuth targets; and rewrite the two commit messages with a
   what/why body.
4. **Prove §8–9 end-to-end (C3).** Run the actual challenge steps in the devcontainer on the
   affected (Windows) setup — `astro dev start` → `astro dev run dags test
   portfolio_analytics_daily 2026-05-04` (§8) → unpause/trigger (§9) → confirm a green run
   and populated marts — and attach the evidence to the PR. A static verify pass is not
   sufficient.

## Evidence appendix

- Challenge steps: `challenges/03-airflow-orchestration/README.md:623` (§8), `:687` (§9),
  `:504–524` (§6 deliverable), `:166–168`, `:1307–1308` (wiring is the graded deliverable).
- Reset overwrites live from stub: `.mise.toml:260`. `challenge:dbt 03` uses
  `PROFILES_DIR=data_products/portfolio_analytics/dbt --target local` (`.mise.toml`,
  `challenge:dbt` task).
- OAuth token minting: `.mise/env.sh:56` (`unset`), `:74` (`export DBT_ACCESS_TOKEN`),
  `:85–86` (`.databrickscfg` fallback).
- `airflow_local_settings.py` mount: `docker-compose.override.yml:8`.
- Live wiring line (leak): `data_products/portfolio_analytics/dags/portfolio_analytics_daily.py:202`.
  Stub `# TODO`: `challenges/03-airflow-orchestration/stubs/dags/portfolio_analytics_daily.py:187`.
  Solution wiring: `challenges/03-airflow-orchestration/solution/dags/portfolio_analytics_daily.py:254`.
- Connector: pin `.devcontainer/requirements.txt:7` (`databricks-sql-connector==4.1.5`);
  `_disable_pandas` in `databricks/databricks-sql-python` `src/databricks/sql/client.py`.
- Raw test output for T1–T3 recorded in the review session (2026-07-31).
