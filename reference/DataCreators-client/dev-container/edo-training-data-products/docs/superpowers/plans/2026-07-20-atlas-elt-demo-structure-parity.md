# Atlas ELT Demo Structure Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `data_products/atlas_elt_demo` so it mirrors `asset_reference_data` artifact structure while using Atlas entities/data (`trades`, `instruments`, `portfolios`, `clients`, `advisors`, `funds`, `fund_holdings`).

**Architecture:** Use `asset_reference_data` as the structural template and replace dataset domain content with Atlas entities from `dpc-academy`. Keep per-dataset artifacts (`airflow`, `bundle`, `contract`, `dbt`, `runtime`) and product-level deployment files (`databricks.yml`, `variables`, init scripts, Python helpers). Preserve repo task entrypoints so dbt commands run through existing `mise`/`dbt_wrapper` flow.

**Tech Stack:** dbt Core + dbt-databricks, Databricks Asset Bundles YAML, Airflow DAG YAML, ODCS YAML contracts, pytest.

## Global Constraints

- Mirror `asset_reference_data` structure at the data-product and dataset levels.
- Do not include geography/currency content in `atlas_elt_demo`.
- Dataset folders must be named after Atlas entities: `trades`, `instruments`, `portfolios`, `clients`, `advisors`, `funds`, `fund_holdings`.
- Include per-dataset artifact categories: `airflow/`, `bundle/`, `contract/`, `dbt/`, `runtime/`, and migration doc pattern.
- Keep dbt runnable in devcontainer using existing repo commands.

---

### Task 1: Lock Structure Parity Requirements with Failing Tests

**Files:**
- Modify: `data_products/test_devcontainer_dind_wiring.py`
- Test: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: `REPO_ROOT` filesystem helper pattern already used in the test file.
- Produces: Structural contract tests that subsequent tasks satisfy.

- [ ] **Step 1: Write the failing test**

```python
def test_atlas_elt_demo_matches_asset_reference_data_product_shell() -> None:
    root = REPO_ROOT / "data_products" / "atlas_elt_demo"
    required_paths = [
        "databricks.yml",
        "dbt_project.yml",
        "dbt_profiles/profiles.yml",
        "packages.yml",
        "requirements.txt",
        "dqf_requirements.txt",
        "DATABRICKS_RUNTIME_VERSION",
        ".dbtignore",
        ".copier-answers.yml",
        "variables/variables.yml",
        "variables/clusters.yml",
        "init_scripts/install_requirements.sh",
        "python/main.py",
        "shared/tests/.gitkeep",
        "datasets/sources.yml",
    ]
    for rel in required_paths:
        assert (root / rel).exists(), rel
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k atlas_elt_demo_matches_asset_reference_data_product_shell`
Expected: FAIL on missing required paths under `data_products/atlas_elt_demo`.

- [ ] **Step 3: Write minimal implementation**

```python
# In the same file, add a second failing test for atlas entity dataset folders.
def test_atlas_elt_demo_has_all_atlas_entity_dataset_folders() -> None:
    root = REPO_ROOT / "data_products" / "atlas_elt_demo" / "datasets"
    for name in [
        "trades",
        "instruments",
        "portfolios",
        "clients",
        "advisors",
        "funds",
        "fund_holdings",
    ]:
        assert (root / name).is_dir(), name
```

- [ ] **Step 4: Run tests to verify both fail**

Run: `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k "atlas_elt_demo_matches_asset_reference_data_product_shell or atlas_elt_demo_has_all_atlas_entity_dataset_folders"`
Expected: FAIL (red state confirmed).

- [ ] **Step 5: Commit**

```bash
git add data_products/test_devcontainer_dind_wiring.py
git commit -m "test: define atlas_elt_demo parity contract"
```

### Task 2: Build Product-Level Shell by Copying Parity Baseline

