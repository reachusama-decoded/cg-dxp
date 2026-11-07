# Classroom troubleshooting — observed and pending boundaries

Start in the runnable project root (the directory with `.mise.toml` and `scripts/challenge-v2.py`). Authentication and preparation happen outside recordings.

| Symptom | Discriminating check | Diagnosis and smallest recovery | Evidence status |
|---|---|---|---|
| Python cannot open `scripts/challenge-v2.py` | `pwd`; `test -f scripts/challenge-v2.py` | Enter the extracted/mounted runnable project root before invoking the interface. | Exact workspace assumptions exercised in package extraction. |
| dbt launcher says old `Capital/…/python` not found | Inspect the launcher path; run the selected Python module/version. | Relocated environment launcher. Prepare a fresh isolated teaching environment and select its absolute executable; do not edit managed Python. | Observed here and repaired through overrides/module invocation. |
| Unknown executable or capture returns 77 | Run `scripts/instructor-demos.py doctor --story <id>` with the capture interpreter. | Missing prerequisite or draft story, distinct from wrong learner work. Prepare that capability; finish draft assertions before marking ready. | Blocked captures and missing-prerequisite tests. |
| Relationship test fails and mart is skipped | Read `target/run_results.json` and the named relationship failure; independently inspect the input key. | Unmatched fund ID. Restore the copied fixture, run `dbt seed --profiles-dir .`, then rebuild and inspect per-fund outputs. | Fresh observed failure/repair/replay capture. |
| A repair still uses wrong input | Compare source CSV and seeded table, then staged rows. | Changing CSV alone does not change a dbt source table. Reseed explicitly before rebuilding staging. | Observed during repair development; fixed and repeated. |
| Grand total is right but funds are wrong | Query per-fund rows against CSV/Decimal calculation. | Grain/join/value error or hard-coded output. Repair the transformation and repeat a total-preserving input variation. | Alternative and hard-coded-mart verifier tests. |
| Docker client cannot reach daemon | `docker version`; `docker context show`; `docker info` | Distinguish absent client from unavailable/wrong daemon/context. Restore the assigned runtime/context; do not prune shared Docker state. | Actual Docker boundary unavailable; live rehearsal pending. |
| Connected profile fails identity/access | Instructor-assigned `databricks current-user me --profile <profile>`; bounded object discovery | Restore the prepared profile and assigned access. Record denied/empty/not-found separately; do not change grants or dump credentials. | Live rehearsal pending. |
| Astro worker cannot find project/dbt | Inspect the assigned worker's mounted path/executable and task log | The developer's path may not be mounted in the worker. Correct only the owned mount/config and retrigger a fresh run. | Live rehearsal pending. |
| An assigned port is occupied | Inspect listeners and the owning resource ledger | Use an assigned free port or stop only your own known service. Never kill another learner's process. | Live collision rehearsal pending. |
| Quality fails and no receipt appears | Inspect actual task states and receipt run identity | Repair the upstream input/quality condition before bounded retry; independently recheck output and new receipt. | Local Dag.test observed; Astro/API/UI recovery pending. |

Instructor smoke, after preparation (from the runnable root):

```bash
.local/demo-capture/bin/python scripts/devc-smoke.py --route duckdb
.local/demo-capture/bin/python scripts/devc-smoke.py --route docker
.local/demo-capture/bin/python scripts/devc-smoke.py --route astro-ui
```

Smoke establishes measured process/tool readiness only. Missing prerequisites return 77. It does not authenticate, start services, infer assigned schemas, fix configuration or certify route completion.
