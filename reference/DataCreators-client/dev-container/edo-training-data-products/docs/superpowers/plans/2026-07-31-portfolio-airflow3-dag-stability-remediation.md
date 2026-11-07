# Portfolio-Analytics Airflow-3 DAG Stability — Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make branch `feature/portfolio-airflow3-dag-stability` mergeable by removing the leaked Challenge-03 §6 deliverable, making every fix survive `mise run challenge:reset 03`, de-risking the Airflow-internal monkey-patches, and documenting the change — without losing the runtime stability the branch adds.

**Architecture:** Challenge 03 keeps three copies of each authored file — the live working copy under `data_products/portfolio_analytics/`, the pristine `challenges/03-airflow-orchestration/stubs/` (what `reset` restores via `cp -R stubs/. data_products/portfolio_analytics/`, `.mise.toml:260`), and the `challenges/03-airflow-orchestration/solution/` reference. Any fix that lives only in the live copy is wiped by reset, and the trainee's one authored line (the dependency wiring) must not ship pre-solved. This plan puts the stability fixes in **stub + live + solution**, keeps the wiring **only in `solution/`**, and gates the local-only Airflow patches behind a version check.

**Tech Stack:** Python 3.12 (Astro/Airflow 3.1 runtime), astronomer-cosmos, dbt-databricks, `databricks-sql-connector==4.1.5`, mise task runner, Astro CLI devcontainer.

> **Post-implementation note (2026-08-03).** The three-copy invariant in the Architecture and
> Global Constraints below was correct but enforced only by discipline, and it had already
> drifted: `check-dag-load.sh` was improved in the live copy (gaining the DagBag structural
> probes) while `stubs/` and `solution/` kept the older version. Because
> `mise run challenge:reset 03` does a blanket `cp -R stubs/. data_products/portfolio_analytics/`,
> running the documented reset **silently downgraded the live tooling script** and left an
> unexplained diff in `git status`.
>
> The three copies are now re-synced, and the invariant is automated by
> `tests/challenges/offline/test_ch03_stub_sync.py`, which fails if any tracked file under
> `challenges/03-airflow-orchestration/stubs/` differs from its counterpart under
> `data_products/portfolio_analytics/`. It compares git **index** blobs, not the working
> tree, so a trainee with the challenge half-finished does not trip it.
>
> Note the blast radius this constraint carries: reset copies *everything* in `stubs/`, not
> just trainee-authored files, so any drift in any mirrored file — including tooling — gets
> pushed into the live product.

## Global Constraints

- Any file under `data_products/portfolio_analytics/` that a fix touches MUST be mirrored into `challenges/03-airflow-orchestration/stubs/` and `challenges/03-airflow-orchestration/solution/` — reset copies `stubs/.` over the live tree (`.mise.toml:260`).
- The Section-6 wiring line `start >> source_freshness_check >> dbt_pipeline >> publish_to_catalog >> end` MUST NOT appear in the stub or the shipped live starter; it is the trainee deliverable and belongs ONLY in `solution/dags/portfolio_analytics_daily.py`.
- Verify the wiring gate with `mise run challenge:verify 03` (static AST check); it must FAIL on a fresh clone and PASS only after the trainee wires the chain.
- Keep `airflow_local_settings.py` import-safe when airflow/cimon are absent (it is mounted ONLY into the astro devcontainer via `docker-compose.override.yml:8`).
- The `local`/`dev` token targets are correct: `.mise/env.sh:74` mints `DBT_ACCESS_TOKEN` from OAuth, and the DAG's `profiles_yml_filepath` path needs a non-interactive token (OAuth `auth_type: oauth` hangs in the container). Do NOT revert them to OAuth; instead fix their stale comments and document the change.
- `mart`/model behavior is unchanged; do not touch dbt models, seeds, or `dbt_project.yml`.

---

### Task 1: Un-leak §6 and make the DAG fix reset-safe (stub == live, both unwired)

