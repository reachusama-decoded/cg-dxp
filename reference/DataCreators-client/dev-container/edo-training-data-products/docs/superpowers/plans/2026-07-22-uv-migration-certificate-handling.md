# UV Migration for Devcontainer + Astro Base-Image Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make uv the default installer for devcontainer setup and Astro Dockerfile package-install stages, while keeping corporate TLS reliability and Python 3.13 SSL strictness compatibility intact.

**Architecture:** Implement a two-phase migration. Phase 1 standardizes uv TLS/index configuration for local devcontainer setup and health checks. Phase 2 replaces pip installs in root `Dockerfile` stage2/stage3 with uv equivalents and validates startup behavior. Keep `sitecustomize.py` unchanged and keep a documented pip rollback path.

**Tech Stack:** Docker/BuildKit, Astronomer Runtime 3.1 base image, Astro CLI, uv, pip, Python 3.13, pytest, shell scripts.

## Post-implementation note (2026-07-23): constraints strategy

- Historical context: initial Dockerfile used Apache `constraints-3.1.3/constraints-3.12.txt`.
- Current runtime (`3.1.8+astro.4`) includes `astronomer-kubernetes-executor` requiring `kubernetes>=35,<36`; Airflow 3.1.3 constraints pin `kubernetes==33.1.0`, causing incompatibility.
- The base image `/etc/pip-constraints.txt` only pins Airflow core/task-sdk/SQLAlchemy and does not constrain provider/data-package backtracking.
- Current stable path is explicit repo pinning in `requirements-pypi.txt`; only evaluate adopting Airflow `constraints-3.1.8` with full compatibility validation.

## Global Constraints

- Keep `sitecustomize.py` behavior unchanged (`VERIFY_X509_STRICT` relaxation stays in place).
- Keep runtime family on Airflow 3.x (`FROM cgprdregistry-aws.capgroup.com/astronomer/astro-runtime:3.1-17-base` unless explicitly changed in a separate decision).
- Keep corp package indexes: `https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/` and `https://cgrepo.capgroup.com/repository/cgpypi/simple/`.
- Keep pip commands available as rollback instructions in docs, but make uv the default path.
- Update tests/docs in the same tasks that change behavior (no behavior change without corresponding assertions/docs).

---

## File Structure

- **Create** `.devcontainer/utils/package-installer-env.sh`  
  Single shared env contract for installer TLS/index settings used by setup/check scripts.
- **Modify** `.devcontainer/utils/setup-python-deps.sh`  
  Consume shared contract and run uv with explicit TLS/index flags.
- **Modify** `.devcontainer/check.sh`  
  Validate uv configuration and package resolution path, plus updated Astro build checks.
- **Modify** `Dockerfile`  
  Replace pip package installs in stage2/stage3 with uv equivalents.
- **Modify** `requirements-pypi.txt`  
  Clarify this file is consumed by uv-driven Dockerfile install path.
- **Modify** `.devcontainer/TROUBLESHOOTING.md` and `.devcontainer/README.md`  
  Document uv-first behavior and exact pip rollback commands.
- **Modify tests** `data_products/test_devcontainer_dind_wiring.py`, `data_products/test_cert_wiring.py`  
  Assert uv-specific wiring and rollback documentation.

### Task 1: Shared uv/pip installer contract for devcontainer setup

**Files:**
- Create: `.devcontainer/utils/package-installer-env.sh`
- Modify: `.devcontainer/utils/setup-python-deps.sh`
- Modify: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: `/cacert.pem`, corp indexes already used in repo.
- Produces:
  - `export UV_NATIVE_TLS=1`
  - `export UV_INDEX_URL=https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/`
  - `export UV_EXTRA_INDEX_URL=https://cgrepo.capgroup.com/repository/cgpypi/simple/`
  - `export PIP_CERT=/cacert.pem`

- [ ] **Step 1: Write the failing test**

```python
def test_setup_python_deps_sources_shared_installer_env() -> None:
    script = _read(".devcontainer/utils/setup-python-deps.sh")
    assert ".devcontainer/utils/package-installer-env.sh" in script


def test_shared_installer_env_defines_uv_contract() -> None:
    env_script = _read(".devcontainer/utils/package-installer-env.sh")
    assert "UV_NATIVE_TLS" in env_script
    assert "UV_INDEX_URL=https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/" in env_script
    assert "UV_EXTRA_INDEX_URL=https://cgrepo.capgroup.com/repository/cgpypi/simple/" in env_script
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest data_products/test_devcontainer_dind_wiring.py::test_setup_python_deps_sources_shared_installer_env data_products/test_devcontainer_dind_wiring.py::test_shared_installer_env_defines_uv_contract -v`  
Expected: FAIL because `package-installer-env.sh` does not exist and cannot be sourced yet.

- [ ] **Step 3: Write minimal implementation**

