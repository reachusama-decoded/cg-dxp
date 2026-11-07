# Devcontainer Setup Deprecations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove deprecated host-path and legacy PAT setup task surfaces while preserving OAuth-first + DinD behavior and parity with `dpc-academy`.

**Architecture:** We remove runtime host-path detection and PAT-era `mise` task entrypoints, then anchor Astro mounts to repo-relative paths. We keep PAT as an explicit fallback only through `.devcontainer/setup-databricks-dbt.sh --pat`, not through default setup automation. We lock behavior with regression tests and docs updates so setup remains clear and non-contradictory.

**Tech Stack:** mise tasks, Devcontainer config/scripts, Docker Compose override, pytest, Markdown docs.

## Global Constraints

- Preserve OAuth-first default setup behavior (`mise run setup:databricks` and `.devcontainer/setup-databricks-dbt.sh`).
- Keep PAT support available only via explicit `--pat` script path.
- Remove `setup:host-path`, `setup:normalize-env`, and `setup:databricks` from `.mise.toml`.
- Remove `HOST_WORKSPACE_PATH` usage from runtime setup and compose mount wiring.
- Keep DinD health/startup behavior unchanged unless tests prove breakage.
- Validate in-container with `mise run setup`, `pytest`, `dpc-check`, and `astro dev start` mount sanity.

---

### Task 1: Lock the new contracts with failing tests first

**Files:**
- Modify: `data_products/test_devcontainer_dind_wiring.py`
- Test: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: Existing helper functions in `data_products/test_devcontainer_dind_wiring.py` (`_read`, `_load_json_permissive`).
- Produces: New/updated tests asserting:
  - no `setup:host-path`, `setup:normalize-env`, `setup:databricks` in `.mise.toml`
  - `docker-compose.override.yml` uses repo-relative `./data_products` mount
  - no `HOST_WORKSPACE_PATH` usage in tracked setup surfaces

- [ ] **Step 1: Write the failing tests**

```python
def test_mise_excludes_deprecated_setup_tasks() -> None:
    mise = _read(".mise.toml")
    assert '[tasks."setup:host-path"]' not in mise
    assert '[tasks."setup:normalize-env"]' not in mise
    assert '[tasks."setup:databricks"]' not in mise


def test_compose_uses_repo_relative_dag_mount() -> None:
    override = _read("docker-compose.override.yml")
    assert "./data_products:/usr/local/airflow/dags" in override
    assert "HOST_WORKSPACE_PATH" not in override
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest -q data_products/test_devcontainer_dind_wiring.py -k "deprecated_setup_tasks or repo_relative_dag_mount"`
Expected: FAIL because current code still contains deprecated task blocks and/or host-path references.

- [ ] **Step 3: Commit test-only change**

```bash
git add data_products/test_devcontainer_dind_wiring.py
git commit -m "test: codify setup deprecation contracts"
```

### Task 2: Remove host-path runtime detection and legacy PAT task entries

**Files:**
- Modify: `.mise.toml`
- Modify: `docker-compose.override.yml`
- Delete: `.devcontainer/utils/set-host-path.sh`
- Test: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: Task contract from Task 1.
- Produces:
  - simplified `tasks.setup` dependency list without deprecated task names
  - compose mount contract using `./data_products`
  - no tracked `set-host-path` utility script

- [ ] **Step 1: Remove deprecated task blocks from `.mise.toml`**

```toml
[tasks.setup]
description = "Full devcontainer setup"
depends = ["setup:env-file", "setup:mise", "setup:gh-auth", "setup:python-deps"]
```

And remove these full task sections:

```toml
[tasks."setup:normalize-env"]
[tasks."setup:host-path"]
[tasks."setup:databricks"]
```

- [ ] **Step 2: Update compose mount to relative path**

```yaml
x-airflow-common: &airflow-common
  volumes:
    - ./data_products:/usr/local/airflow/dags
    - $HOME/.aws:/home/astro/.aws
```

- [ ] **Step 3: Delete obsolete host-path script**

```bash
git rm .devcontainer/utils/set-host-path.sh
```

