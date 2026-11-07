# Atlas ELT Demo Selector Alignment Design

## Objective
Align `atlas_elt_demo` dbt model naming and run selectors with `dpc-academy` conventions so validation commands execute real models.

## Root Cause
The command `--select +bronze_trades` (or another real dpc-style node selector) executes an actual model chain, while staging-wildcard guidance does not match the Atlas naming convention or the dpc-academy layer prefixes.

## Approved Design
1. Rename Atlas dbt model files/nodes to `bronze_*`, `silver_*`, `gold_*` by entity.
2. Keep this repository’s per-dataset folder structure and artifact layout unchanged.
3. Replace selector usage in validation/review with dpc-aligned selectors that execute real nodes (for example, `+bronze_trades` or explicit `bronze_*` model selectors), and ban staging-wildcard guidance.
4. Keep DAG, DAB, ODCS, runtime, and contract artifacts structurally unchanged.

## Verification Design
- Run dbt dependencies for `atlas_elt_demo`.
- Run seeds for Atlas entities.
- Run at least one real dpc-style model chain selector in devcontainer and confirm executed node output.
- Ensure structural parity tests continue passing after rename/refactor.

## Constraints
- Naming convention source of truth: `dpc-academy` conventions take precedence per user instruction.
- No geography/currency content introduced into `atlas_elt_demo`.
- No structural regression in dataset artifact folders.
