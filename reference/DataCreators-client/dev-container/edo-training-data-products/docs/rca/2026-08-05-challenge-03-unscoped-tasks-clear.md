# RCA — Challenge 03 Section 10 tells the trainee to clear *every* historical DAG run, and `--yes` hides it

| Field | Value |
|---|---|
| **Date** | 2026-08-05 |
| **Status** | Root cause proven; fix implemented and verified |
| **Severity** | Medium-high — no data loss, but ~20 minutes of unrequested warehouse compute per trainee, and it teaches a genuinely dangerous habit |
| **Components** | `challenges/03-airflow-orchestration/README.md` (Phase 1, Section 10) · Airflow 3.1 `tasks clear` CLI |
| **Discovered while** | A trainee-simulation run of challenge 03 on Windows 11 (WSL2), 2026-08-05 |
| **Related** | `docs/challenge-runs.md` row for 2026-08-05 / 03 |

---

## 1. Summary

Section 10 ("break it, fix it, clear it") ended with this in its Solution block:

```bash
astro dev run tasks clear portfolio_analytics_daily -t source_freshness_check --downstream --yes
```

The surrounding prose says clearing "re-queues the task and its descendants **without a new DAG
run**", which reads as *this* run. It is not.

> **Root cause: `airflow tasks clear` takes no run id. Its `-s` / `-e` window defaults to the
> DAG's entire history, so the command matches the named task in *every* DAG run that has ever
> executed. `--yes` then suppresses the confirmation prompt that would have listed them.**

With `--downstream`, each matched task drags its whole descendant subtree with it. On a DAG with
nine runs that is nine full re-executions, serialized by `max_active_runs=1`.

---

## 2. Impact

- Every trainee who follows the Solution block literally re-runs the entire DAG history.
- Measured on the 2026-08-05 run: **8 unrelated runs re-executed** back-to-back from 06:31 to
  06:45 before the run the trainee actually wanted even started. Roughly 20 minutes of
  Databricks compute nobody asked for.
- It is silent. `--yes` removes the one signal that would have revealed the blast radius, so the
  trainee sees a slow DAG rather than a mistake.
- Worst of all it is taught as a runbook action — the guide explicitly frames it as "the same
  recovery the runbook prescribes for an on-call engineer". Learning this unscoped form and
  carrying it to production is the real cost.

---

## 3. Root cause

`tasks clear` has no run-id argument at all. Airflow 3.1:

```
Usage: airflow tasks clear [-h] [-B BUNDLE_NAME] [-R] [-d] [-e END_DATE] [-f]
                           [-r] [-s START_DATE] [-t TASK_REGEX] [-u] [-v] [-y]
                           dag_id
```

Scope comes only from `-s` / `-e`, described as "Override start_date / end_date" — i.e. absent
them, the range is unbounded. Dropping `--yes` makes the CLI print exactly what it is about to do:

```
You are about to delete these 9 tasks:
[<TaskInstance: portfolio_analytics_daily.source_freshness_check manual__2026-07-31T17:29:49 [success]>,
 <TaskInstance: portfolio_analytics_daily.source_freshness_check manual__2026-08-05T06:09:44 [success]>,
 ... 7 more across every historical run ...]
```

Nine task instances from one "clear this task" command.

### 3.1 Two traps in the obvious fix

Adding `-s` / `-e` is right, but neither behaves the way a beginner would assume, and both were
found by testing rather than reasoning:

| Attempt | Matched | Why |
|---|---|---|
| `-s 2026-08-05 -e 2026-08-05` | **0 tasks** | `-e` is a *timestamp*: it parses to `00:00`, which is before the run's `05:00` logical date. Silent no-op. |
| `-s 2026-08-05 -e 2026-08-06` | **1 task** — correct | Window covers the logical date |
| any `-s`/`-e` against a `dags trigger` run | **0 tasks** | `-s`/`-e` filter on `logical_date`; a plain manual trigger has none |

That last row matters most: Section 10's own flow tells the trainee to **trigger the DAG
manually**, so date scoping cannot select their run at all. A fix that only added `-s`/`-e`
would have been wrong for the exact case the section creates.

---

## 4. How to reproduce

```bash
astro dev start
# trigger the DAG a few times so history exists, then:
echo n | astro dev run tasks clear portfolio_analytics_daily -t source_freshness_check --downstream
```

Read the `You are about to delete these N tasks` line. `N` is the number of DAG runs in history,
not 1.

---

## 5. The fix

Section 10 now makes the **UI Clear** the primary path — it is scoped to the run you clicked by
construction, and it is the lower-friction path for this audience anyway. The CLI form is kept,
because on-call engineers do use it, but it now carries:

- an explicit warning that `tasks clear` takes no run id, that unscoped means *every* run, and
  that `--yes` hides the evidence;
- the instruction to run it **without** `--yes` first and read the `N tasks` line;
- a correctly scoped example using `-s 2026-08-05 -e 2026-08-06`, with the midnight-parsing trap
  called out;
- the fact that `-s`/`-e` cannot select `dags trigger` runs, so those must be cleared from the UI.

`--yes` no longer appears anywhere in the guide.

### 5.1 Alternatives considered and rejected

| Option | Why not |
|---|---|
| Just add `-s`/`-e` to the existing command | Wrong for this section: the trainee's run is a manual trigger with no logical date, so date scoping matches nothing. Would have replaced a loud bug with a silent one. |
| Delete the CLI example, UI only | Clearing from the CLI is a real on-call skill, and the trap is worth teaching once, in a training repo, rather than discovered in production. |
| Keep `--yes` but add a warning | The prompt *is* the safety mechanism; documenting a warning while suppressing the tool's own is backwards. |

---

## 6. Verification (evidence)

| Check | Result |
|---|---|
| `tasks clear --help` (Airflow 3.1) | No run-id option; scope only via `-s`/`-e` |
| Unscoped command, `--yes` removed | `You are about to delete these 9 tasks` — 9 distinct DAG runs |
| `dags list-runs` after the original run | 8 unrelated runs re-executed 06:31→06:45, ~2 min apart, serialized |
| `-s 2026-08-05 -e 2026-08-05` | 0 tasks — silent no-op, trap confirmed |
| `-s 2026-08-05 -e 2026-08-06` | 1 task, the intended run only — fix confirmed |
| `pytest data_products/portfolio_analytics/tests/ -q` after guide edit | 3 passed |

---

## 7. Lessons

1. **`--yes` on a destructive command in a guide is a defect in itself.** The prompt was the only
   thing standing between the trainee and nine re-runs, and the guide removed it.
2. **"Without a new DAG run" is not the same as "only this DAG run".** The prose was true and
   still left the reader with the wrong model of the blast radius.
3. **Test the fix, do not reason it out.** The first scoped command tried here matched zero tasks
   because `-e` parses to midnight. Shipping the "obvious" fix unverified would have replaced a
   loud bug with a silent one.
4. **Check what the scoping flags actually filter on.** `-s`/`-e` filter `logical_date`, which
   manual triggers do not have — invisible unless you test the case the guide actually creates.