```sh
# .devcontainer/utils/package-installer-env.sh
#!/bin/sh
set -eu

export PIP_CERT="${PIP_CERT:-/cacert.pem}"
export UV_NATIVE_TLS="${UV_NATIVE_TLS:-1}"
export UV_INDEX_URL="${UV_INDEX_URL:-https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/}"
export UV_EXTRA_INDEX_URL="${UV_EXTRA_INDEX_URL:-https://cgrepo.capgroup.com/repository/cgpypi/simple/}"
```

```sh
# .devcontainer/utils/setup-python-deps.sh (top of file)
. .devcontainer/utils/package-installer-env.sh

uv pip install --system --quiet --native-tls \
  --index-url "$UV_INDEX_URL" \
  --extra-index-url "$UV_EXTRA_INDEX_URL" \
  -r .devcontainer/requirements.txt
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest data_products/test_devcontainer_dind_wiring.py::test_setup_python_deps_sources_shared_installer_env data_products/test_devcontainer_dind_wiring.py::test_shared_installer_env_defines_uv_contract -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .devcontainer/utils/package-installer-env.sh .devcontainer/utils/setup-python-deps.sh data_products/test_devcontainer_dind_wiring.py
git commit -m "chore: add shared uv installer env contract"
```

### Task 2: Devcontainer TLS/health-check hardening for uv

**Files:**
- Modify: `.devcontainer/check.sh`
- Modify: `.devcontainer/Dockerfile`
- Modify: `.devcontainer/devcontainer.json`
- Modify: `data_products/test_cert_wiring.py`

**Interfaces:**
- Consumes: Task 1 env contract and current `sitecustomize.py`.
- Produces:
  - uv verification check in `dpc-check`
  - explicit uv TLS env defaults in image/runtime config

- [ ] **Step 1: Write the failing test**

```python
def test_devcontainer_dockerfile_exports_uv_tls_env_defaults() -> None:
    dockerfile = _read(DEVCONTAINER_DOCKERFILE)
    assert "UV_NATIVE_TLS=1" in dockerfile
    assert "UV_INDEX_URL=https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/" in dockerfile


def test_check_script_validates_uv_resolution() -> None:
    script = _read(".devcontainer/check.sh")
    assert "uv can resolve a package (corp index)" in script
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest data_products/test_cert_wiring.py::test_devcontainer_dockerfile_exports_uv_tls_env_defaults data_products/test_cert_wiring.py::test_check_script_validates_uv_resolution -v`  
Expected: FAIL because uv env defaults/check assertion are not present yet.

- [ ] **Step 3: Write minimal implementation**

```dockerfile
# .devcontainer/Dockerfile (ENV block)
ENV SSL_CERT_FILE=/cacert.pem \
    REQUESTS_CA_BUNDLE=/cacert.pem \
    PIP_CERT=/cacert.pem \
    UV_NATIVE_TLS=1 \
    UV_INDEX_URL=https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/ \
    UV_EXTRA_INDEX_URL=https://cgrepo.capgroup.com/repository/cgpypi/simple/
```

```json
// .devcontainer/devcontainer.json (containerEnv)
"UV_NATIVE_TLS": "1",
"UV_INDEX_URL": "https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/",
"UV_EXTRA_INDEX_URL": "https://cgrepo.capgroup.com/repository/cgpypi/simple/"
```

```sh
# .devcontainer/check.sh (TLS section)
check "UV native TLS enabled" bash -c '[ "${UV_NATIVE_TLS:-}" = 1 ]'
soft_check "uv can resolve a package (corp index)" \
  uv pip install --system --dry-run --native-tls \
  --index-url "${UV_INDEX_URL:-https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/}" \
  --extra-index-url "${UV_EXTRA_INDEX_URL:-https://cgrepo.capgroup.com/repository/cgpypi/simple/}" \
  requests
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest data_products/test_cert_wiring.py::test_devcontainer_dockerfile_exports_uv_tls_env_defaults data_products/test_cert_wiring.py::test_check_script_validates_uv_resolution -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .devcontainer/Dockerfile .devcontainer/devcontainer.json .devcontainer/check.sh data_products/test_cert_wiring.py
git commit -m "chore: harden devcontainer uv tls validation"
```

### Task 3: Switch Astro base-image package install stages to uv

**Files:**
- Modify: `Dockerfile`
- Modify: `requirements-pypi.txt`
- Modify: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: root Dockerfile stage2 (`requirements-pypi.txt` + constraints) and stage3 cosmos venv install.
- Produces:
  - stage2 uses `uv pip install --system --native-tls ... -r requirements.txt -c /tmp/constraints.txt`
  - stage3 uses `uv pip install --python /home/astro/.venv/cosmos/bin/python --native-tls ... -r requirements-venv-cosmos.txt`

- [ ] **Step 1: Write the failing test**

