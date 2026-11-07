# Course and environment handoff

Work advanced on 7 October 2026 without the approved dev-container boundary. The actual course root and runnable reference project were located. Existing course edits were preserved; only bounded generated Appendix H text and the two delivery verifier/support-script copies were updated for tested repairs. Current source, not an old release, governs the next run.

## Start in the actual environment

1. Locate the mounted runnable project using `.mise.toml`, `.devcontainer/`, `scripts/challenge-v2.py` and `challenges/v2/manifest.json`. Read applicable repository instructions and inspect Git status.
2. Re-run documented dev-container readiness and sanitized identity/resource probes. Record a new UTC run ID, source hashes, Docker context/server/Compose, Mise, dbt adapters, Databricks CLI, Astro worker/API/UI, browser and broker prerequisites separately.
3. Inspect `bash scripts/setup-v2-tools.sh` before preparing isolated teaching runtimes. Do not upgrade the managed client Python. Run `bash scripts/setup-instructor-demos.sh` for the separate pinned capture tools; select the actual dbt executable/interpreter explicitly using the documented `DEMO_DBT_BIN` and `DEMO_DBT_PYTHON` exports.
4. Run `python3 scripts/challenge-v2.py list`, the supporting local checks and the doctor/smoke commands from `instructor-demos/README.md`. A supporting pass is not task/route acceptance.
5. Complete the Docker and Airflow UI pilots first. Their eight definitions are **draft** and cannot be captured by changing tool availability alone. Docker needs live interaction/lifecycle/mount/image identity and cleanup rehearsal. Airflow needs fresh trigger/API/state/output assertions, authenticated state outside recording, actual graph/log locators, worker-visible paths and executables, receipt identity, quality failure and recovery actions. The current UI definitions only describe navigation contracts and are intentionally blocked.
6. Implement and execute the still-incomplete connected dbt/capstone/Astro/Kafka verifier routes. Complete every offered phase's untouched starter, learner reconstruction and instructor solution on each offered route, plus each optional/reference exercise. Preserve prior-solution-exposure limitations and genuine human review/timing gates.
7. Repeat package-only classroom entry, browser/reconnect/restart, two-workspace Docker/dbt/Airflow isolation, normal waits/resources and main-PDF command copy/paste in disposable assigned scope. Never use broad prune/reset or touch another learner's resources.

## Reusable code and publishing

The runnable project now has `scripts/instructor-demos.py`, its registered PTY/browser/assertion/export modules, a strict schema, twelve source-bound definitions, pinned capture dependencies, independent dbt output checks, a byte-range-capable static media server, source drift and interrupted-cleanup tests, and separate learner/instructor packaging. See `instructor-demos/README.md` for exercised interfaces.

The course adds `scripts/prepare-instructor-demo-course.py`, `scripts/instructor-demo-filter.lua`, `pdf/headers/instructor-demos.tex`, an isolated review tool lock and `scripts/verify-instructor-demo-bundle.py`. They consume static reviewed bundles; they never launch capture workloads. Prepare a **fresh** overlay from a final reviewed bundle:

```bash
python3 scripts/prepare-instructor-demo-course.py --bundle <reviewed-bundle> --output candidates/instructor-demos/<new-overlay>
python3 scripts/prepare-instructor-demo-course.py --bundle <reviewed-bundle> --check
```

The overlay resolves current semantic teaching anchors and records exact original chapter hashes. It contains complete selected story blocks and adapters, leaving the live authoring chapters intact. Its `integration.json` gives the exact builder filter/header/package additions and `INSTRUCTOR_DEMO_BUNDLE` environment requirement. Apply it to an isolated snapshot of the **current** course and run existing gates with new review destinations; do not regenerate an old v4 release over current prose.

After source repairs, use the current root `scripts/sync-course-v2.py` and `scripts/integrate-review-v2.py`, then both `--check` modes. The runnable client's separate `scripts/sync-v2-course.py` also regenerates all 39 READMEs/concepts/summaries into its historical review candidate location; it does not replace the current root course. Both generators were checked. All 33 v2 legacy answer bodies were preserved in instructor files; root conceptual END answer keys and owner editorial conventions remain intact.

Build a full course candidate with `./build-pdf`, its HTML with the documented candidate `V4_RELEASE_DIR`, and `verify-release.py` using a **new** review location. Keep the 100,000-word/237-readable-page floors, all current substantive teaching and figure gates. Full main-course acceptance and the initial three/twelve-story selection remain pending: only dbt is captured here. Owner decisions in devc.md section 7 remain open. No promotion, commit, authoring push or external video publication was performed.

## Evidence scope

The final audit is `../20261007T215100Z-final-source/verification-results.json` and its task matrix. It runs 24 supporting phase journeys across twelve phases; the local/reference result is distinct from task-level explanation, learner independence, actual connected execution or human review. The reconstruction/two-workspace report is `../20261007T215100Z-final-reconstruction/local-classroom-rehearsal.json`; prior solution exposure is disclosed.

Four real DuckDB stories form the partial demo PDF/HTML/media candidate. Eight Docker/Airflow drafts remain blocked; no fabricated frames fill the book. Native PDF integration is proven in an isolated insertion/restoration pilot, while the complete main book and full twelve-story library remain pending. Candidate paths, hashes, playback/bounds review, selection/page cost and package evidence are linked from the root dated review README and devc.md.
