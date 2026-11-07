# Local Dev Test Organization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize local-dev tests into a clear hybrid taxonomy (`local_env` scope + `offline/live` execution split + domain subfolders/markers) while preserving existing verification behavior.

**Architecture:** Keep runtime gates (`dpc-check`, `scripts/verify-with-databricks.sh`) as command entrypoints and restructure pytest assets under `tests/local_env`. Use deterministic collection-contract tests to validate layout and marker behavior. Split oversized mixed modules into focused test files by domain and execution mode.

**Tech Stack:** Python 3.13, pytest, bash, mise tasks, Markdown docs

## Global Constraints

- **Single scope:** local-env only.
- **Primary split by execution mode:** offline vs live.
- **Secondary split by domain:** devcontainer, airflow, auth, tls, etc.
- **Keep operational gates as commands:** do not force `dpc-check` into pytest.
- **Preserve fast default path:** contributors should run deterministic checks first.

---

### Task 1: Scaffold the new local-env test layout and collection contract

**Files:**
- Create: `tests/local_env/offline/tooling/test_local_env_collection_contract.py`
- Modify: `pytest.ini`
- Test: `tests/local_env/offline/tooling/test_local_env_collection_contract.py`

**Interfaces:**
- Consumes: existing repository files and test inventory.
- Produces: canonical collection roots (`tests/local_env/offline`, `tests/local_env/live`) and explicit pytest discovery.

- [ ] **Step 1: Write the failing test**

```python
# tests/local_env/offline/tooling/test_local_env_collection_contract.py
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_pytest_ini_collects_new_local_env_roots() -> None:
    cfg = _read("pytest.ini")
    assert "testpaths =" in cfg
    assert "tests/local_env/offline" in cfg
    assert "tests/local_env/live" in cfg


def test_legacy_data_products_testpaths_removed() -> None:
    cfg = _read("pytest.ini")
    assert "testpaths = data_products" not in cfg
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/local_env/offline/tooling/test_local_env_collection_contract.py -v`  
Expected: FAIL because `pytest.ini` does not yet include the new collection roots.

- [ ] **Step 3: Write minimal implementation**

```ini
# pytest.ini
[pytest]
testpaths =
    tests/local_env/offline
    tests/local_env/live
python_files = test_*.py *_test.py

markers =
    integration: opt-in tests that call live external services
    airflow: tests validating local airflow wiring and DAG contracts
    devcontainer: tests validating local devcontainer and DinD contracts
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/local_env/offline/tooling/test_local_env_collection_contract.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pytest.ini tests/local_env/offline/tooling/test_local_env_collection_contract.py
git commit -m "test: define local_env offline/live pytest collection roots"
```

### Task 2: Move deterministic local-env tests into `offline` domain folders

**Files:**
- Create: `tests/local_env/offline/devcontainer/test_devcontainer_contracts.py`
- Create: `tests/local_env/offline/tls/test_tls_contracts.py`
- Create: `tests/local_env/offline/auth/test_auth_contracts.py`
- Create: `tests/local_env/offline/tooling/test_python_target_contracts.py`
- Modify: remove old `data_products/test_cert_wiring.py`, `data_products/test_tls_enforcement.py`, `data_products/test_devcontainer_python_target.py`
- Test: new files above

**Interfaces:**
- Consumes: assertions currently in deterministic `data_products/test_*.py` files.
- Produces: domain-focused offline tests under `tests/local_env/offline/...`.

- [ ] **Step 1: Write the failing test**

```python
# tests/local_env/offline/tooling/test_offline_layout_presence.py
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_offline_domain_files_exist() -> None:
    required = [
        "tests/local_env/offline/devcontainer/test_devcontainer_contracts.py",
        "tests/local_env/offline/tls/test_tls_contracts.py",
        "tests/local_env/offline/auth/test_auth_contracts.py",
        "tests/local_env/offline/tooling/test_python_target_contracts.py",
    ]
    for rel in required:
        assert (REPO_ROOT / rel).is_file(), rel
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/local_env/offline/tooling/test_offline_layout_presence.py -v`  
Expected: FAIL because new files do not exist yet.

- [ ] **Step 3: Write minimal implementation**

```bash
mkdir -p tests/local_env/offline/{devcontainer,tls,auth,tooling}
git mv data_products/test_cert_wiring.py tests/local_env/offline/tls/test_tls_cert_wiring_contracts.py
git mv data_products/test_tls_enforcement.py tests/local_env/offline/tls/test_tls_enforcement_contracts.py
git mv data_products/test_devcontainer_python_target.py tests/local_env/offline/tooling/test_python_target_contracts.py
```