```python
def test_root_dockerfile_uses_uv_for_stage2_and_stage3_python_installs() -> None:
    dockerfile = _read("Dockerfile")
    assert "uv pip install --system --native-tls" in dockerfile
    assert "uv pip install --python /home/astro/.venv/cosmos/bin/python --native-tls" in dockerfile


def test_requirements_pypi_header_mentions_uv_default() -> None:
    req = _read("requirements-pypi.txt")
    assert "Installer: uv" in req
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest data_products/test_devcontainer_dind_wiring.py::test_root_dockerfile_uses_uv_for_stage2_and_stage3_python_installs data_products/test_devcontainer_dind_wiring.py::test_requirements_pypi_header_mentions_uv_default -v`  
Expected: FAIL because current `Dockerfile` stage2/stage3 still use pip.

- [ ] **Step 3: Write minimal implementation**

```dockerfile
# Dockerfile stage2 install
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv pip install --system --native-tls \
    --index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple \
    --extra-index-url https://cgrepo.capgroup.com/repository/cgpypi/simple \
    -r requirements.txt -c /tmp/constraints.txt
```

```dockerfile
# Dockerfile stage3 cosmos venv install
RUN --mount=type=cache,target=/home/astro/.cache/uv,sharing=locked \
    mkdir -p /home/astro/.venv && \
    python3 -m venv /home/astro/.venv/cosmos && \
    uv pip install --python /home/astro/.venv/cosmos/bin/python --native-tls \
      --index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple \
      --extra-index-url https://cgrepo.capgroup.com/repository/cgpypi/simple \
      -q -r requirements-venv-cosmos.txt
```

```text
# requirements-pypi.txt
# Consumed by root Dockerfile stage2 install.
# Installer: uv (fallback: pip via troubleshooting rollback procedure).
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest data_products/test_devcontainer_dind_wiring.py::test_root_dockerfile_uses_uv_for_stage2_and_stage3_python_installs data_products/test_devcontainer_dind_wiring.py::test_requirements_pypi_header_mentions_uv_default -v`  
Expected: PASS.

- [ ] **Step 5: Validate Astro startup path**

Run: `astro dev start --wait 3m`  
Expected: Airflow starts and no TLS `UnknownIssuer` appears during image dependency install.

- [ ] **Step 6: Commit**

```bash
git add Dockerfile requirements-pypi.txt data_products/test_devcontainer_dind_wiring.py
git commit -m "feat: migrate astro dockerfile package installs to uv"
```

### Task 4: Documentation + rollback drill

**Files:**
- Modify: `.devcontainer/TROUBLESHOOTING.md`
- Modify: `.devcontainer/README.md`
- Modify: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: Task 1-3 uv behavior.
- Produces:
  - explicit rollback instructions from uv back to pip install commands
  - test guard to ensure rollback docs stay present

- [ ] **Step 1: Write the failing test**

```python
def test_troubleshooting_documents_uv_to_pip_rollback_steps() -> None:
    doc = _read(".devcontainer/TROUBLESHOOTING.md")
    assert "UV rollback (emergency)" in doc
    assert "Replace uv install commands in `Dockerfile` stage2/stage3 with equivalent pip commands." in doc
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest data_products/test_devcontainer_dind_wiring.py::test_troubleshooting_documents_uv_to_pip_rollback_steps -v`  
Expected: FAIL because rollback section is not yet present in exact form.

- [ ] **Step 3: Write minimal implementation**

```md
## UV rollback (emergency)

1. Replace uv install commands in `Dockerfile` stage2/stage3 with equivalent pip commands.
2. Rebuild/restart with `astro dev start --wait 3m`.
3. Confirm startup succeeds and capture logs for comparison.
```

```md
Update `.devcontainer/README.md` Python install guidance to show uv-first examples and state pip fallback availability.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest data_products/test_devcontainer_dind_wiring.py::test_troubleshooting_documents_uv_to_pip_rollback_steps -v`  
Expected: PASS.

- [ ] **Step 5: Run final targeted validation set**

Run: `pytest data_products/test_devcontainer_dind_wiring.py data_products/test_cert_wiring.py -v`  
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add .devcontainer/TROUBLESHOOTING.md .devcontainer/README.md data_products/test_devcontainer_dind_wiring.py
git commit -m "docs: add uv migration rollback runbook"
```

## Self-Review

1. **Spec coverage:** All approved spec requirements are mapped: phased both-surface migration, base-image (not ONBUILD) scope, fixed corp index URLs, unchanged `sitecustomize.py`, rollback path, and verification gates.
2. **Placeholder scan:** No placeholders remain. Each code-changing step includes concrete code and concrete commands.
3. **Type consistency:** Shared env contract keys are consistent across tasks (`UV_NATIVE_TLS`, `UV_INDEX_URL`, `UV_EXTRA_INDEX_URL`, `PIP_CERT`) and Dockerfile uv command signatures are identical between test assertions and implementation steps.