**Files:**
- Modify: `data_products/portfolio_analytics/dags/portfolio_analytics_daily.py:202` (remove wiring, restore TODO)
- Overwrite: `challenges/03-airflow-orchestration/stubs/dags/portfolio_analytics_daily.py` (copy the fixed-but-unwired live file over it)
- Test: `challenges/03-airflow-orchestration/verify.sh` (via `mise run challenge:verify 03`), `data_products/portfolio_analytics/tests/test_dag_structure.py`

**Interfaces:**
- Consumes: the branch's already-applied DAG fixes in the live copy (`_build_dbt_runtime_env`, `profiles_yml_filepath` profile config, dynamic freshness target, `max_active_tasks=1`, `RenderConfig(test_behavior=TestBehavior.AFTER_ALL)`, `operator_args["env"]`).
- Produces: a stub and live DAG that are byte-identical, carry all fixes, and are UNWIRED (the `# TODO`), so `reset` is content-neutral and §6 stays an authoring task.

- [ ] **Step 1: Capture the leak baseline (proves the current failure)**

Run: `mise run challenge:verify 03`
Expected: `[pass] DAG parses and wires: start -> ... -> end` — this is the bug: the shipped starter is pre-solved.

- [ ] **Step 2: Remove the wiring line from the live starter**

In `data_products/portfolio_analytics/dags/portfolio_analytics_daily.py`, replace the last line of the `with DAG(...)` block:

```python
    start >> source_freshness_check >> dbt_pipeline >> publish_to_catalog >> end
```