- [ ] **Step 4: Run targeted tests**

Run: `pytest -q data_products/test_devcontainer_dind_wiring.py -k "deprecated_setup_tasks or repo_relative_dag_mount"`
Expected: PASS.

- [ ] **Step 5: Commit implementation change**

```bash
git add .mise.toml docker-compose.override.yml data_products/test_devcontainer_dind_wiring.py
git commit -m "refactor: remove host-path and legacy PAT setup tasks"
```

### Task 3: Align docs and startup guidance to the new setup surface

**Files:**
- Modify: `.devcontainer/README.md`
- Modify: `.devcontainer/TROUBLESHOOTING.md`
- Modify: `README.md` (only if it references removed task behavior)
- Test: Doc/reference grep checks

**Interfaces:**
- Consumes: Final task names and compose behavior from Task 2.
- Produces: Documentation that reflects OAuth-first defaults without host-path detection instructions.

- [ ] **Step 1: Update setup lifecycle text in `.devcontainer/README.md`**

Replace host-path-detection wording with the new flow:

```md
On container startup, the `postCreateCommand` performs the following:
1. Creates the git-ignored `.devcontainer/.env` from `.devcontainer/utils/.env.example` when needed
2. Configures mise, GitHub authentication, and Python dependencies
3. OAuth setup remains explicit via `mise run setup:databricks` (renamed from `setup:databricks-oauth`)
```

- [ ] **Step 2: Remove troubleshooting references to `HOST_WORKSPACE_PATH` or set-host-path behavior**

Ensure troubleshooting points users to repo-root `astro dev start` contract and OAuth command instead of removed host-path internals.

- [ ] **Step 3: Run reference checks**

Run: `rg -n "setup:host-path|setup:normalize-env|setup:databricks|HOST_WORKSPACE_PATH|set-host-path" .`
Expected: no matches in active docs/config (except historical migration docs if intentionally retained).

- [ ] **Step 4: Commit docs alignment**

```bash
git add .devcontainer/README.md .devcontainer/TROUBLESHOOTING.md README.md
git commit -m "docs: align setup guidance with deprecated task removals"
```

### Task 4: End-to-end verification and final integration commit

**Files:**
- Verify only: runtime behavior in devcontainer
- Modify if needed: minimal follow-up fixes from failing checks

**Interfaces:**
- Consumes: Completed Task 1–3 changes.
- Produces: Verified working state for setup + health + Astro local run.

- [ ] **Step 1: Rebuild/reopen devcontainer and run setup**

Run:

```bash
devcontainer up --workspace-folder . --remove-existing-container
devcontainer exec --workspace-folder . bash -lc 'cd /workspaces/edo-training-data-products && mise run setup'
```

Expected: setup completes without referencing removed tasks.

- [ ] **Step 2: Run full automated checks in-container**

Run:

```bash
devcontainer exec --workspace-folder . bash -lc 'cd /workspaces/edo-training-data-products && pytest -q && dpc-check'
```

Expected: pytest passes and `dpc-check` reports `FAIL: 0` (auth WARNs are acceptable before login).

- [ ] **Step 3: Validate Astro mount sanity**

Run:

```bash
devcontainer exec --workspace-folder . bash -lc 'cd /workspaces/edo-training-data-products && astro dev start --wait 180 && astro dev stop'
```

Expected: Airflow services start and stop successfully; DAG mount resolves with `./data_products`.

- [ ] **Step 4: Final commit and push**

```bash
git add -A
git commit -m "chore: deprecate legacy setup surfaces for DinD parity"
git push
```

## Self-Review

- **Spec coverage:** All approved spec decisions are mapped:
  - host-path removal (Task 2)
  - legacy PAT task surface removal (Task 2)
  - tests/docs/verification gates (Task 1, 3, 4)
- **Placeholder scan:** No TBD/TODO placeholders remain; each task has explicit files, commands, and expected outcomes.
- **Type/contract consistency:** Task names, file paths, and task identifiers are consistent across all tasks (`setup:host-path`, `setup:normalize-env`, `setup:databricks`, `HOST_WORKSPACE_PATH`).