Then create focused modules:

```python
# tests/local_env/offline/devcontainer/test_devcontainer_contracts.py
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_devcontainer_uses_dind_run_args() -> None:
    cfg = _read(".devcontainer/devcontainer.json")
    assert '"--privileged"' in cfg
    assert '"--init"' in cfg
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/local_env/offline -v`  
Expected: PASS for moved deterministic tests.

- [ ] **Step 5: Commit**

```bash
git add tests/local_env/offline data_products/test_cert_wiring.py data_products/test_tls_enforcement.py data_products/test_devcontainer_python_target.py
git commit -m "test: move deterministic local-env tests into offline domain suites"
```

### Task 3: Split `test_devcontainer_dind_wiring.py` into focused offline modules

**Files:**
- Create: `tests/local_env/offline/devcontainer/test_dind_runtime_contracts.py`
- Create: `tests/local_env/offline/airflow/test_local_airflow_contracts.py`
- Create: `tests/local_env/offline/auth/test_databricks_auth_contracts.py`
- Create: `tests/local_env/offline/tooling/test_docs_and_build_contracts.py`
- Modify: `data_products/test_devcontainer_dind_wiring.py` (deprecate/remove after parity)
- Test: all new split files

**Interfaces:**
- Consumes: existing assertions in `data_products/test_devcontainer_dind_wiring.py`.
- Produces: concern-isolated test modules with stable names for future additions.

- [ ] **Step 1: Write the failing test**

```python
# tests/local_env/offline/tooling/test_dind_split_contract.py
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_dind_split_files_exist() -> None:
    expected = [
        "tests/local_env/offline/devcontainer/test_dind_runtime_contracts.py",
        "tests/local_env/offline/airflow/test_local_airflow_contracts.py",
        "tests/local_env/offline/auth/test_databricks_auth_contracts.py",
        "tests/local_env/offline/tooling/test_docs_and_build_contracts.py",
    ]
    for rel in expected:
        assert (REPO_ROOT / rel).is_file(), rel
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/local_env/offline/tooling/test_dind_split_contract.py -v`  
Expected: FAIL because split files do not yet exist.

- [ ] **Step 3: Write minimal implementation**

Create files and move assertions by concern. Example split:

```python
# tests/local_env/offline/airflow/test_local_airflow_contracts.py
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


@pytest.mark.airflow
def test_compose_uses_metastore_secrets_backend() -> None:
    compose = _read("docker-compose.override.yml")
    assert "airflow.secrets.metastore.MetastoreBackend" in compose
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/local_env/offline -v`  
Expected: PASS with parity to previous deterministic checks.

- [ ] **Step 5: Commit**

```bash
git add tests/local_env/offline data_products/test_devcontainer_dind_wiring.py
git commit -m "test: split dind local-env contracts into focused offline modules"
```

### Task 4: Move live integration tests to `live` and enforce marker contract

**Files:**
- Create: `tests/local_env/live/cli_integration/test_cert_tool_integration.py` (from move)
- Create: `tests/local_env/offline/tooling/test_live_suite_marker_contract.py`
- Modify: remove old `data_products/test_cert_tool_integration.py`
- Test: moved live suite + marker contract

**Interfaces:**
- Consumes: current cert integration tests and `integration` marker convention.
- Produces: explicit live suite path and marker guarantees.

- [ ] **Step 1: Write the failing test**

```python
# tests/local_env/offline/tooling/test_live_suite_marker_contract.py
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_live_suite_file_exists() -> None:
    assert (REPO_ROOT / "tests/local_env/live/cli_integration/test_cert_tool_integration.py").is_file()


def test_live_suite_is_integration_marked() -> None:
    content = (REPO_ROOT / "tests/local_env/live/cli_integration/test_cert_tool_integration.py").read_text(encoding="utf-8")
    assert "pytestmark = [pytest.mark.integration]" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/local_env/offline/tooling/test_live_suite_marker_contract.py -v`  
Expected: FAIL because file is still in `data_products/`.

- [ ] **Step 3: Write minimal implementation**

```bash
mkdir -p tests/local_env/live/cli_integration
git mv data_products/test_cert_tool_integration.py tests/local_env/live/cli_integration/test_cert_tool_integration.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/local_env/offline/tooling/test_live_suite_marker_contract.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/local_env/live/cli_integration/test_cert_tool_integration.py tests/local_env/offline/tooling/test_live_suite_marker_contract.py data_products/test_cert_tool_integration.py
git commit -m "test: isolate live local-env integration suite under tests/local_env/live"
```

### Task 5: Consolidate local Airflow DAG integrity tests into offline airflow suite