with the trainee TODO (identical to the stub's original line 187):

```python
    # TODO: wire start -> source_freshness_check -> dbt_pipeline -> publish_to_catalog -> end
```

- [ ] **Step 3: Verify the gate now fails (wiring is the deliverable again)**

Run: `mise run challenge:verify 03`
Expected: `[FAIL] The DAG is not wired correctly. Missing dependencies:` and exit code 1.

- [ ] **Step 4: Mirror the fixed-but-unwired live file into the stub**

Run:
```bash
cp data_products/portfolio_analytics/dags/portfolio_analytics_daily.py \
   challenges/03-airflow-orchestration/stubs/dags/portfolio_analytics_daily.py
```

- [ ] **Step 5: Verify stub and live are identical and both carry the fixes**

Run:
```bash
git --no-pager diff --no-index \
  challenges/03-airflow-orchestration/stubs/dags/portfolio_analytics_daily.py \
  data_products/portfolio_analytics/dags/portfolio_analytics_daily.py
grep -c "profiles_yml_filepath\|DBT_RUNTIME_ENV\|max_active_tasks" \
  challenges/03-airflow-orchestration/stubs/dags/portfolio_analytics_daily.py
```
Expected: the diff prints nothing (identical); the grep prints `3` (fixes present in the stub).

- [ ] **Step 6: Confirm the structural test still passes (callbacks/SLA/no-secret intact)**

Run: `pytest data_products/portfolio_analytics/tests/test_dag_structure.py -q`
Expected: PASS — `test_primary_dag_callbacks_and_sla_wired` and `test_no_secret_literals_in_dag_files` are green (the wiring is intentionally not asserted here; it is the `verify.sh` gate).

- [ ] **Step 7: Confirm reset-safety without mutating the tree**

Do NOT run `mise run challenge:reset 03` here — reset copies the whole `stubs/.` subtree over `data_products/portfolio_analytics/`, which would revert the profile fix that Task 3 has not yet synced. Reset-safety of the DAG follows from Step 5 (stub == live): reset copies stub→live, so identical files make it a no-op. The end-to-end reset proof runs once in Task 3 Step 4, after the profile is also synced. Re-assert here without mutating anything:
```bash
grep -c "profiles_yml_filepath\|DBT_RUNTIME_ENV\|max_active_tasks" \
  challenges/03-airflow-orchestration/stubs/dags/portfolio_analytics_daily.py
grep -c "# TODO: wire" challenges/03-airflow-orchestration/stubs/dags/portfolio_analytics_daily.py
```
Expected: `3` (fixes are in the stub) and `1` (stub stays unwired).

- [ ] **Step 8: Commit**

```bash
git add data_products/portfolio_analytics/dags/portfolio_analytics_daily.py \
        challenges/03-airflow-orchestration/stubs/dags/portfolio_analytics_daily.py
git commit -m "fix(challenge-03): keep DAG stability fixes in the stub and un-leak the section-6 wiring

The stability fixes previously lived only in the live copy, so challenge:reset
wiped them and the shipped starter also leaked the trainee's wiring deliverable.
Stub and live now carry the fixes and stay unwired; wiring moves to solution/ (Task 2).

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Bring the stability fixes into the `solution/` reference (keep wiring + docs)

**Files:**
- Overwrite then re-decorate: `challenges/03-airflow-orchestration/solution/dags/portfolio_analytics_daily.py`
- Test: `challenges/03-airflow-orchestration/solution/tests/test_dag_structure.py` (or the live copy)

**Interfaces:**
- Consumes: the fixed-but-unwired live DAG from Task 1.
- Produces: a solution DAG that carries every stability fix AND the finished wiring AND its reference documentation layer (full module docstring, rich `description`, `production` tag), so it is the correct answer key and differs from the stub only by those intentional items.

- [ ] **Step 1: Seed the solution from the fixed live DAG**

Run:
```bash
cp data_products/portfolio_analytics/dags/portfolio_analytics_daily.py \
   challenges/03-airflow-orchestration/solution/dags/portfolio_analytics_daily.py
```
The solution now has all fixes but is temporarily unwired and carries the stub's minimal docstring/`training` tag; the next steps restore its reference identity.

- [ ] **Step 2: Add the wiring line (this is the solution's answer)**

In `challenges/03-airflow-orchestration/solution/dags/portfolio_analytics_daily.py`, replace:

```python
    # TODO: wire start -> source_freshness_check -> dbt_pipeline -> publish_to_catalog -> end
```

with:

```python
    start >> source_freshness_check >> dbt_pipeline >> publish_to_catalog >> end
```

- [ ] **Step 3: Restore the reference `production` tag**

Replace the tag list value `"training"` with `"production"`:

```python
    tags=["dbt", "portfolio-analytics", "cosmos", "databricks", "production", "usage-id:AA00002933", "cost-center:52415"],
```

- [ ] **Step 4: Restore the reference docstring and description**

These three regions are unchanged from `main`, so recover their exact text from
`git show main:challenges/03-airflow-orchestration/solution/dags/portfolio_analytics_daily.py`
and paste them back:
1. the full module docstring (the "Topology / Databricks is the only platform / Alerting is tiered" block) in place of the minimal `"""portfolio_analytics_daily — challenge stub. ..."""`;
2. the `description=(...)` multi-line block in place of `description="Challenge stub for the portfolio analytics orchestration DAG.",`.

Run to view the exact source text:
```bash
git show main:challenges/03-airflow-orchestration/solution/dags/portfolio_analytics_daily.py | sed -n '1,33p;150,175p'
```

- [ ] **Step 5: Verify the solution has fixes + wiring and only the intended diffs vs the live copy**

Run:
```bash
grep -c "profiles_yml_filepath\|DBT_RUNTIME_ENV\|max_active_tasks" \
  challenges/03-airflow-orchestration/solution/dags/portfolio_analytics_daily.py
grep -c "start >> source_freshness_check" \
  challenges/03-airflow-orchestration/solution/dags/portfolio_analytics_daily.py
git --no-pager diff --no-index \
  data_products/portfolio_analytics/dags/portfolio_analytics_daily.py \
  challenges/03-airflow-orchestration/solution/dags/portfolio_analytics_daily.py
```
Expected: first grep `3`; second grep `1` (wired); the diff shows ONLY the docstring, `description`, `production` tag, and the wiring line — nothing else.

- [ ] **Step 6: Confirm the solution parses and passes the structural test**

Run: `pytest challenges/03-airflow-orchestration/solution/tests/test_dag_structure.py -q`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add challenges/03-airflow-orchestration/solution/dags/portfolio_analytics_daily.py
git commit -m "fix(challenge-03): sync stability fixes into the solution DAG and keep it as the wired reference

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 3: Make the profile fix reset-safe and correct its stale OAuth comments

**Files:**
- Modify: `data_products/portfolio_analytics/dbt/profiles.yml` (comments only — the token/threads/`_disable_pandas` code is already correct on the branch)
- Overwrite: `challenges/03-airflow-orchestration/stubs/dbt/profiles.yml`, `challenges/03-airflow-orchestration/solution/dbt/profiles.yml`

**Interfaces:**
- Consumes: the branch's already-fixed data-product profile (`threads: 1`, `connection_parameters._disable_pandas: true`, scheme-stripped host, `token:` auth on `local`/`dev`).
- Produces: all three profile copies identical and reset-safe, with comments that match the token-auth reality.

- [ ] **Step 1: Fix the file header comment (it still claims OAuth)**

In `data_products/portfolio_analytics/dbt/profiles.yml`, replace the header block:

```yaml
# Databricks-only profile. The connection is env-var driven so nothing secret
# lives in this file. Auth is OAuth: `auth_type: oauth` makes dbt-databricks
# delegate to the Databricks SDK, which reads the OAuth session that
# `databricks auth login` wrote to ~/.databrickscfg. There is no token here.
```

with:

```yaml
# Databricks-only profile. The connection is env-var driven so nothing secret
# lives in this file. Auth is token-based: every target reads DBT_ACCESS_TOKEN,
# which `.mise/env.sh` mints from the OAuth session on each mise run (falling
# back to ~/.databrickscfg). A static token target is required because the DAG
# runs dbt via profiles_yml_filepath (target=dev) inside the astro container,
# where auth_type: oauth would fall back to interactive browser OAuth and hang.
```

- [ ] **Step 2: Fix the `local`/`dev` inline comment (it still says "OAuth targets")**

Replace:

```yaml
    # `local` and `dev` are identical OAuth targets. The challenge:dbt / challenge:seed
    # mise tasks invoke dbt with `--target local` (the repo-wide convention every other
    # profile follows); the DAG's Cosmos ProfileConfig uses target_name="dev". Both
    # names must resolve, so both targets are defined.
```

with:

```yaml
    # `local` and `dev` are identical token targets (DBT_ACCESS_TOKEN). The
    # challenge:dbt / challenge:seed mise tasks invoke dbt with `--target local`
    # (the repo-wide convention every other profile follows); the DAG points
    # profiles_yml_filepath at target_name="dev". Both names must resolve, so
    # both targets are defined.
```

- [ ] **Step 3: Mirror the corrected profile into the stub and solution**

Run:
```bash
cp data_products/portfolio_analytics/dbt/profiles.yml \
   challenges/03-airflow-orchestration/stubs/dbt/profiles.yml
cp data_products/portfolio_analytics/dbt/profiles.yml \
   challenges/03-airflow-orchestration/solution/dbt/profiles.yml
```

- [ ] **Step 4: Verify all three profiles are identical and reset-safe**

Run:
```bash
git --no-pager diff --no-index \
  challenges/03-airflow-orchestration/stubs/dbt/profiles.yml \
  data_products/portfolio_analytics/dbt/profiles.yml
mise run challenge:reset 03
grep -c "_disable_pandas" data_products/portfolio_analytics/dbt/profiles.yml
```
Expected: the diff prints nothing; after reset the grep prints `3` (the profile fix survives reset).

- [ ] **Step 5: Commit**

```bash
git add data_products/portfolio_analytics/dbt/profiles.yml \
        challenges/03-airflow-orchestration/stubs/dbt/profiles.yml \
        challenges/03-airflow-orchestration/solution/dbt/profiles.yml
git commit -m "fix(challenge-03): make the dbt profile fix reset-safe and correct its stale OAuth comments

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 4: Version-guard and de-risk the `airflow_local_settings.py` supervisor patches

**Files:**
- Modify: `airflow_local_settings.py`
- Test: `tests/local_env/offline/airflow/test_airflow_local_settings_guard.py` (create)

**Interfaces:**
- Consumes: the branch's `_patch_airflow_task_heartbeat_conflict()` and `_patch_airflow_task_start_race()`.
- Produces: a pure helper `_airflow_supervisor_patches_enabled()` that both supervisor patches call before touching private Airflow internals, so the patches no-op on untested Airflow versions or when not explicitly enabled; and a narrowed duplicate-start branch that cannot silently mark an unrun task green.

- [ ] **Step 1: Write the failing unit test for the guard helper**

Create `tests/local_env/offline/airflow/test_airflow_local_settings_guard.py`:

```python
import importlib

import airflow_local_settings as als


def test_guard_disabled_for_untested_version(monkeypatch):
    monkeypatch.setenv("TRAINING_AIRFLOW3_SUPERVISOR_PATCHES", "1")
    assert als._airflow_supervisor_patches_enabled("2.10.5") is False
    assert als._airflow_supervisor_patches_enabled("3.2.0") is False


def test_guard_enabled_only_for_tested_version_and_optin(monkeypatch):
    monkeypatch.setenv("TRAINING_AIRFLOW3_SUPERVISOR_PATCHES", "1")
    assert als._airflow_supervisor_patches_enabled("3.1.0") is True
    monkeypatch.delenv("TRAINING_AIRFLOW3_SUPERVISOR_PATCHES", raising=False)
    assert als._airflow_supervisor_patches_enabled("3.1.0") is False
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/local_env/offline/airflow/test_airflow_local_settings_guard.py -q`
Expected: FAIL with `AttributeError: module 'airflow_local_settings' has no attribute '_airflow_supervisor_patches_enabled'`.

- [ ] **Step 3: Add the guard helper and gate both supervisor patches on it**

In `airflow_local_settings.py`, add near the top (after the imports):

```python
# The heartbeat/task-start patches below reach into private Airflow SDK
# internals (airflow.sdk.execution_time.supervisor) that were verified only
# against this pinned Airflow line. They are OFF unless explicitly opted in, so
# a stock or upgraded runtime keeps upstream behavior.
_TESTED_AIRFLOW_SUPERVISOR_VERSIONS = ("3.1.",)


def _airflow_supervisor_patches_enabled(version: str | None = None) -> bool:
    if os.environ.get("TRAINING_AIRFLOW3_SUPERVISOR_PATCHES") != "1":
        return False
    if version is None:
        try:
            from airflow import __version__ as version
        except Exception:
            return False
    return any(version.startswith(v) for v in _TESTED_AIRFLOW_SUPERVISOR_VERSIONS)
```

Then, as the first statement inside BOTH `_patch_airflow_task_heartbeat_conflict()` and `_patch_airflow_task_start_race()`, add:

```python
    if not _airflow_supervisor_patches_enabled():
        return
```

(The cimon listener compatibility patch stays unconditional — it fixes a hard `PluginValidationError`, not a race.)

- [ ] **Step 4: Narrow the duplicate-start branch so it cannot fake a green task**

In `_patched_on_child_started`, the `_is_already_running_start_conflict(err)` branch currently sets `self._terminal_state = _supervisor.TaskInstanceState.SUCCESS` and `self._exit_code = 0`. Replace that success-forcing with a non-success neutralization plus a loud log, so a real never-ran task is never reported green:

```python
                if _is_already_running_start_conflict(err):
                    _supervisor.log.warning(
                        "Duplicate task-start conflict; killing duplicate launcher "
                        "and leaving the authoritative TI state to the server",
                        status_code=getattr(getattr(err, "response", None), "status_code", None),
                        detail=getattr(err, "detail", None),
                        ti_id=self.id,
                    )
                    self.kill(_supervisor.signal.SIGKILL, force=True)
                    self._exit_code = 0
                    return
```

Why: the original task process is genuinely running elsewhere, so the server owns the real terminal state; forcing this launcher to `SUCCESS` risked reporting a task green that this subprocess never executed.

- [ ] **Step 5: Run the guard test to verify it passes**

Run: `pytest tests/local_env/offline/airflow/test_airflow_local_settings_guard.py -q`
Expected: PASS (both tests green).

- [ ] **Step 6: Re-confirm import-safety with no airflow installed**

Run:
```bash
AIRFLOW__CORE__DAGS_FOLDER=/tmp/fake_dags python3 -c "import runpy; runpy.run_path('airflow_local_settings.py'); print('IMPORT-SAFE')"
```
Expected: prints `IMPORT-SAFE` and exit 0.

- [ ] **Step 7: Enable the opt-in where the container needs it**

In `docker-compose.override.yml`, add `TRAINING_AIRFLOW3_SUPERVISOR_PATCHES: "1"` to the shared `x-airflow-common` `environment:` anchor (all Airflow services inherit it via `<<: *airflow-common`, the same anchor that mounts `airflow_local_settings.py`), so the patches remain active for the local devcontainer runtime they were written for.

- [ ] **Step 8: Commit**

```bash
git add airflow_local_settings.py tests/local_env/offline/airflow/test_airflow_local_settings_guard.py docker-compose.override.yml
git commit -m "fix(airflow): version-guard the supervisor patches and stop faking a green task on duplicate start

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 5: Document the change and prove Challenge-03 §8–9 end-to-end

**Files:**
- Modify: `challenges/CHANGES.md` (Challenge 03 table)
- Verify: real astro run of §8–9; `mise run challenge:verify 03`

**Interfaces:**
- Consumes: Tasks 1–4.
- Produces: an updated change-and-why log and recorded evidence that the Windows failure is resolved (the repo's static gate cannot prove this on its own).

- [ ] **Step 1: Add Challenge-03 rows to the change log**

Append these rows to the Challenge 03 table in `challenges/CHANGES.md`:

```markdown
| The Cosmos `DbtTaskGroup` now reads the dbt profile via **`profiles_yml_filepath`** (was `DatabricksTokenProfileMapping`), and the freshness gate picks its target at runtime. | Runtime `BaseHook.get_connection` lookups intermittently failed to resolve `databricks_default` during Airflow-3 local `dags test`, so parse/exec now reads the repo profile directly and injects host/token from the connection only when available. |
| The `local`/`dev` dbt targets use **token auth** (`DBT_ACCESS_TOKEN`) instead of `auth_type: oauth`; `threads: 1` and `connection_parameters._disable_pandas: true` were added. | `profiles_yml_filepath` runs `--target dev` inside the astro container, where `auth_type: oauth` falls back to interactive browser OAuth and hangs; `.mise/env.sh` already mints `DBT_ACCESS_TOKEN` from OAuth. `_disable_pandas` disables the pandas/pyarrow deserialization path that flaked on `dbt show`; `threads: 1` removes result-fetch concurrency races. |
| The DAG carries `max_active_tasks=1` and runs Cosmos tests **after all builds** (`TestBehavior.AFTER_ALL`). | Serialize local task execution to avoid Airflow-3 supervisor start/heartbeat races, and stop relationship tests from referencing marts before they are built. |
| A local-only `airflow_local_settings.py` adds **version-guarded, opt-in** compatibility shims for Airflow 3.1 (cimon listener hookspec; transient supervisor heartbeat/start-race handling). | Airflow 3.1's local `dags test` raised a `PluginValidationError` and killed tasks on transient queued→running conflicts, failing §8–9 nondeterministically. The shims are mounted only into the devcontainer and no-op on untested versions. |
```

- [ ] **Step 2: Assert the docs no longer contradict the code**

Run:
```bash
grep -n "identical OAuth target" challenges/CHANGES.md data_products/portfolio_analytics/dbt/profiles.yml || echo "no stale OAuth claim (good)"
grep -n "DatabricksTokenProfileMapping" data_products/portfolio_analytics/dags/portfolio_analytics_daily.py || echo "mapping removed from DAG (good)"
```
Expected: both print their "good" fallbacks (no stale claims remain).

- [ ] **Step 3: Static gates green across the touched challenges**

Run:
```bash
mise run challenge:verify 03
pytest data_products/portfolio_analytics/tests/test_dag_structure.py challenges/03-airflow-orchestration/solution/tests/test_dag_structure.py -q
```
Expected: verify FAILS on the shipped stub (unwired) — wire it locally to confirm it then PASSES — and both structural tests pass.

- [ ] **Step 4: Prove §8–9 for real in the devcontainer (the actual acceptance gate)**

Run, and capture the output for the PR:
```bash
databricks auth describe --profile DEFAULT
mise run challenge:seed 02
astro dev restart --wait 5m
astro dev run dags test portfolio_analytics_daily 2026-05-04 2>&1 | grep -iE "retry|attempt"   # step 8
astro dev run dags unpause portfolio_analytics_daily
astro dev run dags trigger portfolio_analytics_daily                                            # step 9
mise run challenge:dbt 03 -- show --select fct_portfolio_returns --limit 5                      # parity check
```
Expected: §8 shows two retry attempts; §9 reaches `success` with the mart rows previewed (parity with a plain `dbt build`). Attach this log to the PR — a static verify pass is not sufficient evidence for C3.

- [ ] **Step 5: Commit**

```bash
git add challenges/CHANGES.md
git commit -m "docs(challenge-03): record the Airflow-3 DAG stability fixes and their rationale

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Self-Review

**1. Spec coverage** (against `docs/superpowers/specs/2026-07-31-portfolio-airflow3-dag-stability-review-design.md`):
- B1 (leaked wiring) → Task 1 Steps 2–3 + Task 2 (wiring only in solution).
- B2 (reset wipes the fix) → Task 1 (DAG stub sync) + Task 3 (profile stub/solution sync), both proven by a `reset`-then-grep step.
- C1 (stale/contradictory docs) → Task 3 comment fixes + Task 5 CHANGES rows + Step 2 assertion.
- C2 (fragile patches / false green) → Task 4 version guard + narrowed duplicate-start branch + guard unit test.
- C3 (not verified end-to-end) → Task 5 Step 4 real §8–9 run.
- R1 (token switch) → kept intentionally; documented in Task 3 comments and Task 5 CHANGES; rationale in Global Constraints.

**2. Placeholder scan:** every code/edit step contains real content or an exact `git show`/`grep` command; no "TBD"/"handle errors"/"similar to above".

**3. Type/name consistency:** the helper is named `_airflow_supervisor_patches_enabled` in the test (Task 4 Step 1), the implementation (Step 3), and both patch call-sites (Step 3). The env flag `TRAINING_AIRFLOW3_SUPERVISOR_PATCHES` is identical across the test, the helper, and `docker-compose.override.yml` (Step 7). The wiring string is identical in Task 1 (removed), Task 2 (added), and the verify gate.

**Note on ordering:** Task 1 must precede Task 2 (Task 2 seeds the solution from the fixed live file). Tasks 3 and 4 are independent of 1–2 and of each other. Task 5 runs last.
