# Challenge pack v2 — design and implementation plan

**Date:** 5 October 2026. **Status:** local implementation and course candidate built; connected runtime acceptance and junior timing pilots pending. See [implementation review](reviews/IMPLEMENTATION.md).

This plan turns the owner's challenge review into a versioned development-container curriculum. The intended implementation preserves the current pack under `challenges/v1/`, creates a substantially improved pack under `challenges/v2/`, and provides complete instructor solutions under `challenges/v2-solutions/`. The initial delivery was planning only. The subsequent authorized implementation migrated v1, authored v2, installed isolated local verification environments and built a separate course candidate. Existing canonical data products and the promoted v4 release remain preserved.

This `designer/` belongs to `reference/DataCreators-client/dev-container/edo-training-data-products/` in ts-cg-datacreators (formerly under `Capital/`). Challenge version **v2** is independent of the course's **DataCreators-v4** version. The completed v4 release and its implementation record remain historical evidence, not a target to overwrite.

Read this plan with [challenge structure and authoring contract](CHALLENGE-SPEC.md), [migration map](MIGRATION-MAP.md), [proposed curriculum](CURRICULUM.md), [courseware synchronization design](COURSEWARE-SYNC.md), [baseline review](reviews/2026-10-05-baseline-review.md), [capstone data review](reviews/2026-10-05-capstone-data-review.md), and [timing audit](reviews/TIMING-AUDIT.md).

## Decisions derived from the request

| Requirement | Decision |
|---|---|
| Versioned challenge directories | Use the explicitly requested `challenges/v1` and `challenges/v2`, rather than the tentative `challenges-v1` naming. |
| Tool directories | `git`, `docker`, `dbt`, `databricks-cli`, `airflow`, `kafka`, `capstone`, in that curriculum order. |
| Phase directories | `phase-one-certified` and `phase-two-proficient`. Phase-one certification means evidence against a classroom minimum standard; it does not automatically issue a credential. |
| Phase exceptions | Databricks CLI offers Phase 1 only. Kafka offers optional Phase 1 only. Both retain a Phase 2 directory with a short “not offered” README and empty starter for structural consistency. These placeholders are neither assignments nor assessment gates. |
| Learner navigation | One root README per tool, with phase/task tables, concepts, prerequisites and suggested timing; no separately maintained duplicate `tasks.md`. Each phase README contains the actual challenges. |
| Starter convention | Every phase has `starter/`, using `.gitkeep` when no code is needed. Prefer working, benign starters; explicitly document intentional failures and unfinished outputs. |
| Solution location | A mirrored `challenges/v2-solutions/` tree with instructor solutions, explanation and `.sh` verification scripts. Exclude it from learner PDF/HTML extraction. |
| Timing | Every offered phase targets 45–120 minutes for a generalist junior technical learner. Estimate and audit the entire core journey. Record deviations; do not automatically remove content or rewrite estimates to pass the target. |
| Advanced work | A substantive, completable core with separate optional stretch, especially for the capstone. Preserve every existing exercise in v1 and map its proposed v2 disposition. |
| Notes synchronization | Challenge READMEs are the teaching-content authority. Generate short session summaries and instructor concept notes from them; include their complete learner-facing text in the main PDF appendix in a declared order. |
| New scope | The latest request introduces optional Kafka and advanced observability/Datadog planning. Earlier v4 exclusions describe the released edition; they do not silently remove these newly requested v2 topics. |

## Baseline and design risks

The current pack has five numbered challenges: readiness, Docker, dbt, Airflow and Atlas capstone. dbt, Airflow and Atlas already have two phases inside single long READMEs. Docker is a roughly 35-minute lab. Git, a dedicated Databricks CLI exercise and a Kafka learner exercise need new authoring. The current capstone explicitly estimates Phase 1 at 1–3 hours and all 14 Phase 2 extensions at 3+ hours; these are already timing exceptions to record.

Directory relocation affects more than Markdown links. `.mise.toml` resolves `challenges/<NN>-*`; verifiers calculate repository roots relative to their own location; reset writes into the shared `data_products/` tree; tests assume the five numbered directories; dbt/Airflow share fixtures; generated DAGs, profiles, home shortcuts and course adapters can also depend on the current layout. A plain folder move would break this system. [MIGRATION-MAP.md](MIGRATION-MAP.md) defines the compatibility and isolation work before any migration.

