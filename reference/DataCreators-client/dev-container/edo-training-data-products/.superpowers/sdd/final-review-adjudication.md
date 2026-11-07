# Final Review Scope Adjudication

## Pipeline host mapping

The Harness pipeline mapping is already correct, so no pipeline code change was needed.

Proof: `.harness/edo-training-data-products-pipeline.yaml` already includes
`https://cg-db-aa00003661-sqa-us-east-1.cloud.databricks.com`,
`https://cg-db-aa00003661-sqa-us-west-2.cloud.databricks.com`,
`https://cg-db-aa00003661-prd-us-east-1.cloud.databricks.com`, and
`https://cg-db-aa00003661-prd-us-west-2.cloud.databricks.com`.

The modernization execution range starts at `7f00d9b` (2026-07-16, `test: add failing devcontainer dind and oauth wiring checks`). The following findings predate that boundary and were not changed in this fix pass.

## Finding 1 — Environment-specific Databricks hosts

**Adjudication: pre-existing and out of scope.**

- `git blame -L 360,361 .harness/edo-training-data-products-pipeline.yaml` attributes the development host at line 360 to the vended pipeline commit `e55c2c19` from 2026-07-14.
- `git blame -L 235,235` and `git blame -L 275,275 data_products/healthchecks/healthcheck_all_platforms.dag.py` attribute the SQA and production host values to `cc144835` from 2026-07-14.
- Both commits precede modernization commit `7f00d9b`.

These values were not replaced because the correct SQA and production workspace endpoints and matching Harness secrets are deployment inputs, not dev-container modernization details. Guessing replacements could route validation or deployment traffic to the wrong workspace. The deployment owners must supply authoritative environment mappings in a separate change.

## Finding 8 — `test_repo_structure.py` expects `data_products/orders`

**Adjudication: pre-existing and out of scope.**

- `git blame -L 32,39 data_products/test_repo_structure.py` attributes the `orders` expectation to initial commit `e97eb8c`.
- `git ls-tree -d --name-only 7f00d9b^:data_products` shows `.blueprints`, `.shared`, `asset_reference_data`, `healthchecks`, `shared_ref`, and `utils`; it does not show `orders`.
- `python -m pytest data_products/test_repo_structure.py -v` currently reports one failure: `data_products/orders/ directory must exist`; the other eight tests pass.

Neither restoring an `orders` data product nor changing an initial repository-structure contract is part of the dev-container modernization. The repository owner should separately decide whether to restore that product or remove the obsolete expectation.
