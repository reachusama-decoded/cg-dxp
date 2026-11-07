# Task 4 Report

## Status

Implemented Task 4. `atlas_elt_demo` now contains Atlas entity seeds and seed-backed staging, integration, and prepared dbt models for trades, instruments, portfolios, clients, advisors, funds, and fund_holdings.

Legacy `datasets/demo` and `demo_values.csv` content was removed. Product/profile configuration now uses the `atlas_elt_demo` project/profile names and includes the product seed path.

## TDD Evidence

Added `test_atlas_elt_demo_no_longer_uses_demo_dataset_names` before implementation. It initially failed because `datasets/demo` existed, then passed after migration.

Updated the obsolete demo-content parity test to assert all seven Atlas seed files.

## Validation

- Targeted pytest: PASS.
- `mise run dbt:deps atlas_elt_demo`: PASS.
- dbt seed wrapper: PASS; 7 seeds loaded.
- Planned `mise run dbt:run atlas_elt_demo -- --select +staging_*`: PASS exit status, but dbt selected no nodes because required artifact naming mirrors asset_reference_data as `stage_*`.
- Full `data_products/test_devcontainer_dind_wiring.py`: PASS, 40 tests.

## Concerns

The planned `+staging_*` selector currently matches no nodes because the required artifact names are `stage_<entity>.sql`, mirroring `asset_reference_data`; the command exits successfully but performs no model execution. dbt also emits deprecation and duplicate seed/model-name warnings, while seed loading completed successfully.

## Review Findings Fixes (2026-07-20)

### Status

Resolved all Task 4 findings. `stage_trades` now executes one dbt model successfully, rather than selecting zero nodes or failing during dependency inference.

### Changes

- Renamed the seven seed resources to `atlas_seed_<entity>.csv` and updated each matching staging model to reference that unique resource. This preserves the Atlas entity dataset and model structure while removing every seed/model resource-name collision.
- Added a regression test that asserts seed and model resource names are disjoint.
- Removed only terminal spaces and tabs from seed rows. A byte-level comparison against the pre-fix seeds confirmed each row is otherwise unchanged.
- Added regression coverage for terminal seed-row whitespace and the renamed Atlas seed files.

### Tests and Output

1. `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k atlas_elt_demo_no_longer_uses_demo_dataset_names`

   ```text
   1 passed, 41 deselected in 0.01s
   ```

2. `devcontainer exec --workspace-folder . bash -lc 'mise run dbt:deps atlas_elt_demo'`

   ```text
   Installed from <local @ ../../shared>
   Installed from version 0.8.6
   ```

3. `devcontainer exec --workspace-folder . bash -lc 'cd data_products/atlas_elt_demo && /opt/venv/bin/python ../../dbt_wrapper.py seed --project-dir . --profiles-dir dbt_profiles --target local'`

   ```text
   Completed successfully
   Done. PASS=7 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=7
   ```

4. `devcontainer exec --workspace-folder . bash -lc 'mise run dbt:run atlas_elt_demo -- --select stage_trades'`

   ```text
   1 of 1 OK created sql view model training_gqp.stage_trades [OK in 1.69s]
   Completed successfully
   Done. PASS=1 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=1
   ```

5. Additional regression validation:

   ```text
   python -m pytest -q data_products/test_devcontainer_dind_wiring.py
   42 passed in 0.12s

   Seed resource/model name collisions: none
   Remaining terminal seed-row whitespace: 0 rows
   ```

### Concerns

The required dbt commands continue to emit existing dbt deprecation notices and a `dbt_utils` update notice. They are non-blocking and outside Task 4 scope; duplicate resource-name notices are no longer emitted.

## Review Findings Fixes (2026-07-20, Prepared YAML Names)

### Status

Resolved the remaining Important finding. Prepared model entries in each `atlas_elt_demo` dataset YAML now use the actual dbt node name from the prepared SQL filename (`advisors`, `clients`, `fund_holdings`, `funds`, `instruments`, `portfolios`, `trades`) instead of the non-existent `prepared_<entity>` names, so the prepared model `meta` block is applied to the dbt nodes selected by path.

