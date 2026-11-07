# RCA — Challenge 04 was entirely unrunnable: dbt segfaulted on every query

| Field | Value |
|---|---|
| **Date** | 2026-08-03 |
| **Status** | Resolved on `feature/improvements` |
| **Severity** | Critical — 100% of Challenge 04 was impossible to complete; every command that touched data crashed the interpreter with no error message |
| **Components** | `data_products/atlas_elt/dbt_profiles/profiles.yml` · `dbt-databricks` 1.11.7 / `databricks-sql-connector` · Python 3.13 + pandas/pyarrow |
| **Discovered while** | Running a beginner trainee agent end-to-end through Challenge 04 after the raw-dbt conversion |
| **Related** | `docs/rca/2026-08-03-profiles-symlink-windows.md` · `docs/rca/2026-08-03-challenge-02-raw-dbt-walkthrough.md` |

---

## 1. Summary

Every dbt command in Challenge 04 that returned rows from Databricks — `seed`, `run`, `build`,
`test`, `compile`, `show` — **segmentation-faulted the Python interpreter**. The process died with
exit code 139 and, depending on the parse cache, either a raw C-level stack dump or *no output at
all*.

The cause was a single missing two-line setting. dbt-databricks converts result sets through pandas
by default; on this image (Python 3.13 + `databricks-sql-connector` + pyarrow) that conversion
segfaults. Every dbt profile in this repo already disables it with
`connection_parameters: {_disable_pandas: true}` — **except `atlas_elt`**, the one profile Challenge
04 uses.

Adding those two lines to the three `atlas_elt` targets fixed it completely. The capstone now builds
green end to end: `dbt build` → `PASS=40 WARN=0 ERROR=0`.

---

## 2. Impact / who was affected

- **Every trainee attempting Challenge 04.** Not "degraded" — impossible. There is no way to complete
  a dbt challenge when no dbt command can read a row.
- **The failure was maximally deceptive**, for three compounding reasons:
  1. **`dbt debug` passed.** The connection test only performs a handshake and returns no rows, so it
     never hits the pandas path. The guide presents a green `dbt debug` as the "you are configured,
     proceed" signal. It is not.
  2. **A segfault is not a dbt error.** There is no dbt error message, no stack trace from dbt, no
     log line, no exit summary — the interpreter is killed by the OS mid-call.
  3. **With a warm parse cache, `dbt seed` exited 0 and printed nothing.** The trainee reasonably
     concluded it had worked, moved on, and then could not understand why no tables existed.
- The trainee correctly diagnosed the mechanism but had no way to know a working reference profile
  existed two directories away, so they logged it as an unrecoverable environment defect.

---

## 3. Symptoms

```console
$ cd data_products/atlas_elt && dbt seed
Found 28 models, 1 snapshot, 4 data tests, 7 seeds, 7 sources, 833 macros
Concurrency: 1 threads (target='local')

Fatal Python error: Segmentation fault

Current thread (most recent call first):
  File ".../pandas/core/arrays/numpy_.py", line 501 in to_numpy
  File ".../pandas/core/internals/managers.py" ...
  File ".../databricks/sql/result_set.py", line 129 in _convert_arrow_table
  File ".../databricks/sql/result_set.py", line 411 in fetchall
  File ".../dbt/adapters/databricks/handle.py", line 73 in fetchall
  File ".../dbt/adapters/sql/connections.py", line 204 in get_result_from_cursor
Segmentation fault
EXIT: 139
```

Minimal reproduction — a query with no tables, no models, no seeds involved:

```console
$ cd data_products/atlas_elt && dbt show --inline "select 1 as a" --limit 1
Concurrency: 1 threads (target='local')
EXIT=139
```

That reduction is what localised the fault to the connection layer rather than to any model SQL.

---

## 4. Root cause

`dbt-databricks` materialises query results into a pandas DataFrame
(`result_set.py::_convert_arrow_table` → `pandas ... to_numpy`). On this image that path segfaults in
the native pandas/pyarrow layer.

The connector supports opting out via `_disable_pandas`, and this repo already relies on that
everywhere. A survey of all tracked profiles at the time of the fault:

| Profile | `_disable_pandas` | Used by |
|---|---|---|
| `challenges/02-dbt-pipeline/dbt_profiles/profiles.yml` | ✅ all 3 targets | Challenge 02 |
| `data_products/portfolio_analytics/dbt/profiles.yml` | ✅ all 3 targets | Challenge 03 |
| `challenges/03-airflow-orchestration/{stubs,solution}/dbt/profiles.yml` | ✅ | Challenge 03 |
| **`data_products/atlas_elt/dbt_profiles/profiles.yml`** | ❌ **absent** | **Challenge 04** |