**Files:**
- Create: `tests/local_env/offline/airflow/test_dag_integrity.py`
- Modify: remove `.astro/test_dag_integrity_default.py` and `tests/data_products/test_dag_example.py` after parity
- Test: new DAG integrity suite

**Interfaces:**
- Consumes: legacy DAG integrity assertions.
- Produces: single offline airflow integrity entrypoint in local-env taxonomy.

- [ ] **Step 1: Write the failing test**

```python
# tests/local_env/offline/airflow/test_dag_integrity_location_contract.py
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_dag_integrity_suite_exists_under_local_env_offline_airflow() -> None:
    assert (REPO_ROOT / "tests/local_env/offline/airflow/test_dag_integrity.py").is_file()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/local_env/offline/airflow/test_dag_integrity_location_contract.py -v`  
Expected: FAIL before file creation.

- [ ] **Step 3: Write minimal implementation**

```python
# tests/local_env/offline/airflow/test_dag_integrity.py
from __future__ import annotations

from contextlib import contextmanager
import logging
import os

import pytest
from airflow.models import DagBag


@contextmanager
def suppress_logging(namespace: str):
    logger = logging.getLogger(namespace)
    old_value = logger.disabled
    logger.disabled = True
    try:
        yield
    finally:
        logger.disabled = old_value


@pytest.mark.airflow
def test_airflow_dags_import_cleanly() -> None:
    with suppress_logging("airflow"):
        dag_bag = DagBag(include_examples=False)
    assert not dag_bag.import_errors, dag_bag.import_errors
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/local_env/offline/airflow/test_dag_integrity.py -v`  
Expected: PASS in configured local airflow context.

- [ ] **Step 5: Commit**

```bash
git add tests/local_env/offline/airflow/test_dag_integrity.py .astro/test_dag_integrity_default.py tests/data_products/test_dag_example.py
git commit -m "test: unify local airflow dag integrity checks under offline airflow suite"
```

### Task 6: Add an umbrella local-dev verification task and update all repo docs

**Files:**
- Modify: `.mise.toml`
- Modify: `README.md`
- Modify: `GETTING_STARTED.md`
- Modify: `.devcontainer/README.md`
- Modify: any other impacted `.md` files that reference legacy test paths/commands
- Test: task invocation + doc command consistency

**Interfaces:**
- Consumes: new test taxonomy and existing gate commands.
- Produces: one documented local-dev verification flow.

- [ ] **Step 1: Write the failing test**

```python
# tests/local_env/offline/tooling/test_local_dev_verify_task_contract.py
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_mise_has_local_dev_verify_task() -> None:
    mise = _read(".mise.toml")
    assert '[tasks."verify:local-dev"]' in mise
    assert "dpc-check" in mise
    assert "pytest tests/local_env/offline" in mise
    assert "verify-with-databricks.sh" in mise


def test_docs_reference_new_local_env_pytest_paths() -> None:
    docs = [_read("README.md"), _read("GETTING_STARTED.md"), _read(".devcontainer/README.md")]
    joined = "\n".join(docs)
    assert "tests/local_env/offline" in joined
    assert "tests/local_env/live" in joined
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/local_env/offline/tooling/test_local_dev_verify_task_contract.py -v`  
Expected: FAIL before task/doc updates.

- [ ] **Step 3: Write minimal implementation**

```toml
# .mise.toml
[tasks."verify:local-dev"]
description = "Run local-env verification in recommended order"
run = """
dpc-check
pytest tests/local_env/offline
if [ "${CERT_INTEGRATION_TESTS:-0}" = "1" ]; then
  pytest tests/local_env/live -m integration
fi
bash scripts/verify-with-databricks.sh
"""
```

Doc command block to apply consistently:

```bash
dpc-check
pytest tests/local_env/offline
CERT_INTEGRATION_TESTS=1 pytest tests/local_env/live -m integration
bash scripts/verify-with-databricks.sh
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/local_env/offline/tooling/test_local_dev_verify_task_contract.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .mise.toml README.md GETTING_STARTED.md .devcontainer/README.md tests/local_env/offline/tooling/test_local_dev_verify_task_contract.py
git commit -m "docs: publish unified local-dev verification workflow and umbrella task"
```

## Final Verification Gate

- [ ] Run: `pytest tests/local_env/offline -v`
- [ ] Run: `pytest tests/local_env/live -m integration -v` (with `CERT_INTEGRATION_TESTS=1` when live checks are desired)
- [ ] Run: `mise run verify:local-dev`
- [ ] Confirm no doc references remain to deprecated local-env test paths.