### Changes

- Updated all seven `data_products/atlas_elt_demo/datasets/*/dbt/*.yml` files to match prepared SQL filenames under `dbt/prepared/*.sql`.
- Added regression coverage that fails when a prepared YAML model entry uses `prepared_<entity>` instead of the SQL filename stem.

### Tests and Output

1. RED regression check before the YAML fix:

   Command:

   ```bash
   python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k atlas_prepared_model_yaml_names_match_sql_filenames
   ```

   Output:

   ```text
   F                                                                        [100%]
   =================================== FAILURES ===================================
   ___________ test_atlas_prepared_model_yaml_names_match_sql_filenames ___________

       def test_atlas_prepared_model_yaml_names_match_sql_filenames() -> None:
           root = REPO_ROOT / "data_products" / "atlas_elt_demo" / "datasets"
           for path in root.glob("*/dbt/*.yml"):
               dataset = path.parent.parent.name
               text = path.read_text(encoding="utf-8")
   >           assert f"- name: {dataset}\n" in text, str(path.relative_to(root))
   E           AssertionError: clients/dbt/clients.yml
   E           assert '- name: clients\n' in 'version: 2\n\nmodels:\n  - name: stage_clients\n    config:\n      meta:\n        enabled: true\n        domain: atla...\n        domain: atlas_elt_demo\n        dataset_type: master\n        load_type: full\n        table_name: clients\n'

   data_products/test_devcontainer_dind_wiring.py:134: AssertionError
   =========================== short test summary info ============================
   FAILED data_products/test_devcontainer_dind_wiring.py::test_atlas_prepared_model_yaml_names_match_sql_filenames
   1 failed, 42 deselected in 0.06s
   ```

2. Required pytest check:

   Command:

   ```bash
   python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k atlas_elt_demo_no_longer_uses_demo_dataset_names
   ```

   Output:

   ```text
   .                                                                        [100%]
   1 passed, 42 deselected in 0.01s
   ```

3. Prepared YAML regression check after the fix:

   Command:

   ```bash
   python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k atlas_prepared_model_yaml_names_match_sql_filenames
   ```

   Output:

   ```text
   .                                                                        [100%]
   1 passed, 42 deselected in 0.02s
   ```

