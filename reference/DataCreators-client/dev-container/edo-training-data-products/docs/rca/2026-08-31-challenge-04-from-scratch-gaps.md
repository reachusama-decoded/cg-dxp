# Challenge 04 from-scratch validation gaps

**Date:** 2026-08-31
**Status:** Fixed and verified

## Impact

A maintainer could validate the solved Atlas project, but could not prove the learner journey from reset stubs through all Phase 1 and Phase 2 checks. Two Phase 2 exercises were also not reproducible from the shipped materials:

- Challenges 7 and 8 told learners to add dbt tests, while the corresponding solution YAML files were identical to the stubs and contained no tests.
- Challenge 10 told learners to inspect compiled SQL under the configured Unity Catalog Volume path, which is not mounted in the devcontainer.

## Root cause

The existing `verify.sh` validates the current or overlaid final project state. It does not reset the product, apply learner edits in section order, execute each documented command, validate Airflow, or retain session-scoped command evidence. The two documentation defects survived because final-state compilation did not exercise their learner instructions.

## Fix

- Extended `challenges/04-atlas-capstone/verify.sh` with a `--from-scratch` mode that resets, authors from shipped solutions in learner order, runs all executable checks, retains per-step logs, audits dbt invocations and tracked-file scope, stops Astro, and restores starter state. Its default no-argument mode remains the normal completion gate.
- Added a non-destructive `--review` mode that prints a plain-ASCII instructor synopsis of Phase 1 and all 14 Phase 2 challenges.
- Added the missing `non_negative` and `relationships` test declarations to the solution YAML files.
- Changed Challenge 10 to compile with a temporary local `--target-path` before inspecting the generated SQL.
- Added offline regression coverage for manifests, ordering, reset protection, solution deltas, and maintainer documentation.

## Verification

The finalized runner completed 67/67 executable steps twice from restored starter state. The full live gate built 28 models and passed 8 data tests on Databricks. Airflow loaded all 11 Atlas DAGs with no import errors, the advisor DAG details loaded, and the dynamic UI URL returned HTTP success. Each run restored all 28 placeholder model files and removed the learner-created exposure file. Evidence is retained under `.devcontainer/verify/04-atlas-capstone/` and intentionally ignored by Git.