**Files:**
- Create/Modify: `data_products/atlas_elt_demo/databricks.yml`
- Create/Modify: `data_products/atlas_elt_demo/.copier-answers.yml`
- Create/Modify: `data_products/atlas_elt_demo/.dbtignore`
- Create/Modify: `data_products/atlas_elt_demo/DATABRICKS_RUNTIME_VERSION`
- Create/Modify: `data_products/atlas_elt_demo/dbt_project.yml`
- Create/Modify: `data_products/atlas_elt_demo/dbt_profiles/profiles.yml`
- Create/Modify: `data_products/atlas_elt_demo/packages.yml`
- Create: `data_products/atlas_elt_demo/requirements.txt`
- Create: `data_products/atlas_elt_demo/dqf_requirements.txt`
- Create tree: `data_products/atlas_elt_demo/variables/*`
- Create tree: `data_products/atlas_elt_demo/init_scripts/*`
- Create tree: `data_products/atlas_elt_demo/python/*`
- Create tree: `data_products/atlas_elt_demo/shared/{analyses,seeds,snapshots,tests,macros}/.gitkeep`
- Test: `data_products/test_devcontainer_dind_wiring.py::test_atlas_elt_demo_matches_asset_reference_data_product_shell`

**Interfaces:**
- Consumes: Structural test from Task 1.
- Produces: Product shell expected by bundle/dbt/runtime tooling.

- [ ] **Step 1: Write the failing test**

```python
# Keep Task 1 test as the failing guard; do not alter assertions.
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest -q data_products/test_devcontainer_dind_wiring.py::test_atlas_elt_demo_matches_asset_reference_data_product_shell`
Expected: FAIL with missing shell files.

- [ ] **Step 3: Write minimal implementation**

```bash
cp data_products/asset_reference_data/.copier-answers.yml data_products/atlas_elt_demo/.copier-answers.yml
cp data_products/asset_reference_data/.dbtignore data_products/atlas_elt_demo/.dbtignore
cp data_products/asset_reference_data/DATABRICKS_RUNTIME_VERSION data_products/atlas_elt_demo/DATABRICKS_RUNTIME_VERSION
cp data_products/asset_reference_data/databricks.yml data_products/atlas_elt_demo/databricks.yml
cp data_products/asset_reference_data/requirements.txt data_products/atlas_elt_demo/requirements.txt
cp data_products/asset_reference_data/dqf_requirements.txt data_products/atlas_elt_demo/dqf_requirements.txt
cp -R data_products/asset_reference_data/variables data_products/atlas_elt_demo/
cp -R data_products/asset_reference_data/init_scripts data_products/atlas_elt_demo/
cp -R data_products/asset_reference_data/python data_products/atlas_elt_demo/
mkdir -p data_products/atlas_elt_demo/shared/{analyses,seeds,snapshots,tests,macros}
touch data_products/atlas_elt_demo/shared/{analyses,seeds,snapshots,tests,macros}/.gitkeep
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -q data_products/test_devcontainer_dind_wiring.py::test_atlas_elt_demo_matches_asset_reference_data_product_shell`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add data_products/atlas_elt_demo data_products/test_devcontainer_dind_wiring.py
git commit -m "feat: scaffold atlas_elt_demo product shell"
```

### Task 3: Add Atlas-Named Dataset Artifact Trees

**Files:**
- Create tree for each dataset:
  - `data_products/atlas_elt_demo/datasets/trades/{airflow,bundle,contract,dbt,runtime}`
  - `data_products/atlas_elt_demo/datasets/instruments/{airflow,bundle,contract,dbt,runtime}`
  - `data_products/atlas_elt_demo/datasets/portfolios/{airflow,bundle,contract,dbt,runtime}`
  - `data_products/atlas_elt_demo/datasets/clients/{airflow,bundle,contract,dbt,runtime}`
  - `data_products/atlas_elt_demo/datasets/advisors/{airflow,bundle,contract,dbt,runtime}`
  - `data_products/atlas_elt_demo/datasets/funds/{airflow,bundle,contract,dbt,runtime}`
  - `data_products/atlas_elt_demo/datasets/fund_holdings/{airflow,bundle,contract,dbt,runtime}`
- Create: `data_products/atlas_elt_demo/datasets/sources.yml`
- Modify: `data_products/test_devcontainer_dind_wiring.py`
- Test: `data_products/test_devcontainer_dind_wiring.py::test_atlas_elt_demo_has_all_atlas_entity_dataset_folders`

**Interfaces:**
- Consumes: dataset-folder test from Task 1.
- Produces: Atlas dataset topology discoverable by loaders/bundle includes.

- [ ] **Step 1: Write the failing test**

```python
def test_each_atlas_dataset_has_required_artifact_directories() -> None:
    base = REPO_ROOT / "data_products" / "atlas_elt_demo" / "datasets"
    required = ["airflow", "bundle", "contract", "dbt", "runtime"]
    for dataset in ["trades", "instruments", "portfolios", "clients", "advisors", "funds", "fund_holdings"]:
        for child in required:
            assert (base / dataset / child).is_dir(), f"{dataset}/{child}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k "atlas_elt_demo_has_all_atlas_entity_dataset_folders or each_atlas_dataset_has_required_artifact_directories"`