4. Required prepared-model dbt listing:

   Command:

   ```bash
   devcontainer exec --workspace-folder . bash -lc 'cd data_products/atlas_elt_demo && dbt ls --profiles-dir dbt_profiles --select path:datasets/*/dbt/prepared/*.sql --output json'
   ```

   Output:

   ```text
   03:10:50  Running with dbt=1.11.8
   WARNING:thrift.transport.sslcompat:using legacy validation callback
   03:10:52  [WARNING]: Deprecated functionality
   The `target-path` config in `dbt_project.yml` has been deprecated, and will no
   longer be supported in a future version of dbt-core. If you wish to write dbt
   artifacts to a custom directory, please use the --target-path CLI flag or
   DBT_TARGET_PATH env var instead.
   03:10:52  Registered adapter: databricks=1.11.7
   03:10:52  [WARNING]: Use managed Iceberg tables when table_format is iceberg. When this flag is disabled, UniForm is used instead.
   You may opt into the new behavior sooner by setting `flags.use_managed_iceberg` to `True` in `dbt_project.yml`.
   Visit https://docs.getdbt.com/reference/global-configs/behavior-changes for more information.
   03:10:52  Unable to do partial parsing because config vars, config profile, or config target have changed
   03:10:55  [WARNING]: Enable concurrent execution of microbatch incremental batches. When enabled, dbt will run microbatch batches in parallel threads instead of sequentially. The microbatch strategy itself requires dbt-core 1.9+; this flag controls whether batches run concurrently.
   You may opt into the new behavior sooner by setting `flags.use_concurrent_microbatch` to `True` in `dbt_project.yml`.
   Visit https://docs.getdbt.com/reference/global-configs/behavior-changes for more information.
   03:10:55  Found 21 models, 7 seeds, 1066 macros
   {"name": "advisors", "resource_type": "model", "package_name": "atlas_elt_demo", "original_file_path": "datasets/advisors/dbt/prepared/advisors.sql", "unique_id": "model.atlas_elt_demo.advisors", "alias": "prepared_advisors", "config": {"enabled": true, "alias": "prepared_advisors", "schema": "atlas_elt_demo", "database": null, "tags": [], "meta": {"enabled": true, "domain": "atlas_elt_demo", "dataset_type": "master", "load_type": "full", "table_name": "advisors"}, "group": null, "materialized": "view", "incremental_strategy": null, "batch_size": null, "lookback": 1, "begin": null, "persist_docs": {}, "post-hook": [], "pre-hook": [], "quoting": {}, "column_types": {}, "full_refresh": null, "unique_key": null, "on_schema_change": "ignore", "on_configuration_change": "apply", "grants": {}, "packages": [], "docs": {"show": true, "node_color": null}, "contract": {"enforced": false, "alias_types": true}, "event_time": null, "concurrent_batches": null, "access": "protected", "freshness": null}, "tags": [], "depends_on": {"macros": [], "nodes": ["model.atlas_elt_demo.int_advisors"]}}
   {"name": "clients", "resource_type": "model", "package_name": "atlas_elt_demo", "original_file_path": "datasets/clients/dbt/prepared/clients.sql", "unique_id": "model.atlas_elt_demo.clients", "alias": "prepared_clients", "config": {"enabled": true, "alias": "prepared_clients", "schema": "atlas_elt_demo", "database": null, "tags": [], "meta": {"enabled": true, "domain": "atlas_elt_demo", "dataset_type": "master", "load_type": "full", "table_name": "clients"}, "group": null, "materialized": "view", "incremental_strategy": null, "batch_size": null, "lookback": 1, "begin": null, "persist_docs": {}, "post-hook": [], "pre-hook": [], "quoting": {}, "column_types": {}, "full_refresh": null, "unique_key": null, "on_schema_change": "ignore", "on_configuration_change": "apply", "grants": {}, "packages": [], "docs": {"show": true, "node_color": null}, "contract": {"enforced": false, "alias_types": true}, "event_time": null, "concurrent_batches": null, "access": "protected", "freshness": null}, "tags": [], "depends_on": {"macros": [], "nodes": ["model.atlas_elt_demo.int_clients"]}}
   {"name": "fund_holdings", "resource_type": "model", "package_name": "atlas_elt_demo", "original_file_path": "datasets/fund_holdings/dbt/prepared/fund_holdings.sql", "unique_id": "model.atlas_elt_demo.fund_holdings", "alias": "prepared_fund_holdings", "config": {"enabled": true, "alias": "prepared_fund_holdings", "schema": "atlas_elt_demo", "database": null, "tags": [], "meta": {"enabled": true, "domain": "atlas_elt_demo", "dataset_type": "master", "load_type": "full", "table_name": "fund_holdings"}, "group": null, "materialized": "view", "incremental_strategy": null, "batch_size": null, "lookback": 1, "begin": null, "persist_docs": {}, "post-hook": [], "pre-hook": [], "quoting": {}, "column_types": {}, "full_refresh": null, "unique_key": null, "on_schema_change": "ignore", "on_configuration_change": "apply", "grants": {}, "packages": [], "docs": {"show": true, "node_color": null}, "contract": {"enforced": false, "alias_types": true}, "event_time": null, "concurrent_batches": null, "access": "protected", "freshness": null}, "tags": [], "depends_on": {"macros": [], "nodes": ["model.atlas_elt_demo.int_fund_holdings"]}}
   {"name": "funds", "resource_type": "model", "package_name": "atlas_elt_demo", "original_file_path": "datasets/funds/dbt/prepared/funds.sql", "unique_id": "model.atlas_elt_demo.funds", "alias": "prepared_funds", "config": {"enabled": true, "alias": "prepared_funds", "schema": "atlas_elt_demo", "database": null, "tags": [], "meta": {"enabled": true, "domain": "atlas_elt_demo", "dataset_type": "master", "load_type": "full", "table_name": "funds"}, "group": null, "materialized": "view", "incremental_strategy": null, "batch_size": null, "lookback": 1, "begin": null, "persist_docs": {}, "post-hook": [], "pre-hook": [], "quoting": {}, "column_types": {}, "full_refresh": null, "unique_key": null, "on_schema_change": "ignore", "on_configuration_change": "apply", "grants": {}, "packages": [], "docs": {"show": true, "node_color": null}, "contract": {"enforced": false, "alias_types": true}, "event_time": null, "concurrent_batches": null, "access": "protected", "freshness": null}, "tags": [], "depends_on": {"macros": [], "nodes": ["model.atlas_elt_demo.int_funds"]}}
   {"name": "instruments", "resource_type": "model", "package_name": "atlas_elt_demo", "original_file_path": "datasets/instruments/dbt/prepared/instruments.sql", "unique_id": "model.atlas_elt_demo.instruments", "alias": "prepared_instruments", "config": {"enabled": true, "alias": "prepared_instruments", "schema": "atlas_elt_demo", "database": null, "tags": [], "meta": {"enabled": true, "domain": "atlas_elt_demo", "dataset_type": "master", "load_type": "full", "table_name": "instruments"}, "group": null, "materialized": "view", "incremental_strategy": null, "batch_size": null, "lookback": 1, "begin": null, "persist_docs": {}, "post-hook": [], "pre-hook": [], "quoting": {}, "column_types": {}, "full_refresh": null, "unique_key": null, "on_schema_change": "ignore", "on_configuration_change": "apply", "grants": {}, "packages": [], "docs": {"show": true, "node_color": null}, "contract": {"enforced": false, "alias_types": true}, "event_time": null, "concurrent_batches": null, "access": "protected", "freshness": null}, "tags": [], "depends_on": {"macros": [], "nodes": ["model.atlas_elt_demo.int_instruments"]}}
   {"name": "portfolios", "resource_type": "model", "package_name": "atlas_elt_demo", "original_file_path": "datasets/portfolios/dbt/prepared/portfolios.sql", "unique_id": "model.atlas_elt_demo.portfolios", "alias": "prepared_portfolios", "config": {"enabled": true, "alias": "prepared_portfolios", "schema": "atlas_elt_demo", "database": null, "tags": [], "meta": {"enabled": true, "domain": "atlas_elt_demo", "dataset_type": "master", "load_type": "full", "table_name": "portfolios"}, "group": null, "materialized": "view", "incremental_strategy": null, "batch_size": null, "lookback": 1, "begin": null, "persist_docs": {}, "post-hook": [], "pre-hook": [], "quoting": {}, "column_types": {}, "full_refresh": null, "unique_key": null, "on_schema_change": "ignore", "on_configuration_change": "apply", "grants": {}, "packages": [], "docs": {"show": true, "node_color": null}, "contract": {"enforced": false, "alias_types": true}, "event_time": null, "concurrent_batches": null, "access": "protected", "freshness": null}, "tags": [], "depends_on": {"macros": [], "nodes": ["model.atlas_elt_demo.int_portfolios"]}}
   {"name": "trades", "resource_type": "model", "package_name": "atlas_elt_demo", "original_file_path": "datasets/trades/dbt/prepared/trades.sql", "unique_id": "model.atlas_elt_demo.trades", "alias": "prepared_trades", "config": {"enabled": true, "alias": "prepared_trades", "schema": "atlas_elt_demo", "database": null, "tags": [], "meta": {"enabled": true, "domain": "atlas_elt_demo", "dataset_type": "master", "load_type": "full", "table_name": "trades"}, "group": null, "materialized": "view", "incremental_strategy": null, "batch_size": null, "lookback": 1, "begin": null, "persist_docs": {}, "post-hook": [], "pre-hook": [], "quoting": {}, "column_types": {}, "full_refresh": null, "unique_key": null, "on_schema_change": "ignore", "on_configuration_change": "apply", "grants": {}, "packages": [], "docs": {"show": true, "node_color": null}, "contract": {"enforced": false, "alias_types": true}, "event_time": null, "concurrent_batches": null, "access": "protected", "freshness": null}, "tags": [], "depends_on": {"macros": [], "nodes": ["model.atlas_elt_demo.int_trades"]}}
   03:10:55  [WARNING][DeprecationsSummary]: Deprecated functionality
   Summary of encountered deprecations:
   - ConfigTargetPathDeprecation: 1 occurrence
   To see all deprecation instances instead of just the first occurrence of each,
   run command again with the `--show-all-deprecations` flag. You may also need to
   run with `--no-partial-parse` as some deprecations are only encountered during
   parsing.
   ```

