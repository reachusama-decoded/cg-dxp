# Evidence checklist

Use this to decide what to save. Suggested filenames organize your work; they are not a required implementation layout. Link the actual files in `SUBMISSION.md` and `reports/REPORT.md`. The instructor assesses their contents and observes your explanation.

## Record the working product

Run all commands in this checklist from your current product: `cd "$CG_PRODUCT_ROOT"`, then `python runtime/check_workspace.py`. Use the training-root setup in README for a new terminal. Switch the directory, CG_PRODUCT_ROOT and assigned target settings together for pair/fault work, then restore the personal settings before phase 3.

Save `runtime/check_workspace.py` output showing the absolute product/project/profile paths and assigned catalog/schema/prefix. Record the product folder and context for each run. Use a separate assignment for phase-2 pair work and return to your personal assignment in phase 3.

## Record a run

For each run or controlled test, record:

| Field | What to record |
|---|---|
| Code | The Git commit that ran; for team work, the integration repository and commit. Commit code before execution. |
| Input | The baseline or labeled fault input and its manifest/hash. |
| Execution | Where it ran, command or DAG ID, run ID, output prefix and result. |
| Check | The rule being tested, expected behavior, actual behavior and diagnostic rows or task states. |
| Artifact | A relative path to saved results, logs or receipts. Remove credentials and sensitive text. |
| Follow-up | Repair, rerun or unresolved blocker. Distinguish local checks from real warehouse/worker execution. |

Use `git rev-parse HEAD` to obtain the current commit identifier. Save a copy of dbt’s `target/run_results.json` and the relevant diagnostic output after each run, before a later run replaces them. Inspect logs before including them. Keep the inputs and output prefix associated with each copy so the instructor can trace it.

## Phase 0: reviewed design

| Save | What completion looks like |
|---|---|
| Readiness JSON in `evidence/phase-0/` | Requested local/connected checks pass, or the failing check and instructor recovery action are recorded. A blocker is not a completed connected check. |
| `docs/PRD.md` | Names the internal consumer, three enquiries, ETF starting scope and later team extension. States what cannot be answered. |
| ODCS contract and `docs/STTM.csv` | Describe the phase-1 row/key, fields, units, unknown values and source mappings. The public checker confirms edits; the instructor separately reviews meaning and validates the ODCS version. |
| `docs/design-decisions.md` and RFD | Record a Catalyst suggestion you checked, the correction and reason, one unresolved assumption, and the source-selection decision. |

After editing the design drafts, run `python public_checks/check_contract.py` from the project root. Its success message confirms the templates were edited; it does not approve their meaning. Save its output and any instructor contract review notes.

## Phase 1: individual ETF core

Save a compact `evidence/phase-1/checks.md` with links to:

- The tested code commit and dbt run/test results.
- A full comparison of expected versus output ETF IDs: no missing, extra or repeated IDs; all 25 are present once. Derive the expected set from the agreed source selection, not from the output itself.
- A check of each selected fee and its unit conversion against its source row; unknown reporting dates stay null.
- One source-to-output trace showing product ID, original fee/unit/date, output fee/unit/date and separate product/fee source references.
- The controlled conflict result: valid baseline passes; the instructor’s conflicting input fails the intended fee rule; the restored baseline passes. Identify the failing rule and diagnostic rows.
- Your observation slot/result and the `phase-1-submitted` tag. The instructor records formal observation separately.

A screenshot of five rows or a row count alone cannot establish ID membership or correct values. If a test fails because the environment is unavailable, record that blocker separately from input-quality rejection.

## Phase 2: pair catalogue and release

| Save | What completion looks like |
|---|---|
| `evidence/phase-2/catalogue-checks.md` | All 109 required IDs appear once. Fee values match selected source rows. Unknown SMA costs and unsupported or ambiguous returns remain visible with reasons. At least two different comparison-rejection reasons are demonstrated. |
| Contract/STTM revision | Agreed team column names/types, row meaning, source mappings and comparison rules match the integrated report. |
| `evidence/phase-2/release-runs.md` | Record baseline, controlled failure, repair and retry run IDs with their code/input identities and task states. |
| Saved callback event | Contains workflow/run/task/attempt/batch identifiers and error category; sensitive text is excluded. Delivering it twice produces one saved event for that attempt. A failure of the event writer is logged. |
| Accepted-output comparison | Save the accepted view definition and full product ID/value results before the fault and after it. They are unchanged; the failed candidate’s receipt task did not accept a release. After repair, acceptance succeeds; retrying the same repaired release preserves its identity. |
| Personal contribution | Link authored commits and at least one review/integration record. State which domain and additional responsibility you handled. |
| Personal AI skill example | Save the actual input, result, independent source/check review and revised instructions under `skills/<your-skill>/examples/`. |

Complete the baseline before asking the instructor to prepare the fault product. Let each owned run finish or stop it before editing the working product’s code or inputs. Restore the baseline product through the instructor’s prepared process, then repair/rerun and retry. A test that imports a callback or marks a task failed in the UI does not demonstrate an actual worker failure.

## Phase 3: both advanced components, individually

Start from the reviewed phase-2 pair baseline in your personal repository. Record that integration commit, then author both components yourself using personal workflow IDs and output prefixes.

| Your responsibility | Save | What completion looks like |
|---|---|---|
| Loader, macro, test and reports | Compiled SQL from both macro calls, history/test outputs, seven enquiry results and loader checks | Different column names use the same macro behavior. Invalid arguments/intervals and overlap in both clocks are rejected. Corrections retain prior knowledge and unaffected dates. Retries leave the stored facts unchanged; reused IDs with changed statements fail. No-match enquiries remain present. |
| Factory and execution | Two configurations, DAG graphs, actual personal run IDs/output prefixes and replay results | Configurations create distinct workflows and outputs, reject malformed settings and preserve required task order. A failed candidate is blocked; repair/replay runs through the worker. |
| Integration and explanation | `evidence/phase-3/checks.md`, your tested personal commit, expected-versus-actual results and a regression/repair | Both components work together in your project. Derive historical expected values independently from events. Explain both clocks, your own implementation and any missing connected evidence. |

Phase-2 pair work can supply the reviewed baseline; another person’s phase-3 implementation or run does not complete your assignment. Do not spend report or presentation time on optional exercises.

## Final submission

Complete the report prompts and personal speaking notes. `SUBMISSION.md` must identify your repository, tested personal code commits, exact phase-2 pair integration commit, personal phase-3 commit and evidence links. Commit the evidence/report and tag `capstone-submitted`. The instructor records the final tag’s commit outside your repository; your run records continue to point to the code that actually ran.

Missing or incomplete evidence should name the unmet requirement and next action. Do not substitute an intended result for an observed result.