The supplied capstone data has no missing key columns, duplicate primary/composite keys or raw foreign-key orphans in the checked relationships. Static analysis of the reference domain filters and joins yields 9,880 valid trades from 10,000 raw trades, 3,717 positions and 1,028 reported portfolios. The conformed portfolio dimension has 2,500 rows: 1,472 have no qualifying trades and therefore do not enter the trade-driven report. This is a population-contract question, not evidence that an ID column is absent. Confirm it with live model counts and anti-joins before deciding whether to change data or report semantics.

The client container, Astro runtime, Cosmos environment and remote Databricks warehouse are distinct execution boundaries. Source pins do not prove installed versions. Plan exact version/API probes, read-only CLI access, prepared learner schemas and instructor provisioning before live rehearsal. An offline DAG check is not proof that a dbt task ran or that an event triggered the pipeline.

## Intended architecture

```text
challenges/
  README.md                       # version selector and readiness links
  v1/
    README.md                     # preserved numbered route
    CHANGES.md
    00-environment-check/ ... 04-atlas-capstone/
  v2/
    README.md                     # course route, optionality, prerequisites
    manifest.json                 # inventory/order/assessment metadata
    git/ ... docker/ ... dbt/ ... databricks-cli/ ... airflow/ ... kafka/ ... capstone/
      README.md                   # summary and timeline
      phase-one-certified/
        README.md                 # concepts + actual learner challenges
        starter/
      phase-two-proficient/
        README.md                 # core, then optional stretch; or not offered
        starter/
  v2-solutions/
    README.md
    manifest.json
    <tool>/<phase>/
      README.md
      solution/
      verify.sh
      verify-starter.sh
      evidence/README.md           # evidence protocol, no credentials or claimed runs
```

The diagram describes the implemented version directories. Verification results and outstanding runtime gates are recorded in the implementation review. Non-offered phases require no fake solution or script. Keep runtime logs in an ignored evidence directory outside committed solution assets. The environment readiness challenge remains preserved in v1; v2 navigation links to a version-aware readiness check without inventing an eighth tool phase.

Each active phase must be independently startable using its supplied baseline. Phase 2 accepts completed Phase 1 work or a prepared Phase 1 output fixture with identical semantics, so a learner can enter the advanced route without spending another phase reconstructing setup. Freeze the initial fixture, separate learner-authored paths from generated paths, and declare any write outside `starter/` in the workspace manifest.

## Proposed learner journeys

The detailed task/outcome and legacy mapping are in [CURRICULUM.md](CURRICULUM.md). These ranges are initial estimates, not observed completion times.

| Tool | Phase 1 core | Phase 2 core | Initial estimate, minutes |
|---|---|---|---|
| Git | Inspect a repository, commit, branch, merge and resolve a small conflict; explain history. | Clone a training repository, push a branch, use `gh` for a PR, review, revise and synchronize. | 60–90 / 75–110 |
| Docker | Run an image, open a shell, inspect lifecycle, write a simple Dockerfile and prove app output. | Build named targets from a multistage Dockerfile, separate build/runtime content and compare behavior. | 60–90 / 75–110 |
| dbt | Sources, typed staging, `ref`, grain, one small useful mart and minimum key/relationship checks. | Diagnose a join/reconciliation defect, build a substantive mart and demonstrate incremental replay behavior. | 75–110 / 90–120 |
| Databricks CLI | Establish identity/profile, distinguish workspace paths from catalogs, inspect accessible `training_dev` metadata and explain an access limitation. | Not offered. | 45–65 / N/A |
| Airflow | Author a small Python DAG with dbt tasks, dependencies, a run and a basic log/state check. | Implement and demonstrate failure/recovery and bounded replay; inspect the result in Astro's local UI. | 75–110 / 90–120 |
| Kafka, optional | Produce a dataset-arrived event; a supplied consumer bridge triggers prepared Airflow→dbt; inspect results and replay behavior. | Not offered. | 60–90 / N/A |
| Capstone | Build a meaningful Atlas slice, retain business keys, investigate population loss and demonstrate a consumer output with independent checks. | Complete a fixed advanced reporting/reconciliation core; explain and present the result; clearly separate the optional extensions. | 90–120 / 90–120 |

Datadog integration is a candidate Airflow Phase 2 stretch route after a working neutral failure/recovery core. It must teach an operational decision and inspect evidence; adding a YAML config or merely opening a screen is not advanced proficiency. Actual hosted Astronomer access is conditional; local Astro UI is the baseline. Kafka is optional across the course, not a hidden dependency of mandatory dbt/Airflow/capstone completion.

## Implementation work packages and dependencies

Implementation status:

| Package | Status |
|---|---|
| P0 | 728-file snapshot, baseline suite and path/runtime inventory captured; client-connected probes pending. |
| P1 | v1 migration and numeric routing implemented; fresh indexed compatibility suite passes. |
| P2 | Seven tool routes, twelve active phases, two inactive placeholders and sixty core tasks authored. |
| P3 | Local seed/build/test and independent raw-CSV per-key oracle verified; connected casts/counts pending. |
| P4 | Twenty-four offline Bash starter/reference checks executed; unavailable service gates recorded as blocked. |
| P5 | Per-task estimates reconcile within the band; timing audit and empty pilot ledger supplied. No junior pilot claimed. |
| P6 | All 39 learner READMEs generate complete appendix, session summaries and instructor concepts; drift checks implemented. |
| P7 | Full retained-depth PDF/HTML review candidate built; connected combined-route rehearsal, pilots and promotion pending. |

The work-package descriptions below remain the acceptance contract. A local result does not close a connected or human-pilot gate.

### P0 — freeze evidence and resolve runtime inputs

Record the exact Git revision when available, source hashes, file inventory, link targets, challenge README headings, task/reset destinations, cross-product dependencies and client/Catalyst versions. Capture existing offline-suite results in a disposable copy with the local Git metadata required by reset tests. Treat older RCA run results as historical evidence. Probe tools only in their real execution boundary when that environment is available.

Deliver a migration-input manifest, readiness matrix and source-to-v2 coverage ledger. The planning baseline is [the dated review](reviews/2026-10-05-baseline-review.md); [baseline-inputs.json](reviews/baseline-inputs.json) fingerprints the current project files. Gate: every maintained input is assigned to preservation, new content, compatibility update or historical reference; no existing learner block disappears from the ledger.

### P1 — migrate v1 and make version routing safe

Move the five current challenge directories, their index and change history to v1. Preserve challenge bodies and solution semantics; record unavoidable path-only changes separately. Keep existing numeric `mise run challenge:verify <NN>` and reset entry points selecting **v1**, so they cannot silently execute a new v2 topic. Introduce an explicit version/tool/phase interface for v2. Implement root resolution, paths, home links, selectors and scoped reset through a common resolver/manifest rather than more hardcoded relative depths.

Update current tests and current operational documentation; retain dated historical reports without falsely rewriting their historical paths. Protect v1/v2 runtime workspaces and learner schemas from cross-version resets. Gate: all five legacy challenges are reachable, verifiers and file-only resets retain their behavior, solution exclusion still works, and before/after source differences are explained.

### P2 — finalize authoring schema and write seven tool routes

Use [CHALLENGE-SPEC.md](CHALLENGE-SPEC.md) to implement the manifest schema, root/phase README templates, stable IDs, completion evidence and intentional-defect markers. Split the existing READMEs by concepts and proof, not simply halfway through the file. Preserve their clear Concept → Challenge → Hint → Check → optional variation style. Produce complete root indexes and phase READMEs for all seven tools; include explicit inactive-phase pages for Databricks CLI and Kafka.

Author Git and Docker first to exercise simple local workflows. Split and improve dbt next, then write the bounded CLI route. Airflow should consume a prepared tested dbt baseline. Kafka consumes prepared Airflow/dbt fixtures and remains optional. Atlas capstone follows the data-contract review. Gate: every core task has a reason, concrete learner deliverable, observable check and declared prerequisite; mere command execution cannot by itself prove advanced competence.

### P3 — resolve the capstone population contract

Reproduce the static review using seed/profile casts and compiled models in the approved warehouse. Record row counts at raw, filtered trade, position, joined and consumer grains. Check uniqueness, nulls, anti-joins, zero-activity portfolios, trade-ID retention and report grain. Distinguish expected 120 invalid-trade removals from unintended join loss. Decide whether the intended report represents active trading portfolios or every portfolio. If all portfolios are required, design the driving relation, left joins, null/zero semantics and reconciliations explicitly; do not blindly replace every inner join.

Add a bounded learner investigation with expected population counts and a controlled defective fixture. Promote basic key/relationship/population proof into Phase 1. Keep advanced analytics and history depth in Phase 2/stretch. Account for all 14 legacy extensions in the mapping. Gate: an independent output oracle catches the defect and the instructions state why any row is removed. Static review findings are not labelled live results.

### P4 — provide starters, solutions and verification

Create the mirrored instructor solution pack and shell verification entry points. Test baseline starters separately from solved behavior. A scaffold that intentionally returns a placeholder is a successful scaffold run, not a completed challenge. A deliberate failure must identify its command, expected symptom, explanation and repair objective in the learner's Check text.