### Concerns

The required dbt listing passes and shows all seven prepared dbt node names now match SQL filenames. Existing dbt deprecation/behavior-change warnings remain non-blocking and outside this fix.

---

# Task 4: OAuth token metastore-only docs update — Report

Status: Completed

Commits:
- f707e2db41e9eea5ebe019b869446c2037b3046c  (docs: align databricks oauth airflow token source-of-truth)

One-line tests run (successful):
- pytest data_products/test_devcontainer_dind_wiring.py::test_docs_state_oauth_token_not_persisted_in_airflow_settings - PASS
- pytest data_products/test_devcontainer_dind_wiring.py -q -> 98 passed

Concerns:

- None functional: all targeted tests passed. Note: many unrelated local file changes were present in the working tree; I only staged and committed the four files required by Task 4.

---

# Task 4: Challenge 00 — environment check (this run)

What I implemented

- Created challenges/v1/00-environment-check/README.md (devcontainer-framed guide)
- Created challenges/v1/00-environment-check/verify.sh (executable verify script)
- Added tests/challenges/offline/test_ch00.py (offline gate tests)

What I tested and test results

- Ran focused pytest before making changes: the README contained the word "laptop", causing the devcontainer reframe assertion to fail (RED).
- After updating README and adding the verify script and test, the focused pytest passed.