So the defect is an **inconsistency, not a discovery**. The workaround was already known and applied
repo-wide; `atlas_elt` was simply never updated. That also explains why Challenges 02 and 03 worked
fine in the same container, same interpreter, same session — they were protected and 04 was not.

### Why nothing caught it

- **`dbt debug` and `dbt parse` both pass**, because neither returns result rows. The natural smoke
  tests are exactly the two commands that cannot see this bug.
- **The verify gate is static.** `challenges/04-atlas-capstone/verify.sh` runs `deps`, `parse`,
  `compile` and a bundle validate; live `run`/`test` are gated behind `CERT_INTEGRATION_TESTS=1`.
  `compile` does issue a query and did segfault — but the gate had presumably not been run live on
  this image since the profile diverged.
- **No test asserted the invariant.** The `_disable_pandas` setting was a convention propagated by
  copy-paste, with nothing enforcing it.

---

## 5. Fix

Added to all three `atlas_elt` targets (`local`, `dev`, `dev7`), in both
`dbt_profiles/profiles.yml` and the project-dir copy:

```yaml
      connection_parameters:
        _disable_pandas: true
```

### Guardrail added

`tests/local_env/offline/tooling/test_dbt_profiles_disable_pandas.py` walks every tracked
`profiles.yml`, parses it, and asserts that **every** target with `type: databricks` sets
`_disable_pandas: true`. A new profile — or a new target on an existing profile — now fails the test
instead of silently segfaulting at runtime. Negative-tested: flipping the value to `false` fails with
all three offending targets named.

---

## 6. Verification

All run inside the devcontainer from `data_products/atlas_elt`, after the fix:

```console
$ dbt show --inline "select 1 as a" --limit 1
Previewing inline node:
| a |
| 1 |
EXIT=0                                    # was 139

$ dbt seed
Done. PASS=7 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=7      # 10,000 trades loaded

$ dbt build
Finished running 1 incremental model, 7 seeds, 1 snapshot, 3 table models,
4 data tests, 24 view models in 114.01s
Done. PASS=40 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=40

$ mise run challenge:verify 04
[pass] offline checks complete
VERIFY_EXIT=0
```

(`databricks bundle validate` reports a Terraform OpenPGP "key expired" warning from the future-dated
sandbox clock; `verify.sh` already treats that as non-fatal by design.)

---

## 7. Secondary findings from the same walkthrough

Two smaller issues, both fixed in the guide:

**`dbt deps` dirties a tracked file.** The Quick Start's second command rewrites
`data_products/atlas_elt/package-lock.yml`, expanding the `shared` package path from `../../shared`
to an absolute machine-specific path. Every trainee therefore has a dirty `git status` after step 2,
with no idea whether they broke something — and could commit a path that is wrong for everyone else.
The guide now calls this out as expected build-artifact churn and says how to reset it.

**The verify gate does not run the pipeline.** The guide said "a clean run means … all tests pass",
but the gate is static (`deps`/`parse`/`compile` + bundle validate) and never executes a model. The
guide now states this plainly and points back to `dbt build` / `dbt test` as the commands that
actually run the pipeline.

---

## 8. Lessons

1. **When a workaround is a convention, make it a test.** `_disable_pandas` was correctly applied in
   four places and missed in one. Copy-paste conventions decay silently; the guard test is three
   dozen lines and would have caught this the day the profile was added.
2. **`dbt debug` is a connectivity check, not a readiness check.** It returns no rows, so it cannot
   detect faults in result handling. Any "are you set up?" step should run something that actually
   returns data — `dbt show --inline "select 1 as a"` is a two-second, side-effect-free smoke test
   that would have caught this immediately.
3. **A static verify gate cannot certify a data pipeline.** Compiling SQL proves the graph is
   coherent; it says nothing about whether a single row can be read or written. Gates that never
   execute give false confidence precisely where confidence matters most.
4. **Segfaults break every assumption about error reporting.** No exception, no log, sometimes exit 0
   with empty output. When a tool "does nothing", check the exit code for 139 before believing it
   succeeded.
5. **Compare against the working sibling first.** Challenges 02 and 03 worked in the same container
   and interpreter. Diffing the passing profile against the failing one located the root cause faster
   than reading the pandas traceback.
