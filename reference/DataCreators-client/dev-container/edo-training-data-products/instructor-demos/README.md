# Observed instructor demonstrations

The reusable capture/publishing system is implemented. Four local dbt stories
are executable; eight Docker/Airflow teaching contracts stay **draft** pending
live rehearsal. A draft or missing prerequisite returns exit **77** and creates
no frames. The initial selection remains three of twelve stories (25%): Docker
image-to-shell, dbt build-and-inspect and Airflow trigger/graph/log. Publication
includes only captured, reviewed stories; it does not fill missing catalogue slots.

## Prepare a separate capture environment

From this runnable project's root:

```bash
bash scripts/setup-instructor-demos.sh
# Select the prepared dbt teaching environment, without upgrading managed Python:
export DEMO_DBT_BIN="$PWD/.local/v2-tools/bin/dbt"
export DEMO_DBT_PYTHON="$PWD/.local/v2-tools/bin/python"
.local/demo-capture/bin/python scripts/instructor-demos.py validate
.local/demo-capture/bin/python scripts/instructor-demos.py doctor --story dbt-build-and-inspect
.local/demo-capture/bin/python scripts/devc-smoke.py --route duckdb
```

A moved venv may retain launcher paths to the old checkout. Recreate an isolated
teaching environment using the established `scripts/setup-v2-tools.sh` in the
actual container, or select a fresh environment explicitly. Do not edit the
managed interpreter or pretend a broken launcher is a modeling failure. In the
7 October authoring-host run, `.local/demo-dbt/` is a separate measured environment;
replace `v2-tools` with `demo-dbt` in the two exports to repeat that local route.
Capture dependencies are fully pinned in `requirements.lock`; Chromium is the
revision supplied by the pinned Playwright release.

## Inspect and execute a story

```bash
.local/demo-capture/bin/python scripts/instructor-demos.py list
.local/demo-capture/bin/python scripts/instructor-demos.py capture --story dbt-build-and-inspect --run-id my-fresh-run --dry-run
.local/demo-capture/bin/python scripts/instructor-demos.py capture --story dbt-build-and-inspect --run-id my-fresh-run
.local/demo-capture/bin/python scripts/instructor-demos.py check --story dbt-build-and-inspect --run-id my-fresh-run
```

Run IDs are safe identifiers and may never reuse an existing capture directory.
Fresh workspaces copy explicitly labelled instructor-completed assets; they never
replace a learner attempt. Real PTYs retain shell state. pyte decodes actual ANSI
output into a Chromium terminal surface; native browser recording preserves the
observed transition. Input events and raw output remain distinct and private.
Application actions use Playwright navigation, clicks, fills and visible locators.
No application success labels or responses are simulated.

Each story binds task IDs, current source/config/schema/theme hashes, observed
exits, registered assertions, times, frame/video hashes and owned cleanup. Changes
invalidate reuse. Failed/interrupted runs remain visible and cannot be exported.
Ctrl-C closes owned PTYs/browser processes and executes only declared cleanup.
Private raw output/databases/browser videos remain under ignored `.local/`.
Sanitized evidence lives under `designer/reviews/instructor-demos/<run-id>/`.

## Review and export

Inspect **all** selected frames, the video at normal speed, failure reason,
readability and absence of sensitive data before approving a candidate:

```bash
.local/demo-capture/bin/python scripts/instructor-demos.py review --story dbt-build-and-inspect --run-id my-fresh-run --reviewer instructor --notes 'Record the actual frame/video review and its limitations here.'
.local/demo-capture/bin/python scripts/instructor-demos.py export --run-id my-fresh-run --story dbt-build-and-inspect --output .local/demo-candidate/my-fresh-run --pdf
cd .local/demo-candidate/my-fresh-run
python3 serve.py --port 8000
```

Open `http://localhost:8000/` for HTML playback. WebM, WebVTT captions, transcripts,
copyable commands, checksums, native story fragments and the demo PDF travel
with the bundle. PDF watch links open its relative HTML companion; no hosted URL
or QR code is invented. Dense command frames receive their own printed page.
Publishing is offline and never runs workloads or consumes unreviewed evidence.
A capture CLI result is a status report, not reviewer approval.

For multiple stories, capture each under the same fresh run ID and repeat
`--story` on `export`. Three additional ready definitions are
`dbt-sources-refs-and-sql`, `dbt-test-failure-and-repair` and
`dbt-fanout-and-replay`. The last two observe real negative tests, repair and
replay against independent CSV/Decimal calculations.

## Tests and supporting checks

```bash
.local/demo-capture/bin/python -m pytest tests/instructor_demos -q
# To include consequential real-dbt verifier tests:
V2_DBT_BIN="$DEMO_DBT_BIN" V2_PYTHON_BIN="$DEMO_DBT_PYTHON" .local/demo-capture/bin/python -m pytest tests/instructor_demos -q
python3 -m pytest tests/challenges/offline tests/local_env/offline -q
V2_DBT_BIN="$DEMO_DBT_BIN" V2_PYTHON_BIN="$DEMO_DBT_PYTHON" python3 scripts/run-devc-audit.py --run-id another-fresh-run
```

The audit runs supporting starter/reference journeys. It does not promote
phase-level assertions to every task/route or substitute for learner/human review.
`instructor-demos/rehearse-local.py` reconstructs dbt Phase 1 from its starter and
exercises two concurrent local workspaces. It discloses prior solution exposure;
agent elapsed time is not measured junior learner completion time.

## Remaining live work

Docker definitions and Airflow UI definitions are explicit draft contracts, not
completed routes. The Airflow definitions still need fresh trigger/API/run-bound
output assertions, actual UI locators, worker mount/executable discovery and
failure/recovery actions before changing `readiness` to `ready`. Docker needs
image digests, real interactive/lifecycle/mount assertions and interrupted-run
cleanup rehearsed in the dev container. Do not change status merely to bypass the
gate. Advanced dbt is observed on DuckDB only; Databricks remains separate.

Root `devc.md` and its dated evidence/handoff identify exactly what remains. Full
course acceptance waits for the selected Docker and Airflow pilots, all offered
live routes, task-level three journeys, packaged course commands and human/display
reviews. Candidate generation never authorizes release promotion or external video
publication.


## 8 October 2026 assigned-route supersession

Current dbt and Airflow stories now bind the supplied Portfolio Analytics inputs and the Databricks/Astro runtime contract. They are draft until connected rehearsal and fresh capture. Their earlier local story source is retained unchanged under `historical-local/stories`; old recordings/manifests remain historical and cannot enter the current assigned book. The root generator `scripts/generate-portfolio-demos.py` checks adapter freshness and records bindings in the new structure review. No fake UI/terminal observations are supplied.