Run solution checks on fresh disposable workspaces, twice where replay/idempotency matters. Demonstrate documented failure → diagnosis → repair; inspect meaningful outputs independently of the supplied solution. Keep offline, Docker and live/remote evidence distinct, and report unavailable prerequisites as blocked/skipped rather than PASS. Verify that scripts restore lock files and that reset/cleanup touches only declared learner assets and isolated training resources. Gate: instructor evidence binds each task ID to source hash, tool versions, command, exit/result and artifact; no credentials or stale warehouse outputs can falsely prove success.

### P5 — estimate and observe timing

Use [TIMING-AUDIT.md](reviews/TIMING-AUDIT.md) for per-task estimates, inclusive phase totals, junior pilot observations, machine wait time and instructor interventions. Pilot a complete core, not a solved-state gate. Record `under-band`, `in-band`, `over-band` or `unmeasured`; explain spread and setup barriers. Optional stretch has its own estimates and never supplies missing minutes to a core phase.

An estimate or observation outside 45–120 minutes creates an audit finding. **Do not fix timing exceptions as part of the audit.** Keep the original scope and evidence visible and propose any subsequent redesign as a separate decision. Gate: every offered phase has an honest estimate and review status; exceptions remain visible in instructor scheduling and release notes.

### P6 — generate course and instructor views from READMEs

Implement the deterministic, complete extraction specified in [COURSEWARE-SYNC.md](COURSEWARE-SYNC.md). Produce session summaries containing phase/core/stretch status, task IDs, concepts, timing, prerequisites and evidence. Reuse tool-root READMEs verbatim; generate the instructor demonstration/concept index from the corresponding concept headings and explanations. Append every learner README in the declared v2 tool/phase order, including nested stretch READMEs, to the main book.

Render code, tables, images, link destinations and intentional-defect notices legibly; give every task a stable appendix anchor. Exclude instructor solutions. Bind all generated views to source hashes and fail a synchronization check on drift, missing READMEs or unsupported structure. No length cap or summary extraction is permitted on the full appendix. Gate: changed challenge text updates inline summary, instructor view and full appendix in the same build; printed materials remain understandable without an external web page.

### P7 — rehearse the combined route and review a future course candidate

Use an isolated candidate, preserving the promoted v4 release. Run legacy compatibility, v2 starter/solution, Git/GitHub sandbox, Docker build/run, dbt, Airflow UI/run and optional Kafka event-chain checks at the applicable execution boundary. Verify event payload/data identity and output, not just receipt of a message. Pilot phase timing and whole-course scheduling separately: seven Phase 1 routes are not a single two-hour session.

Build a future book candidate only after the pack is sufficiently authored. Retain v4's restored course depth and its 100,000 substantive-word/237-readable-page minimums; those are course acceptance floors, not a word quota for this planning pack. Check source retention, all learner README coverage, full appendix readability and relevant session summaries. A page count alone is not acceptance. Gate: the review identifies all unresolved access/runtime/timing findings and compares old/new teaching coverage before a course promotion decision.

## Review responsibilities and completion criteria

The implementer maintains the coverage ledger, manifests and exact evidence. A technical reviewer checks tool/API behavior, isolation and independent results. An instructional reviewer checks explanation quality, minimum/advanced standards, concept placement and task progression. Junior pilot learners supply timing evidence; instructor feedback supplies demonstration and scheduling needs. A future team may allocate these roles, but this planning delivery does not claim independent reviews that have not occurred.

- [x] Inspect the current layout, dispatch/reset paths, phase structures and known RCAs.
- [x] Conduct a static capstone key/relationship/population review and label its limits.
- [x] Define version folders, phase exceptions, starter/solution conventions and the curriculum proposal.
- [x] Define a full-text appendix and single-source instructor/session views.
- [x] Record timing targets, existing exceptions and the no-automatic-fix rule.
- [x] Migrate v1 and verify offline compatibility.
- [x] Author the actual v2 challenges, starter code and solutions.
- [x] Execute local starter/reference checks with independent output and failure/replay evidence.
- [ ] Verify each active phase at its execution boundary and pilot timing.
- [x] Generate and review the local course candidate, retaining existing course depth.
- [ ] Complete connected rehearsal, representative learner pilots and independent course acceptance.

The versioned pack and review candidate are built. The implementation review names every unavailable live boundary and unobserved timing gate; these remain open rather than being reported as PASS.
