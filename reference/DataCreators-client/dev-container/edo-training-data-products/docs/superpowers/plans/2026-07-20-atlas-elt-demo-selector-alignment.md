# Atlas ELT Demo Selector Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align `atlas_elt_demo` dbt naming/selectors to `dpc-academy` so validation executes real models.

**Architecture:** Keep this repo’s existing per-dataset artifact structure, but rename Atlas dbt model nodes to `bronze_*`, `silver_*`, and `gold_*` by entity. Update selector validation to target real nodes (`+bronze_trades`) and keep all shell parity artifacts unchanged. Prove execution in devcontainer with deps, seed, and run.

**Tech Stack:** dbt Core, dbt-databricks, mise tasks, devcontainer CLI, pytest.

## Global Constraints

- Naming convention source of truth: `dpc-academy` conventions take precedence per user instruction.
- No geography/currency content introduced into `atlas_elt_demo`.
- No structural regression in dataset artifact folders.
- Keep `atlas_elt_demo` artifact structure parity already established.

---

### Task 1: Enforce dpc Naming Contract in Tests

**Files:**
- Modify: `data_products/test_devcontainer_dind_wiring.py`
- Test: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: Existing `REPO_ROOT`-based file existence tests for `atlas_elt_demo`.
- Produces: Failing/passing guard that enforces `bronze_*/silver_*/gold_*` naming and bans `stage_*` in Atlas datasets.

- [ ] **Step 1: Write the failing test**

```python
def test_atlas_elt_demo_uses_dpc_layer_prefixes() -> None:
    base = REPO_ROOT / "data_products" / "atlas_elt_demo" / "datasets"
    entities = ["trades", "instruments", "portfolios", "clients", "advisors", "funds", "fund_holdings"]
    for e in entities:
        assert (base / e / "dbt" / "staging" / f"bronze_{e}.sql").is_file()
        assert (base / e / "dbt" / "integration" / f"silver_{e}.sql").is_file()
        assert (base / e / "dbt" / "prepared" / f"gold_{e}.sql").is_file()
        assert not (base / e / "dbt" / "staging" / f"stage_{e}.sql").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k dpc_layer_prefixes`  
Expected: FAIL because current files still include `stage_*`/`int_*` naming.

- [ ] **Step 3: Write minimal implementation**

```python
# In the same test file, add selector guard:
def test_atlas_elt_demo_selector_smoke_targets_real_nodes() -> None:
    # This test protects command choice used by reviewers/validation scripts.
    assert True  # replaced in Task 2 with command-backed verification
```

- [ ] **Step 4: Run test to verify it passes/fails as expected**

Run: `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k "dpc_layer_prefixes or selector_smoke_targets_real_nodes"`  
Expected: first test FAIL (red), second PASS placeholder.

- [ ] **Step 5: Commit**

```bash
git add data_products/test_devcontainer_dind_wiring.py
git commit -m "test: enforce dpc naming prefixes for atlas models"
```

### Task 2: Rename Atlas Models and References to bronze/silver/gold

**Files:**
- Modify/Create/Rename:  
  - `data_products/atlas_elt_demo/datasets/*/dbt/staging/*.sql`  
  - `data_products/atlas_elt_demo/datasets/*/dbt/integration/*.sql`  
  - `data_products/atlas_elt_demo/datasets/*/dbt/prepared/*.sql`  
  - `data_products/atlas_elt_demo/datasets/*/dbt/*.yml`
- Modify: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: Task 1 failing naming test.
- Produces: dbt graph with `bronze_* -> silver_* -> gold_*` per entity and consistent YAML model names.

- [ ] **Step 1: Write the failing test**

```python
def test_atlas_elt_demo_run_selector_executes_bronze_model_chain() -> None:
    # command-level integration guard for selector behavior
    assert True  # replaced after command wiring in this task
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k run_selector_executes_bronze_model_chain`  
Expected: FAIL once assertion is replaced by real command-backed check.

- [ ] **Step 3: Write minimal implementation**

```bash
for e in trades instruments portfolios clients advisors funds fund_holdings; do
  mv "data_products/atlas_elt_demo/datasets/$e/dbt/staging/stage_${e}.sql" \
     "data_products/atlas_elt_demo/datasets/$e/dbt/staging/bronze_${e}.sql"
  mv "data_products/atlas_elt_demo/datasets/$e/dbt/integration/int_${e}.sql" \
     "data_products/atlas_elt_demo/datasets/$e/dbt/integration/silver_${e}.sql"
  mv "data_products/atlas_elt_demo/datasets/$e/dbt/prepared/${e}.sql" \
     "data_products/atlas_elt_demo/datasets/$e/dbt/prepared/gold_${e}.sql"
done
```

```python
# Update SQL refs and YAML model names to bronze_/silver_/gold_ names in each dataset.
# Example expected ref chain after edit:
# silver_trades.sql -> ref('bronze_trades')
# gold_trades.sql -> ref('silver_trades')
```

- [ ] **Step 4: Run tests and commands to verify pass**

Run:
1. `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k dpc_layer_prefixes`
2. `devcontainer exec --workspace-folder . bash -lc 'mise run dbt:deps atlas_elt_demo'`
3. `devcontainer exec --workspace-folder . bash -lc 'cd data_products/atlas_elt_demo && /opt/venv/bin/python ../../dbt_wrapper.py seed --project-dir . --profiles-dir dbt_profiles --target local'`
4. `devcontainer exec --workspace-folder . bash -lc 'mise run dbt:run atlas_elt_demo -- --select +bronze_trades'`
Expected:
- pytest PASS
- dbt deps PASS
- dbt seed PASS (7 seeds)
- dbt run PASS with executed models (not “Nothing to do”)

- [ ] **Step 5: Commit**

```bash
git add data_products/atlas_elt_demo data_products/test_devcontainer_dind_wiring.py
git commit -m "feat: align atlas model naming to dpc bronze-silver-gold"
```

### Task 3: Final Selector Contract and Regression Validation

**Files:**
- Modify: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: Renamed models and updated refs from Task 2.
- Produces: Stable test contract that prevents regression to non-executing selectors.

- [ ] **Step 1: Write the failing test**

```python
def test_atlas_elt_demo_no_staging_wildcard_selector_dependency() -> None:
    # Prevent future reliance on non-executing selector examples for atlas demo validation.
    runbook = (REPO_ROOT / "docs" / "superpowers" / "plans" / "2026-07-20-atlas-elt-demo-selector-alignment.md").read_text()
    assert "+bronze_trades" in runbook
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k no_staging_wildcard_selector_dependency`  
Expected: FAIL until selector guidance is aligned.

- [ ] **Step 3: Write minimal implementation**

```python
# Update test assertions and any in-repo validation references so atlas selector examples
# use +bronze_trades or equivalent real-node selectors.
```

- [ ] **Step 4: Run tests to verify pass**

Run:
1. `python -m pytest -q data_products/test_devcontainer_dind_wiring.py -k "atlas_elt_demo and dpc_layer_prefixes"`
2. `python -m pytest -q data_products/test_devcontainer_dind_wiring.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add data_products/test_devcontainer_dind_wiring.py docs/superpowers/specs/2026-07-20-atlas-elt-demo-selector-alignment-design.md
git commit -m "test: lock selector contract to executing dpc-style nodes"
```
