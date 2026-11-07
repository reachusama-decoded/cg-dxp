# V2 structure, authoring and verification contract

Status: proposed specification, 5 October 2026. See [PLAN.md](PLAN.md) for scope and work packages. All paths below describe a future challenge pack.

## File and inventory rules

Use `challenges/v2/<tool>/README.md` and `<tool>/<phase>/README.md` as the learner authorities. The root version README lists curriculum order, environment readiness, mandatory/optional routes and version-aware verification instructions. Tool READMEs give lightweight navigation and a task table, not independently authored copies of challenge prose.

All seven tools have both named phase directories and a `starter/` in each. Databricks CLI and Kafka Phase 2 pages say “not offered” and contain no tasks or invented timing. Kafka Phase 1 says “optional” in the version index, tool index, phase page, task manifest and generated teaching views. Empty starters use `.gitkeep` with a README note explaining that the work is CLI activity or evidence files.

The future `manifest.json` records, at minimum:

| Entity | Fields |
|---|---|
| Pack | schema version, challenge version, source revision/hash inventory, explicit tool order, generator version |
| Tool | ID, title, root README path, course day/session destination, phase order |
| Phase | ID, offered/optional status, phase README path, starter path, prerequisites, core estimate low/high, timing audit status |
| Task | Stable ID, title, concept IDs, core/stretch status, task order, source README + heading/anchor, estimated minutes, authored paths, success evidence |
| Runtime | execution boundary, version constraints/probe, preparation, identity/access needs, workspace/schema/topic ownership, cleanup |
| Starter | baseline command, expected exit/output, intentional-defect entries and affected task IDs |
| Solution | instructor path, verifier path, starter verifier path, expected outputs and evidence state |

Proposed task IDs use `git-p1-01`, `dbt-p2-02`, etc.; concept IDs such as `git-commit-history` survive moving a task between phases. Do not renumber IDs after publication merely to change presentation order. Root tables are checked against the manifest and phase headings. The manifest is structural metadata; explanations and actual learner instructions remain in READMEs. Neither metadata nor generated text becomes a second manually maintained source of task prose.

## Tool README template

```markdown
# <Tool> challenges

<What this tool is for and how this section fits the course.>

## Before you start
<Environment, prerequisites, where work is written, phase entry fixture.>

## Suggested timeline and tasks
| Phase | Task ID | Title | Concepts | Core/stretch | Minutes | Evidence |
| ... |

<Inclusive phase estimate and timing-audit link.>

## Choose your phase
<Links to phase READMEs; minimum standard vs advanced proficiency.>

## Teaching concepts
<Concept IDs/titles and demonstration opportunities.>
```

The timeline includes reading, authoring, checking and explaining results. If access/setup is prepared by the instructor, say so, with a separate preparation estimate. Phase 2 does not presume completion of an unpublished solution; ship its entry fixture and say which Phase 1 outcomes it represents.

## Phase README template

```markdown
# <Tool>: Phase <one/two> — <Certified/Proficient>

<Offered/optional status; minimum/advanced outcome.>

## Prerequisites and workspace
<Prepared entry baseline, directory, execution boundary and versions.>

## Starter behavior
<What works before edits, commands/output, declared intentional defects.>

## Timeline and completion standard
<Core task table, total range, independent evidence rubric.>

## Core challenges

### <task-id>: <task title>
#### Concept: <concept-id> — <plain title>
<Explain the concept, purpose and a concrete example before asking for work.>
#### Challenge
<Goal, exact authoring/activity, files, business/data result.>
#### Hint
<Enough orientation to start; do not reveal the entire answer.>
#### Check
<Command or inspection, expected outcome, evidence to retain.>
<If deliberately incomplete/broken: expected initial symptom and reason.>
#### Try a variation (optional)
<Small twist, clearly outside completion requirements.>

## Phase completion
<What artifacts and explanations meet the standard; verifier limits.>

## Optional stretch
<Distinct tasks with prerequisites/estimates, or links to stretch READMEs.>
```

Place stretch after all core tasks and the core completion gate. Keep any larger stretch routes under `phase-two-proficient/stretch/<topic>/README.md` with their own starter when appropriate; include them in the full appendix inventory. Core prerequisites must never depend on completing a stretch task. Checks should test understanding as well as behavior: for example, explaining a merge result, demonstrating replay without duplication, or accounting for a missing portfolio.

## Starter baseline and intentional defects

Three states must remain distinct: **valid starter**, **expected instructional failure**, and **completed solution**. Prefer a starter that starts/imports/compiles and prints an explanatory message or produces an explicitly labelled placeholder. A valid no-op DAG can import without claiming that it executed dbt. A placeholder SQL model may compile while producing no meaningful product; scope tests so unfinished downstream models do not cause unexplained eager-selection failures.

Where a failure is pedagogically needed, put a notice in that task's Check text and in the starter behavior section. Identify the affected file, command, expected nonzero exit/message class, why it is deliberate, and what success looks like after repair. Do not promise exact version-dependent log strings without measuring them. A malformed blank Dockerfile should not surprise a learner: either provide a benign buildable baseline or document the deliberate initial build failure precisely.

The starter verifier establishes the declared initial state. The solution verifier establishes the finished learning outcome. A starter passing its own check does not certify the learner. Both checks run from a fresh copy, not a workspace carrying yesterday's warehouse tables or a completed answer.

## Instructor solution and shell verification contract

Mirror active tool/phase paths beneath `challenges/v2-solutions/`. Each phase has a solution README explaining the reasoning, complete authored assets, `verify.sh`, and `verify-starter.sh`. An index maps stable task IDs to solution sections and scripts. Include empty solution directories only when CLI/evidence-based work genuinely needs no code; provide reference commands and expected observations instead.

Design Bash scripts with strict error handling, quoted paths, explicit repository/workspace discovery and cleanup traps. The exact interface is to be implemented, but it must support separated offline/live modes, safe help/dry-run descriptions and a disposable workspace. No verifier should silently reset a learner's current work, mutate a tracked lock file, clear an entire Airflow date range or delete unrelated resources. If end-to-end rehearsal applies solutions, it must use a fresh isolated copy and restore it on exit.

Verification must cover the steps the README tells a learner to take, as well as the final state. Check independently specified output values, grains, row populations and state transitions. Include failure/repair/replay where that is the learning objective. Use a paired GitHub sandbox or instructor review fixture without pretending a local file is a real PR. Assert Docker target outputs rather than inspecting Dockerfile keywords. Execute Airflow/dbt and inspect results for live completion rather than accepting DAG syntax as execution proof. Verify a Kafka event's identity reaches the intended DAG run and data output rather than accepting a producer exit code.

Required evidence: task/phase ID, source hashes, safe command, execution boundary, actual versions, prerequisite status, exit code, result assertions, run/artifact IDs, cleanup status and duration. Classify results as pass, fail, expected instructional failure, blocked or skipped. An unavailable cloud service cannot yield a live pass. Commit verification scripts and expected-output fixtures; keep raw logs ignored and sanitized. “Verified script” means there is an actual recorded run against its current hash, not simply an executable permission bit.

Existing dbt learner instructions favor direct `dbt ...` commands. Preserve this learning contract; wrappers may prepare the environment or verify/reset a challenge but should not hide the tool being taught. Review solution ignore rules and DAG discovery roots so the reference pack is never accidentally executed as learner code.