Expected: FAIL due to missing dataset trees.

- [ ] **Step 3: Write minimal implementation**

```bash
for d in trades instruments portfolios clients advisors funds fund_holdings; do
  mkdir -p "data_products/atlas_elt_demo/datasets/$d"/{airflow,bundle,contract/dbt,contract/migrations,dbt/staging,dbt/integration,dbt/prepared,runtime}
  cp data_products/asset_reference_data/datasets/currency/airflow/currency.dag.yml "data_products/atlas_elt_demo/datasets/$d/airflow/${d}.dag.yml"
  cp data_products/asset_reference_data/datasets/currency/bundle/currency.job.yml "data_products/atlas_elt_demo/datasets/$d/bundle/${d}.job.yml"
  cp data_products/asset_reference_data/datasets/currency/bundle/currency_dq.job.yml "data_products/atlas_elt_demo/datasets/$d/bundle/${d}_dq.job.yml"
  cp data_products/asset_reference_data/datasets/currency/contract/currency.odcs.yaml "data_products/atlas_elt_demo/datasets/$d/contract/${d}.odcs.yaml"
  cp data_products/asset_reference_data/datasets/currency/runtime/dq_verify.py "data_products/atlas_elt_demo/datasets/$d/runtime/dq_verify.py"
  cp data_products/asset_reference_data/datasets/currency/cspn_migration.md "data_products/atlas_elt_demo/datasets/$d/cspn_migration.md"
done
cp data_products/asset_reference_data/datasets/sources.yml data_products/atlas_elt_demo/datasets/sources.yml
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k "atlas_elt_demo_has_all_atlas_entity_dataset_folders or each_atlas_dataset_has_required_artifact_directories"`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add data_products/atlas_elt_demo/datasets data_products/test_devcontainer_dind_wiring.py
git commit -m "feat: add atlas entity dataset artifact trees"
```

### Task 4: Replace Demo dbt Content with Atlas Entity Models and Seeds

**Files:**
- Create/Modify: `data_products/atlas_elt_demo/seeds/*.csv`
- Create/Modify: `data_products/atlas_elt_demo/datasets/*/dbt/*.yml`
- Create/Modify: `data_products/atlas_elt_demo/datasets/*/dbt/{staging,integration,prepared}/*.sql`
- Modify: `data_products/atlas_elt_demo/dbt_project.yml`
- Modify: `data_products/atlas_elt_demo/dbt_profiles/profiles.yml`
- Test: targeted dbt execution via `mise` commands

**Interfaces:**
- Consumes: dataset artifact tree from Task 3.
- Produces: atlas-based dbt graph compatible with repo wrapper commands.

- [ ] **Step 1: Write the failing test**

```python
def test_atlas_elt_demo_no_longer_uses_demo_dataset_names() -> None:
    root = REPO_ROOT / "data_products" / "atlas_elt_demo"
    assert not (root / "datasets" / "demo").exists()
    text = (root / "dbt_project.yml").read_text()
    assert "demo_values" not in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k atlas_elt_demo_no_longer_uses_demo_dataset_names`
Expected: FAIL while legacy `demo` naming still exists.

- [ ] **Step 3: Write minimal implementation**

```bash
rm -rf data_products/atlas_elt_demo/datasets/demo data_products/atlas_elt_demo/seeds/demo_values.csv
cp data_products/asset_reference_data/dbt_project.yml data_products/atlas_elt_demo/dbt_project.yml
cp data_products/asset_reference_data/dbt_profiles/profiles.yml data_products/atlas_elt_demo/dbt_profiles/profiles.yml
for seed in trades instruments portfolios clients advisors funds fund_holdings; do
  gh api "repos/cg-open-itg/dpc-academy/contents/dbt/seeds/${seed}.csv" \
    --jq '.content' | tr -d '\n' | base64 --decode > "data_products/atlas_elt_demo/seeds/${seed}.csv"
done
for d in trades instruments portfolios clients advisors funds fund_holdings; do
  cp data_products/asset_reference_data/datasets/currency/dbt/currency.yml "data_products/atlas_elt_demo/datasets/$d/dbt/${d}.yml"
  cp data_products/asset_reference_data/datasets/currency/dbt/staging/stage_currency.sql "data_products/atlas_elt_demo/datasets/$d/dbt/staging/stage_${d}.sql"
  cp data_products/asset_reference_data/datasets/currency/dbt/integration/int_currency.sql "data_products/atlas_elt_demo/datasets/$d/dbt/integration/int_${d}.sql"
  cp data_products/asset_reference_data/datasets/currency/dbt/prepared/currency.sql "data_products/atlas_elt_demo/datasets/$d/dbt/prepared/${d}.sql"
done
```

- [ ] **Step 4: Run tests and dbt to verify it passes**

Run:
1. `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k atlas_elt_demo_no_longer_uses_demo_dataset_names`
2. `devcontainer exec --workspace-folder . bash -lc 'mise run dbt:deps atlas_elt_demo'`
3. `devcontainer exec --workspace-folder . bash -lc 'cd data_products/atlas_elt_demo && /opt/venv/bin/python ../../dbt_wrapper.py seed --project-dir . --profiles-dir dbt_profiles --target local'`
4. `devcontainer exec --workspace-folder . bash -lc 'mise run dbt:run atlas_elt_demo -- --select +staging_*'`
Expected: pytest PASS and dbt commands complete successfully.

- [ ] **Step 5: Commit**

```bash
git add data_products/atlas_elt_demo data_products/test_devcontainer_dind_wiring.py
git commit -m "feat: migrate atlas_elt_demo to atlas entity dbt content"
```

### Task 5: Final Contract Parity Validation and Cleanup

**Files:**
- Modify: `data_products/test_devcontainer_dind_wiring.py`
- Test: full targeted parity suite

**Interfaces:**
- Consumes: completed scaffold + dbt graph from prior tasks.
- Produces: final confidence checks for structural parity and runnable state.

- [ ] **Step 1: Write the failing test**

```python
def test_each_atlas_dataset_has_dag_bundle_contract_runtime_files() -> None:
    base = REPO_ROOT / "data_products" / "atlas_elt_demo" / "datasets"
    names = ["trades", "instruments", "portfolios", "clients", "advisors", "funds", "fund_holdings"]
    for name in names:
        assert (base / name / "airflow" / f"{name}.dag.yml").is_file()
        assert (base / name / "bundle" / f"{name}.job.yml").is_file()
        assert (base / name / "bundle" / f"{name}_dq.job.yml").is_file()
        assert (base / name / "contract" / f"{name}.odcs.yaml").is_file()
        assert (base / name / "runtime" / "dq_verify.py").is_file()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k each_atlas_dataset_has_dag_bundle_contract_runtime_files`
Expected: FAIL until all file names are aligned.

- [ ] **Step 3: Write minimal implementation**

```bash
for d in trades instruments portfolios clients advisors funds fund_holdings; do
  test -f "data_products/atlas_elt_demo/datasets/$d/airflow/${d}.dag.yml"
  test -f "data_products/atlas_elt_demo/datasets/$d/bundle/${d}.job.yml"
  test -f "data_products/atlas_elt_demo/datasets/$d/bundle/${d}_dq.job.yml"
  test -f "data_products/atlas_elt_demo/datasets/$d/contract/${d}.odcs.yaml"
  test -f "data_products/atlas_elt_demo/datasets/$d/runtime/dq_verify.py"
done
```

- [ ] **Step 4: Run tests to verify it passes**

Run:
1. `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k "atlas_elt_demo or each_atlas_dataset_has_dag_bundle_contract_runtime_files"`
2. `python -m pytest -q data_products/test_devcontainer_dind_wiring.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add data_products/test_devcontainer_dind_wiring.py data_products/atlas_elt_demo
git commit -m "test: finalize atlas_elt_demo structural parity coverage"
```