TDD Evidence

RED (before implementation)

Command run:
  cd /Users/gqp/Downloads/repos/emu/edo-training-data-products && pytest -q tests/challenges/offline/test_ch00.py -q

Relevant failing output:
  .F                                                                       [100%]
  =================================== FAILURES ===================================
  _____________________ test_guide_reframed_for_devcontainer _____________________
  E       AssertionError: assert ('byod' not in '00 — enviro...tructions.\n'
  E         'byod' is contained here:
  E           tructions. and 'laptop' not in '00 — enviro...tructions.\n'
  E         'laptop' is contained here:
  E           g on your laptop. if something is missing, prefer the devcontainer workflow and follow the repo's getting_started.md and .devcontainer/readme.md instructions.

Why failure was expected: The test asserts the README must mention "devcontainer" and must not mention "byod" or "laptop". The initial README draft contained the word "laptop", so the assertion correctly failed.

GREEN (after implementation)

Command run:
  cd /Users/gqp/Downloads/repos/emu/edo-training-data-products && pytest -q tests/challenges/offline/test_ch00.py -q

Relevant passing output:
  ..                                                                       [100%]

Files changed

- challenges/v1/00-environment-check/README.md (new)
- challenges/v1/00-environment-check/verify.sh (new, +x)
- tests/challenges/offline/test_ch00.py (new)

Self-review findings

- Completeness: I implemented the guide and verify script per the brief and added the offline tests that assert the README is devcontainer-framed and the verify script is executable.
- Quality: README is concise and references the devcontainer workflow. verify.sh matches the brief and exits non-zero with clear messages when checks fail.
- Discipline: I made only the requested files and a report. No unrelated changes were introduced.

Issues or concerns

- None functional. The verify.sh requires dpc-check, databricks, and astro CLIs to be present in the devcontainer; in CI those may be absent and the live verify will fail, which is acceptable per the brief (the offline pytest is the CI gate).