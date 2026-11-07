# Training Challenges + Atlas Capstone Port — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port the `preflight` training challenges (00–03) and the Atlas capstone (04) into the `edo-training-data-products` devcontainer so trainees run every challenge with one command through the repo's existing dbt / Databricks / Astro tooling.

**Architecture:** A new `challenges/` home holds each challenge's guide + `verify`/`reset`, driven by four new `challenge:*` mise tasks and a first-class `tests/challenges/{offline,live}` pytest suite (offline = hermetic, in CI; live = `CERT_INTEGRATION_TESTS=1`). Challenges 03 and 04 place their real artifacts natively under `data_products/` (`portfolio_analytics`, `atlas_elt`); the capstone becomes a real paved-path product and the placeholder `atlas_elt_demo` is retired. Trainees author only dbt models (and, for 03, the DAG) from `select 1 as placeholder` stubs; the reference solution is retained per challenge as the answer key + live-verify baseline.

**Tech Stack:** mise tasks (TOML `usage`), pytest (`pytest.ini` markers `integration`/`airflow`), dbt-databricks 1.11 via `dbt_wrapper.py`, Databricks Asset Bundles, Airflow 3.x + astronomer-cosmos 1.15 + apache-airflow-providers-databricks 7.7.4, Astronomer (Astro) local runtime, ODCS contracts (spec files only).

## Global Constraints

- **Branch:** work on `feature/improvements` (current); commit after every task; push after each commit.
- **Design source of truth:** `docs/superpowers/specs/2026-07-27-training-challenges-and-atlas-capstone-design.md`. Do not re-decide resolved items.
- **Native flow must stay green:** `mise run verify:local-dev` and `pre-commit run --all-files` pass identically before and after (parity check).
- **Offline tests hermetic:** no Databricks/Astro; live tests marked `@pytest.mark.integration`, gated by `CERT_INTEGRATION_TESTS=1`, and pass on stubs offline / build red until authored.
- **Challenge products keep real domain names:** `portfolio_analytics`, `atlas_elt` — never challenge-number-prefixed (the name propagates into dbt project, bundle, and Databricks job names).
- **Contract publish is instructor-only:** never add `mise run contract:migrate` (Flyway) to any challenge step, verify, or CI. Contracts ship as `contract/<d>.odcs.yaml` spec files only.
- **Stub convention:** trainee-authored model bodies (and 03's DAG task wiring) become `select 1 as placeholder` / `# TODO`; scaffolding, `schema.yml` tests, macros, seeds, snapshots ship complete; `profiles.yml` is swapped for the shared env-contract profile, not stubbed.
- **dbt target/catalog:** `--target local`, app catalog `training_dev`, schema `training_<user>` (from `DATABRICKS_SCHEMA`); dbt-databricks 1.11.
- **Source repo (read-only reference):** `preflight/` (a sibling checkout at `../preflight` relative to repo root, i.e. `/Users/gqp/Downloads/repos/emu/preflight`). Copy artifacts from there; it is not modified.

---

## File Structure

**Create:**
- `challenges/README.md` — 00→04 path, the one prerequisite, and the challenge↔product map.
- `challenges/00-environment-check/` — `README.md` (guide), `verify.sh`.
- `challenges/01-docker-intro/` — guide, `Dockerfile`, `app/`, `verify.sh`.
- `challenges/02-dbt-pipeline/` — guide, `dbt/` (stub working tree), `dbt_profiles/profiles.yml`, `solution/`, `stubs/`, `verify.sh`.
- `challenges/03-airflow-orchestration/` — guide + `verify.sh` + `solution/` (the DAG/dbt live under `data_products/portfolio_analytics/`).
- `challenges/04-atlas-capstone/` — guide + `verify.sh` + `reset` wiring + `solution/` (the product lives under `data_products/atlas_elt/`).
- `tests/challenges/offline/` — hermetic pytest suite (structure/parse/import).
- `tests/challenges/live/` — `@pytest.mark.integration` pytest suite (build/deploy/trigger).
- `tests/challenges/__init__.py`, `tests/challenges/conftest.py` — shared helpers (repo root, challenge discovery).
- `data_products/portfolio_analytics/` — challenge 03 native placement (Cosmos DAG + co-located dbt project).
- `data_products/atlas_elt/` — capstone paved-path product (datasets, contracts, bundle jobs, DQ, blueprint DAGs).

**Modify:**
- `.mise.toml` — add `challenge:verify`, `challenge:verify-all`, `challenge:dbt`, `challenge:reset`.
- `pytest.ini` — add `tests/challenges/offline` + `tests/challenges/live` to `testpaths`.
- `.sqlfluffignore` — ignore `challenges/` working+solution SQL; `.dbtignore` — ignore `challenges/**/solution/**`.
- `docker-compose.override.yml:34` — default `AIRFLOW_VAR_DATA_PRODUCT_NAME` → `atlas_elt`.
- `.devcontainer/README.md:252` — repoint the `clients_job` example to an `atlas_elt` dataset.
- `data_products/test_atlas_local_runtime_contract.py`, `tests/local_env/offline/tooling/test_devcontainer_dind_wiring.py` — repoint `atlas_elt_demo` → `atlas_elt`.
- `GETTING_STARTED.md` — add an "Optional: Training Challenges" pointer.

**Delete:**
- `data_products/atlas_elt_demo/` (Phase 2, last task).

---

# Phase 0 — Foundation (challenge harness)

## Task 1: `challenges/` home + discoverability

**Files:**
- Create: `challenges/README.md`
- Modify: `GETTING_STARTED.md` (add pointer after the "## 6. Start Astronomer" section)
- Test: `tests/challenges/offline/test_home.py`, `tests/challenges/__init__.py`, `tests/challenges/conftest.py`

**Interfaces:**
- Produces: `conftest.py` helper `repo_root() -> pathlib.Path` and `challenge_dirs() -> list[Path]` (sorted `challenges/NN-*`), consumed by all later offline tests.

- [ ] **Step 1: Write the failing test**

Create `tests/challenges/__init__.py` (empty) and `tests/challenges/conftest.py`:

```python
from __future__ import annotations
import re
from pathlib import Path
import pytest

def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]

def challenge_dirs() -> list[Path]:
    root = repo_root() / "challenges"
    return sorted(p for p in root.glob("*") if p.is_dir() and re.match(r"\d\d-", p.name))

@pytest.fixture
def root() -> Path:
    return repo_root()
```

Create `tests/challenges/offline/__init__.py` (empty) and `tests/challenges/offline/test_home.py`:

```python
from pathlib import Path
from tests.challenges.conftest import repo_root, challenge_dirs

def test_challenges_readme_lists_full_path() -> None:
    readme = (repo_root() / "challenges" / "README.md").read_text()
    for token in ("00-environment-check", "01-docker-intro", "02-dbt-pipeline",
                  "03-airflow-orchestration", "04-atlas-capstone"):
        assert token in readme, f"challenges/README.md must mention {token}"

def test_five_challenge_dirs_present() -> None:
    names = [p.name for p in challenge_dirs()]
    assert names == ["00-environment-check", "01-docker-intro", "02-dbt-pipeline",
                     "03-airflow-orchestration", "04-atlas-capstone"], names

def test_getting_started_points_to_challenges() -> None:
    gs = (repo_root() / "GETTING_STARTED.md").read_text()
    assert "challenges/README.md" in gs
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/challenges/offline/test_home.py -v`
Expected: FAIL — `challenges/README.md` does not exist (FileNotFoundError) and empty challenge dir list.

- [ ] **Step 3: Create `challenges/README.md`**

```markdown
# Training Challenges

A guided path from a working devcontainer to a real CG data product. Do them in order.

**Prerequisite:** open this repo in its devcontainer and run `mise run setup:databricks`
once (mints your Databricks auth for every challenge — no per-challenge setup).

| # | Folder | You learn | You author |
|---|--------|-----------|------------|
| 00 | `00-environment-check` | your toolchain is ready | (nothing — run the check) |
| 01 | `01-docker-intro` | build & run a container on the devcontainer's Docker | (nothing — run the image) |
| 02 | `02-dbt-pipeline` | a `source → staging → marts` dbt pipeline on Databricks | the dbt model bodies |
| 03 | `03-airflow-orchestration` | orchestrate that pipeline with Airflow + Cosmos | the DAG (`data_products/portfolio_analytics`) |
| 04 | `04-atlas-capstone` | build a real paved-path data product | the source→domain→consumer dbt models (`data_products/atlas_elt`) |

**Run any challenge:** `mise run challenge:verify <NN>` (e.g. `mise run challenge:verify 02`).
**Start over:** `mise run challenge:reset <NN>` re-blanks the models you author back to stubs.

Challenges 03 and 04 keep their real artifacts under `data_products/` with real product
names (`portfolio_analytics`, `atlas_elt`); each such folder's `README.md` header points
back to its `challenges/NN-*` guide.
```

- [ ] **Step 4: Add the `GETTING_STARTED.md` pointer**

Append after the "## 6. Start Astronomer (Local Airflow)" section:

```markdown

## 7. Optional: Training Challenges

New to the stack? Work `challenges/README.md` (00→04) — a guided path from a green
devcontainer to a real paved-path data product. Run one with `mise run challenge:verify <NN>`.
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/challenges/offline/test_home.py -v`
Expected: PASS (3 tests). `challenge_dirs()` is still empty until later tasks — so relax `test_five_challenge_dirs_present` to `assert names == names` is **not** allowed; instead mark it `@pytest.mark.xfail(reason="dirs created in Tasks 5–9", strict=False)` now and remove the xfail in Task 9.

- [ ] **Step 6: Commit**

```bash
git add challenges/README.md GETTING_STARTED.md tests/challenges
git commit -m "feat(challenges): add challenges home, discoverability, and offline test scaffold"
git push
```

## Task 2: `challenge:*` mise tasks

**Files:**
- Modify: `.mise.toml` (append four `[tasks."challenge:*"]` blocks)
- Test: `tests/challenges/offline/test_mise_tasks.py`

**Interfaces:**
- Produces: CLI `mise run challenge:verify <NN>`, `challenge:verify-all`, `challenge:dbt <NN> -- <args>`, `challenge:reset <NN>`. `verify` runs `challenges/<NN>-*/verify.sh`; `reset` restores working files from `challenges/<NN>-*/stubs/`; `dbt` runs dbt in the challenge's `dbt/` dir with `--profiles-dir dbt_profiles`.

- [ ] **Step 1: Write the failing test**

Create `tests/challenges/offline/test_mise_tasks.py`:

```python
import subprocess
from tests.challenges.conftest import repo_root

def _mise_tasks() -> str:
    return subprocess.run(["mise", "tasks", "--no-header"], cwd=repo_root(),
                          capture_output=True, text=True, check=True).stdout

def test_challenge_tasks_register() -> None:
    out = _mise_tasks()
    for task in ("challenge:verify", "challenge:verify-all", "challenge:dbt", "challenge:reset"):
        assert task in out, f"{task} must be registered in .mise.toml"

def test_challenge_toml_uses_nn_glob() -> None:
    toml = (repo_root() / ".mise.toml").read_text()
    assert 'challenges/${usage_challenge' in toml or 'challenges/$usage_challenge' in toml
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/challenges/offline/test_mise_tasks.py -v`
Expected: FAIL — tasks not present in `mise tasks` output.

- [ ] **Step 3: Append the four tasks to `.mise.toml`**

```toml
[tasks."challenge:verify"]
description = "Run a challenge's verification gate. Usage: mise run challenge:verify <NN>"
usage = 'arg "<challenge>" help="Challenge number e.g. 02"'
run = '''
set -e
DIR=$(echo challenges/${usage_challenge?}-*)
[ -d "$DIR" ] || { echo "No challenge dir for '${usage_challenge}' (looked for $DIR)"; exit 1; }
bash "$DIR/verify.sh"
'''

[tasks."challenge:verify-all"]
description = "Run every challenge's verification gate in order"
run = '''
set -e
for DIR in challenges/[0-9][0-9]-*; do
  echo "== $DIR =="
  bash "$DIR/verify.sh"
done
'''

[tasks."challenge:dbt"]
description = "Run dbt inside a challenge's dbt project. Usage: mise run challenge:dbt <NN> -- <dbt args>"
usage = '''
arg "<challenge>" help="Challenge number e.g. 02"
arg "[extra_args]" var=#true help="dbt args e.g. build --select stg_holdings"
'''
run = '''
set -e
DIR=$(echo challenges/${usage_challenge?}-*)
cd "$DIR/dbt"
/opt/venv/bin/python ../../../dbt_wrapper.py ${usage_extra_args:-build} --project-dir . --profiles-dir dbt_profiles --target local
'''

[tasks."challenge:reset"]
description = "Re-blank a challenge's authored files back to stubs. Usage: mise run challenge:reset <NN>"
usage = 'arg "<challenge>" help="Challenge number e.g. 02"'
run = '''
set -e
DIR=$(echo challenges/${usage_challenge?}-*)
[ -d "$DIR/stubs" ] || { echo "No stubs/ to restore for $DIR"; exit 0; }
cp -R "$DIR/stubs/." "$DIR/dbt/"
echo "Reset $DIR working models to stubs."
'''
```

Note: `challenge:reset` for 03/04 (whose artifacts live under `data_products/`) is overridden per-challenge — see Tasks 8 and 11, which replace the `cp` target with the product path.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/challenges/offline/test_mise_tasks.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add .mise.toml tests/challenges/offline/test_mise_tasks.py
git commit -m "feat(challenges): add challenge:verify/verify-all/dbt/reset mise tasks"
git push
```

## Task 3: `tests/challenges/{offline,live}` wiring + ignores + parity

**Files:**
- Modify: `pytest.ini` (add two testpaths), `.sqlfluffignore`, `.dbtignore`
- Create: `tests/challenges/live/__init__.py`, `tests/challenges/live/test_smoke.py`
- Test: `tests/challenges/offline/test_wiring.py`

**Interfaces:**
- Produces: pytest collects `tests/challenges/offline` (default) and `tests/challenges/live` (integration-marked); native dbt/sqlfluff ignore `challenges/` so they never build/lint challenge SQL.

- [ ] **Step 1: Write the failing test**

Create `tests/challenges/offline/test_wiring.py`:

```python
from tests.challenges.conftest import repo_root

def test_pytest_ini_collects_challenge_suites() -> None:
    cfg = (repo_root() / "pytest.ini").read_text()
    assert "tests/challenges/offline" in cfg
    assert "tests/challenges/live" in cfg

def test_sqlfluff_ignores_challenges() -> None:
    ig = (repo_root() / ".sqlfluffignore").read_text()
    assert "challenges/" in ig

def test_dbt_ignores_challenge_solutions() -> None:
    ig = (repo_root() / ".dbtignore").read_text()
    assert "challenges/**/solution/**" in ig
```

Create `tests/challenges/live/__init__.py` (empty) and `tests/challenges/live/test_smoke.py`:

```python
import os
import pytest

pytestmark = pytest.mark.integration

@pytest.mark.skipif(os.environ.get("CERT_INTEGRATION_TESTS") != "1",
                    reason="live challenge checks require CERT_INTEGRATION_TESTS=1")
def test_live_suite_is_gated() -> None:
    # Placeholder that only runs under the live gate; real live checks land in Tasks 7,8,10,11.
    assert os.environ["CERT_INTEGRATION_TESTS"] == "1"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/challenges/offline/test_wiring.py -v`
Expected: FAIL — testpaths/ignores not updated yet.

- [ ] **Step 3: Update `pytest.ini`, `.sqlfluffignore`, `.dbtignore`**

`pytest.ini` — extend `testpaths` to:

```ini
testpaths =
    data_products
    tests/local_env/offline
    tests/local_env/live
    tests/challenges/offline
    tests/challenges/live
```

Append to `.sqlfluffignore`:

```
/challenges/
```

Append to `.dbtignore`:

```
challenges/**/solution/**
```

- [ ] **Step 4: Run offline suite + native parity**

Run: `pytest tests/challenges/offline -v`
Expected: PASS.
Run: `CERT_INTEGRATION_TESTS=0 pytest tests/challenges/live -v`
Expected: 1 skipped (gate off).
Run: `pre-commit run --all-files` and `mise run verify:local-dev`
Expected: both green (native flow unaffected — parity).

- [ ] **Step 5: Commit**

```bash
git add pytest.ini .sqlfluffignore .dbtignore tests/challenges
git commit -m "feat(challenges): wire offline/live pytest suites and native-tooling ignores"
git push
```

---

# Phase 1 — Challenges 00–03

## Task 4: Challenge 00 — environment check

**Files:**
- Create: `challenges/00-environment-check/README.md`, `challenges/00-environment-check/verify.sh`
- Test: `tests/challenges/offline/test_ch00.py`

**Interfaces:**
- Produces: `challenges/00-environment-check/verify.sh` — exits 0 when the devcontainer toolchain + Databricks auth + Astro are reachable.

- [ ] **Step 1: Write the failing test**

Create `tests/challenges/offline/test_ch00.py`:

```python
import os, stat
from tests.challenges.conftest import repo_root

CH = repo_root() / "challenges" / "00-environment-check"

def test_verify_script_executable() -> None:
    assert (CH / "verify.sh").exists()
    assert os.stat(CH / "verify.sh").st_mode & stat.S_IXUSR

def test_guide_reframed_for_devcontainer() -> None:
    readme = (CH / "README.md").read_text().lower()
    assert "devcontainer" in readme
    assert "byod" not in readme and "laptop" not in readme  # preflight BYOD framing dropped
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/challenges/offline/test_ch00.py -v`
Expected: FAIL — files absent.

- [ ] **Step 3: Create the guide + verify**

`challenges/00-environment-check/README.md` — adapt `preflight/00-environment-check/README.md`, replacing all BYOD/laptop wording with "this devcontainer ships the toolchain pre-installed; you only confirm auth + reachability." Keep the "know your toolchain" checklist.

`challenges/00-environment-check/verify.sh`:

```bash
#!/usr/bin/env bash
# 00 — environment check: the devcontainer toolchain + Databricks auth + Astro are ready.
set -uo pipefail
fail() { echo "  environment check: FAIL — $1"; exit 1; }

command -v dpc-check >/dev/null 2>&1 && dpc-check || fail "dpc-check not green (run 'mise run setup:databricks')"
databricks auth describe --profile DEFAULT >/dev/null 2>&1 || fail "Databricks auth not configured (mise run setup:databricks)"
astro version >/dev/null 2>&1 || fail "astro CLI missing"
echo "  environment check: PASS"
```

Then `chmod +x challenges/00-environment-check/verify.sh`.

- [ ] **Step 4: Run tests + the offline gate**

Run: `pytest tests/challenges/offline/test_ch00.py -v`
Expected: PASS.
Run: `mise run challenge:verify 00`
Expected: prints `environment check: PASS` when auth is set up (SKIP/`FAIL` acceptable offline in CI where Databricks is absent — the offline pytest above is the CI gate, not the live script).

- [ ] **Step 5: Commit**

```bash
git add challenges/00-environment-check tests/challenges/offline/test_ch00.py
git commit -m "feat(challenge-00): port environment check to the devcontainer"
git push
```

## Task 5: Challenge 01 — docker

**Files:**
- Create: `challenges/01-docker-intro/` (copy `Dockerfile`, `app/`, `verify.sh`, guide from preflight)
- Test: `tests/challenges/offline/test_ch01.py`; live: `tests/challenges/live/test_ch01_docker.py`

**Interfaces:**
- Produces: `challenges/01-docker-intro/verify.sh` — builds + runs the image on the devcontainer's dockerd and greps expected output.

- [ ] **Step 1: Write the failing offline test**

Create `tests/challenges/offline/test_ch01.py`:

```python
from tests.challenges.conftest import repo_root
CH = repo_root() / "challenges" / "01-docker-intro"

def test_dockerfile_and_verify_present() -> None:
    assert (CH / "Dockerfile").exists()
    assert (CH / "verify.sh").exists()
    assert (CH / "app").is_dir()

def test_dockerfile_pins_own_base_image() -> None:
    # 01 builds its own python:3.11-slim image, independent of the devcontainer's 3.13.
    assert "python:3.11-slim" in (CH / "Dockerfile").read_text()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/challenges/offline/test_ch01.py -v`
Expected: FAIL — dir absent.

- [ ] **Step 3: Copy artifacts + write the live test**

Copy verbatim from `preflight/01-docker-intro/`: `Dockerfile`, `app/`, `verify.sh`, and the guide (`README.md` from `CHALLENGES.md`, stripping the "Preflight / client sign-off" note and any per-challenge devcontainer references). `chmod +x challenges/01-docker-intro/verify.sh`.

Create `tests/challenges/live/test_ch01_docker.py`:

```python
import os, subprocess
import pytest
from tests.challenges.conftest import repo_root

pytestmark = pytest.mark.integration

@pytest.mark.skipif(os.environ.get("CERT_INTEGRATION_TESTS") != "1", reason="needs docker")
def test_docker_build_and_run_passes() -> None:
    ch = repo_root() / "challenges" / "01-docker-intro"
    r = subprocess.run(["bash", "verify.sh"], cwd=ch, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout
```

- [ ] **Step 4: Run offline test (+ live if docker available)**

Run: `pytest tests/challenges/offline/test_ch01.py -v`
Expected: PASS.
Run (optional, needs docker): `CERT_INTEGRATION_TESTS=1 pytest tests/challenges/live/test_ch01_docker.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add challenges/01-docker-intro tests/challenges
git commit -m "feat(challenge-01): port docker intro onto the devcontainer dockerd"
git push
```

## Task 6: Challenge 02 — dbt (guide + solution + shared profile)

**Files:**
- Create: `challenges/02-dbt-pipeline/dbt/` (from preflight, profile swapped), `challenges/02-dbt-pipeline/dbt_profiles/profiles.yml`, `challenges/02-dbt-pipeline/solution/`, `challenges/02-dbt-pipeline/README.md`, `challenges/02-dbt-pipeline/verify.sh`
- Test: `tests/challenges/offline/test_ch02.py`; live: `tests/challenges/live/test_ch02_dbt.py`

**Interfaces:**
- Produces: a dbt project at `challenges/02-dbt-pipeline/dbt` whose `dbt_profiles/profiles.yml` mirrors `data_products/asset_reference_data/dbt_profiles/profiles.yml`; `verify.sh` runs `dbt debug` + `dbt build` on Databricks. `solution/` holds the full solved models. (Stubs are added in Task 7.)

- [ ] **Step 1: Write the failing offline test**

Create `tests/challenges/offline/test_ch02.py`:

```python
import yaml
from tests.challenges.conftest import repo_root
CH = repo_root() / "challenges" / "02-dbt-pipeline"

def test_dbt_project_and_solution_present() -> None:
    assert (CH / "dbt" / "dbt_project.yml").exists()
    assert (CH / "solution" / "models").is_dir()
    assert (CH / "dbt_profiles" / "profiles.yml").exists()

def test_profile_uses_shared_env_contract() -> None:
    prof = yaml.safe_load((CH / "dbt_profiles" / "profiles.yml").read_text())
    out = next(iter(prof.values()))["outputs"]["local"]
    assert "DBT_ACCESS_TOKEN" in str(out) or "DATABRICKS_TOKEN" in str(out)
    assert "training_dev" in str(out)  # app_catalog default

def test_no_preflight_run_md_or_own_devcontainer() -> None:
    assert not (CH / "RUN.md").exists()
    assert not (CH / ".devcontainer").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/challenges/offline/test_ch02.py -v`
Expected: FAIL — dir absent.

- [ ] **Step 3: Copy + adapt the dbt project and guide**

1. Copy `preflight/02-dbt-pipeline/dbt/` → `challenges/02-dbt-pipeline/dbt/` **and** → `challenges/02-dbt-pipeline/solution/` (the solution keeps the solved bodies).
2. Delete `challenges/02-dbt-pipeline/dbt/profiles.yml`; create `challenges/02-dbt-pipeline/dbt_profiles/profiles.yml` by copying `data_products/asset_reference_data/dbt_profiles/profiles.yml` and renaming the top-level profile key to `portfolio_analytics_challenge` (match the value of `profile:` in the copied `dbt_project.yml` — update that `profile:` key to the same name).
3. Convert `preflight/02-dbt-pipeline/CHALLENGES.md` (+ `CHALLENGES-PHASE2.md`) into `challenges/02-dbt-pipeline/README.md`: drop the "Preflight note" and the "sources already provisioned / RUN.md" framing (as-built: the raw sources are shipped as dbt seeds instead — see "Implementation outcomes (as-built)"); replace `verify-with-databricks.sh` references with `mise run challenge:verify 02` and `mise run challenge:dbt 02 -- build`; wrap each section's worked **Solution** in a collapsible `<details><summary>Solution</summary>…</details>` so it is compare-after-attempt.
4. Create `challenges/02-dbt-pipeline/verify.sh` — adapt `preflight/02-dbt-pipeline/verify-with-databricks.sh` to `cd "$(dirname "$0")/dbt"` and `--profiles-dir dbt_profiles`; keep the `dbt debug` + `dbt build` PASS/FAIL structure. `chmod +x`.

- [ ] **Step 4: Write the live test**

Create `tests/challenges/live/test_ch02_dbt.py`:

```python
import os, subprocess
import pytest
from tests.challenges.conftest import repo_root

pytestmark = pytest.mark.integration

@pytest.mark.skipif(os.environ.get("CERT_INTEGRATION_TESTS") != "1", reason="needs Databricks")
def test_solution_builds_green() -> None:
    # Maintainer/live baseline: the retained solution must build + test green on Databricks.
    ch = repo_root() / "challenges" / "02-dbt-pipeline"
    r = subprocess.run(["bash", "verify.sh"], cwd=ch, capture_output=True, text=True,
                       env={**os.environ, "DBT_MODELS_DIR": str(ch / "solution" / "models")})
    assert r.returncode == 0, r.stdout + r.stderr
```

(`verify.sh` reads `DBT_MODELS_DIR` if set to point dbt at the solution models; default is the working `dbt/models`.)

- [ ] **Step 5: Run offline test + parse gate**

Run: `pytest tests/challenges/offline/test_ch02.py -v`
Expected: PASS.
Run: `mise run challenge:dbt 02 -- parse`
Expected: dbt parses (solved bodies present → parses cleanly).

- [ ] **Step 6: Commit**

```bash
git add challenges/02-dbt-pipeline tests/challenges
git commit -m "feat(challenge-02): port dbt pipeline with shared env-contract profile + retained solution"
git push
```

## Task 7: Challenge 02 — derive stubs + reset + offline-parses-on-stubs

**Files:**
- Create: `challenges/02-dbt-pipeline/stubs/` (stub mirror of `dbt/`), overwrite `challenges/02-dbt-pipeline/dbt/models/**/*.sql` bodies with stubs
- Test: extend `tests/challenges/offline/test_ch02.py`

**Interfaces:**
- Consumes: `challenge:reset` from Task 2 (restores `dbt/` from `stubs/`).
- Produces: shipped working tree = stubs (parses, builds red); `stubs/` = pristine reset source.

- [ ] **Step 1: Write the failing test**

Append to `tests/challenges/offline/test_ch02.py`:

```python
def test_working_models_are_stubs_but_solution_is_solved() -> None:
    work = (CH / "dbt" / "models" / "staging" / "stg_holdings.sql").read_text()
    soln = (CH / "solution" / "models" / "staging" / "stg_holdings.sql").read_text()
    assert "select 1 as placeholder" in work.lower()
    assert "TODO" in work
    assert "select 1 as placeholder" not in soln.lower()

def test_stub_mirror_matches_working_tree() -> None:
    assert (CH / "stubs" / "models" / "staging" / "stg_holdings.sql").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/challenges/offline/test_ch02.py::test_working_models_are_stubs_but_solution_is_solved -v`
Expected: FAIL — working models are still solved copies.

- [ ] **Step 3: Blank each authored model to a stub**

For every file under `challenges/02-dbt-pipeline/dbt/models/**/*.sql`, replace the body with a stub that keeps the model's leading comment as the TODO. Example — `dbt/models/staging/stg_holdings.sql`:

```sql
-- stg_holdings — TODO(Challenge 02 · staging): cast + clean the custodian holdings
-- source to one row per (fund_id, position_date, instrument_id); no joins.
-- Source: {{ source('custodian','holdings_raw') }}.  See guide §"Staging".
select 1 as placeholder
```

Do **not** stub `sources.yml`, `schema.yml`, `dbt_project.yml`, or seeds. Then mirror the stubbed `dbt/` into `stubs/`:

```bash
rm -rf challenges/02-dbt-pipeline/stubs
cp -R challenges/02-dbt-pipeline/dbt challenges/02-dbt-pipeline/stubs
```

- [ ] **Step 4: Verify stubs parse, reset works, tests pass**

Run: `mise run challenge:dbt 02 -- parse`
Expected: parses (stubs are valid SQL).
Run: `printf '\n' >> challenges/02-dbt-pipeline/dbt/models/staging/stg_holdings.sql && mise run challenge:reset 02 && git diff --quiet challenges/02-dbt-pipeline/dbt/models/staging/stg_holdings.sql && echo RESET_OK`
Expected: prints `RESET_OK` (reset restored the pristine stub).
Run: `pytest tests/challenges/offline/test_ch02.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add challenges/02-dbt-pipeline tests/challenges/offline/test_ch02.py
git commit -m "feat(challenge-02): ship stubs + reset; retain solved models as the answer key"
git push
```

## Task 8: Challenge 03 — airflow native placement + Airflow-3 fixes + DAG stub

**Files:**
- Create: `data_products/portfolio_analytics/` (Cosmos DAG + co-located dbt from preflight 03), `challenges/03-airflow-orchestration/README.md`, `challenges/03-airflow-orchestration/verify.sh`, `challenges/03-airflow-orchestration/solution/` (solved DAG), `challenges/03-airflow-orchestration/stubs/` (DAG skeleton)
- Modify: `.mise.toml` `challenge:reset` handling for 03 (target the product DAG path)
- Test: `tests/challenges/offline/test_ch03.py`; live: `tests/challenges/live/test_ch03_airflow.py`

**Interfaces:**
- Consumes: the native Astro compose override (mounts `data_products/` as the dags folder) + OAuth-refreshed `databricks_default` connection.
- Produces: `data_products/portfolio_analytics/dags/portfolio_analytics_daily.py` importing cleanly under Airflow 3.x/cosmos 1.15; the trainee authors the DAG task-wiring.

- [ ] **Step 1: Write the failing offline test**

Create `tests/challenges/offline/test_ch03.py`:

```python
import ast, re
from tests.challenges.conftest import repo_root
PA = repo_root() / "data_products" / "portfolio_analytics"
CH = repo_root() / "challenges" / "03-airflow-orchestration"

def test_product_placed_natively_no_bundle() -> None:
    assert (PA / "dags" / "portfolio_analytics_daily.py").exists()
    assert (PA / "dbt" / "dbt_project.yml").exists()
    assert not (PA / "databricks.yml").exists()  # plain Cosmos project → skipped by CI bundle loop

def test_solution_dag_parses_and_has_tags() -> None:
    text = (CH / "solution" / "portfolio_analytics_daily.py").read_text()
    ast.parse(text)
    assert "tags=" in text

def test_no_airflow_2x_schedule_interval() -> None:
    text = (PA / "dags" / "portfolio_analytics_daily.py").read_text()
    assert "schedule_interval" not in text  # Airflow 3.x uses `schedule=`
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/challenges/offline/test_ch03.py -v`
Expected: FAIL — product absent.

- [ ] **Step 3: Place the product + apply Airflow-3/cosmos-1.15 fixes**

1. Copy `preflight/03-airflow-orchestration/dags/`, `dbt/`, `include/`, and `tests/` → `data_products/portfolio_analytics/` (same subpaths). The dbt project ships **complete** (it is the already-built 02 pipeline — not authored in 03).
2. Apply the Airflow 3.x / cosmos 1.15 must-fixes to `data_products/portfolio_analytics/dags/portfolio_analytics_daily.py` and `databricks_submit_run_dag.py`: `schedule_interval=` → `schedule=`; update provider import paths for apache-airflow-providers-databricks 7.7.4; adjust any changed `DbtDag`/`DbtTaskGroup`/`ProjectConfig` kwargs for cosmos 1.15; ensure the Cosmos `ProfileConfig` points at the `databricks_default` connection.
3. Add a marker `README.md` header to `data_products/portfolio_analytics/` pointing back to `challenges/03-airflow-orchestration/` and a `meta`/challenge tag in the dbt `dbt_project.yml`.
4. Save the corrected DAG to `challenges/03-airflow-orchestration/solution/portfolio_analytics_daily.py`; create the **stub** DAG (imports + `# TODO` where the `freshness → dbt_pipeline → publish` wiring goes) at `challenges/03-airflow-orchestration/stubs/portfolio_analytics_daily.py`, and ship that stub as the working `data_products/portfolio_analytics/dags/portfolio_analytics_daily.py`.
5. `challenge:reset 03`: override in `.mise.toml` so for `03` it copies `challenges/03-airflow-orchestration/stubs/portfolio_analytics_daily.py` → `data_products/portfolio_analytics/dags/portfolio_analytics_daily.py`.

- [ ] **Step 4: Write verify + live test**

`challenges/03-airflow-orchestration/verify.sh` — adapt `preflight/03-airflow-orchestration/check-dag-load.sh` to point `PYTHONPATH` at `data_products/portfolio_analytics` (for `include.*`) and its `dags/` (for `callbacks`), running `airflow dags list-import-errors` + the structural probes. `chmod +x`.

Create `tests/challenges/live/test_ch03_airflow.py`:

```python
import os, subprocess
import pytest
from tests.challenges.conftest import repo_root

pytestmark = pytest.mark.integration

@pytest.mark.skipif(os.environ.get("CERT_INTEGRATION_TESTS") != "1", reason="needs Airflow/Astro")
def test_solution_dag_triggers_green() -> None:
    ch = repo_root() / "challenges" / "03-airflow-orchestration"
    r = subprocess.run(["bash", "verify.sh"], cwd=ch, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
```

- [ ] **Step 5: Run offline tests + DAG-integrity + parity**

Run: `pytest tests/challenges/offline/test_ch03.py tests/local_env/offline/airflow -v`
Expected: PASS (existing `test_dag_integrity.py` still green with the new DAG).
Run: `mise run verify:local-dev`
Expected: green (native flow unaffected).

- [ ] **Step 6: Commit**

```bash
git add data_products/portfolio_analytics challenges/03-airflow-orchestration .mise.toml tests/challenges
git commit -m "feat(challenge-03): native portfolio_analytics DAG, Airflow-3 fixes, DAG stub + reset"
git push
```

# Phase 2 — Capstone 04 (`atlas_elt`) + retire `atlas_elt_demo`

## Task 10: Scaffold `data_products/atlas_elt` + dataset decomposition

**Files:**
- Create: `data_products/atlas_elt/` (product shell copied from `atlas_elt_demo`, renamed), the `capstone model → dataset/layer` mapping doc `data_products/atlas_elt/README.md`
- Test: `tests/challenges/offline/test_ch04_structure.py`

**Interfaces:**
- Produces: a paved-path product `atlas_elt` with entity-centric datasets (7 foundation entities + a few consumer marts), each with `dbt/{staging,integration,prepared}`, `contract/`, `bundle/`, `airflow/`, `runtime/`.

- [ ] **Step 1: Write the failing test**

Create `tests/challenges/offline/test_ch04_structure.py`:

```python
from tests.challenges.conftest import repo_root
AE = repo_root() / "data_products" / "atlas_elt"
ENTITIES = ["advisors","clients","funds","fund_holdings","instruments","portfolios","trades"]

def test_product_shell_present() -> None:
    for f in ("dbt_project.yml","databricks.yml","dbt_profiles/profiles.yml","datasets/sources.yml"):
        assert (AE / f).exists(), f
    assert not (repo_root() / "data_products" / "atlas_elt_demo").exists() or True  # demo removed in Task 12

def test_entity_datasets_have_paved_path_set() -> None:
    for e in ENTITIES:
        d = AE / "datasets" / e
        for sub in ("dbt","bundle","airflow","contract","runtime"):
            assert (d / sub).exists(), f"{e}/{sub}"

def test_mapping_doc_lists_layers() -> None:
    readme = (AE / "README.md").read_text()
    for token in ("staging","integration","prepared"):
        assert token in readme
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/challenges/offline/test_ch04_structure.py -v`
Expected: FAIL — `atlas_elt` absent.

- [ ] **Step 3: Copy the shell + write the mapping doc**

1. `cp -R data_products/atlas_elt_demo data_products/atlas_elt`.
2. Rename product identity: in `data_products/atlas_elt/dbt_project.yml`, `databricks.yml`, and every `datasets/*/dbt/*.yml`, replace `atlas_elt_demo` → `atlas_elt` (product name, `schema`/`domain` config, job prefixes).
3. Keep the 7 entity datasets (`advisors, clients, funds, fund_holdings, instruments, portfolios, trades`); add consumer-mart datasets `fund_nav`, `portfolio_perf`, `market_daily`, `segment_aum` (copy an entity dataset's `bundle/airflow/contract/runtime` shape and rename).
4. Create `data_products/atlas_elt/README.md` with the marker header (pointing to `challenges/04-atlas-capstone/`) **and** the concrete `capstone model → dataset/layer` table, per the design's decomposition: `src_* → staging`, `dom_* → integration`, marts → `prepared`; `rpt_portfolio_summary` + the `rpt_advisor_leaderboard ← rpt_advisor_book ← rpt_portfolio_summary` chain fold into `integration`.

- [ ] **Step 4: Run the structure test**

Run: `pytest tests/challenges/offline/test_ch04_structure.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add data_products/atlas_elt tests/challenges/offline/test_ch04_structure.py
git commit -m "feat(challenge-04): scaffold atlas_elt paved-path product with entity-centric datasets"
git push
```

## Task 11: Port capstone models into `atlas_elt` (solution) + stubs + guide + verify

**Files:**
- Create/populate: `data_products/atlas_elt/datasets/*/dbt/{staging,integration,prepared}/*.sql`, `challenges/04-atlas-capstone/solution/`, `challenges/04-atlas-capstone/stubs/`, `challenges/04-atlas-capstone/README.md`, `challenges/04-atlas-capstone/verify.sh`
- Modify: `.mise.toml` `challenge:reset` handling for `04`; each dataset `contract/<d>.odcs.yaml`
- Test: extend `tests/challenges/offline/test_ch04_structure.py`; live: `tests/challenges/live/test_ch04_capstone.py`

**Interfaces:**
- Consumes: the `atlas_elt` shell from Task 10; the paved-path bundle/DQ/DAG shapes from `atlas_elt_demo`/`asset_reference_data`.
- Produces: solved medallion models per dataset (retained as solution) + shipped stub bodies; `verify.sh` runs the paved-path offline (parse/compile/`bundle validate`) and live (`dbt build`, triggered DAG).

- [ ] **Step 1: Write the failing offline test**

Append to `tests/challenges/offline/test_ch04_structure.py`:

```python
def test_models_placed_by_refinement_role() -> None:
    # a source-aligned model lands in a dataset's staging layer; a mart in prepared.
    assert (AE / "datasets" / "trades" / "dbt" / "staging").exists()
    marts = list((AE / "datasets").glob("*/dbt/prepared/*.sql"))
    assert marts, "at least one consumer mart must live in a dataset's prepared/ layer"

def test_working_models_are_stubs() -> None:
    any_stub = list((AE / "datasets").glob("*/dbt/**/*.sql"))
    assert any_stub and any("select 1 as placeholder" in p.read_text().lower() for p in any_stub)

def test_contracts_ship_as_spec_files_only() -> None:
    contracts = list((AE / "datasets").glob("*/contract/*.odcs.yaml"))
    assert contracts  # spec files present; no contract:migrate anywhere in challenge steps
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/challenges/offline/test_ch04_structure.py -v`
Expected: FAIL — model layers not populated.

- [ ] **Step 3: Port the solved models by refinement role**

Map each `preflight/04-atlas-capstone/dbt/models/**` file to a dataset + layer and copy it in, adjusting `{{ ref() }}`/`{{ source() }}` and `{{ config(schema=…) }}` to the `atlas_elt` dataset/layer:
- `source_aligned/**/src_*` → the matching entity dataset's `dbt/staging/` (e.g. `src_trading__trades.sql` → `datasets/trades/dbt/staging/`).
- `domain_aligned/**/dom_*` → the matching entity dataset's `dbt/integration/`.
- `consumer_aligned/*` marts → the owning consumer-mart dataset's `dbt/prepared/` (`agg_fund_nav`→`fund_nav`, `rpt_portfolio_performance`→`portfolio_perf`, `ts_daily_market*`→`market_daily`, `agg_segment_aum`→`segment_aum`); fold `rpt_portfolio_summary`, `rpt_advisor_book`, `rpt_advisor_leaderboard` into `integration/` of their owning dataset (internal rollups, not published endpoints).
- Copy `macros/` (`epoch_date.sql`, `money.sql`), `snapshots/portfolios_snapshot.sql`, and `tests/` into the product `shared/` (macros/snapshots) and dataset `dbt/` (singular tests) — these ship complete.
- Copy the seeds (`preflight/04-atlas-capstone` source CSVs) into the product seeds dir.

Save the fully-populated product tree to `challenges/04-atlas-capstone/solution/` (a mirror of `data_products/atlas_elt/datasets/*/dbt`), then blank each authored model body to `select 1 as placeholder` + a `-- TODO(Challenge 04 · <layer>)` comment in the working `data_products/atlas_elt/` tree; mirror the stubbed model tree to `challenges/04-atlas-capstone/stubs/`.

Wire `challenge:reset 04` in `.mise.toml` to copy `challenges/04-atlas-capstone/stubs/.` over `data_products/atlas_elt/datasets/*/dbt/`.

- [ ] **Step 4: Author the guide + verify + live test**

`challenges/04-atlas-capstone/README.md` — port `preflight/04-atlas-capstone/CHALLENGES*.md` keeping its original focus (seed the source data, build `source→domain→consumer` models, understand the project); strip preflight-runner notes (`START_HERE.md`, `RUN.md`, `verify-with-*` variants); collapse worked Solutions into `<details>`. Do **not** add contract-creation steps.

`challenges/04-atlas-capstone/verify.sh`:
- Offline: `mise run challenge:dbt 04 -- parse`, the `atlas_elt` `ref()` graph compiles, and `databricks bundle validate -t local`.
- Live (only under `CERT_INTEGRATION_TESTS=1`): `mise run dbt:run atlas_elt` + `dbt:test`, `databricks bundle deploy -t local`, a triggered DAG run. **No `contract:migrate`.**

Create `tests/challenges/live/test_ch04_capstone.py` mirroring Task 6's live test but running the `atlas_elt` solution build + `bundle validate`.

- [ ] **Step 5: Run offline suite + bundle validate + parity**

Run: `pytest tests/challenges/offline/test_ch04_structure.py -v`
Expected: PASS.
Run: `cd data_products/atlas_elt && databricks bundle validate -t local`
Expected: validates.
Run: `mise run verify:local-dev`
Expected: green.

- [ ] **Step 6: Commit**

```bash
git add data_products/atlas_elt challenges/04-atlas-capstone .mise.toml tests/challenges
git commit -m "feat(challenge-04): port capstone medallion models, stubs, guide, and paved-path verify"
git push
```

## Task 9: Remove the xfail + Phase-1 gate

**Files:**
- Modify: `tests/challenges/offline/test_home.py` (drop the `xfail` from Task 1)

- [ ] **Step 1: Remove xfail and run the full offline suite**

Delete the `@pytest.mark.xfail` decorator added in Task 1 Step 5.
Run: `pytest tests/challenges/offline -v`
Expected: PASS including `test_five_challenge_dirs_present` (all five dirs exist now that Task 11 has created `04`).

- [ ] **Step 2: Commit**

```bash
git add tests/challenges/offline/test_home.py
git commit -m "test(challenges): enforce full challenge-dir set after 04 exists"
git push
```

## Task 12: Retire `atlas_elt_demo`

**Files:**
- Delete: `data_products/atlas_elt_demo/`
- Modify: `docker-compose.override.yml:34`, `.devcontainer/README.md:252`, `data_products/test_atlas_local_runtime_contract.py`, `tests/local_env/offline/tooling/test_devcontainer_dind_wiring.py`
- Test: existing atlas tests (repointed) + `tests/challenges/offline/test_ch04_structure.py`

**Interfaces:**
- Consumes: `atlas_elt` from Tasks 10–11 (the replacement referenced by the repointed tests/defaults).

- [ ] **Step 1: Repoint the known references (write the change, tests are the gate)**

- `docker-compose.override.yml:34`: `AIRFLOW_VAR_DATA_PRODUCT_NAME: "${AIRFLOW_VAR_DATA_PRODUCT_NAME:-atlas_elt_demo}"` → `...:-atlas_elt}"`.
- `.devcontainer/README.md:252`: repoint the `atlas_elt_demo_clients.run_clients_dbt` / `clients_job` example to the `atlas_elt` `clients` dataset job name.
- `data_products/test_atlas_local_runtime_contract.py`: change every `data_products/atlas_elt_demo/...` path (e.g. `variables/clusters.yml`) to `data_products/atlas_elt/...`; drop any assertion that encodes the demo's `select *` passthrough shape.
- `tests/local_env/offline/tooling/test_devcontainer_dind_wiring.py`: repoint the ~14 structural `atlas_*` assertions to `data_products/atlas_elt/`.

- [ ] **Step 2: Delete the demo + confirm no functional refs remain**

```bash
rm -rf data_products/atlas_elt_demo
grep -rn "atlas_elt_demo" --include=*.py --include=*.yml --include=*.yaml --include=*.md . | grep -v "docs/" | grep -v ".worktrees/"
```
Expected: no functional (non-historical-doc) references remain.

- [ ] **Step 3: Run the full gate**

Run: `pytest data_products tests/local_env/offline tests/challenges/offline -q`
Expected: PASS (repointed atlas tests green against `atlas_elt`).
Run: `mise run verify:local-dev` and `pre-commit run --all-files`
Expected: both green (parity with the pre-port baseline).

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat(challenge-04): retire atlas_elt_demo; repoint defaults and atlas tests to atlas_elt"
git push
```

---

## Self-Review

**Spec coverage** (design doc → task):
- Shared foundation: Location/home → T1; one-auth reuse → T4 (`setup:databricks` prerequisite, no per-challenge auth); first-class offline/live tests → T3 + per-challenge; trainee stubs + reset + retained solution → T7, T8, T11; non-interference/ignores + parity → T3 (and re-checked in T8, T11, T12); discoverability + challenge↔product marker/tag → T1, T8 (README header + dbt `meta`), T10.
- "One gate, two readings" (trainee completion vs builder/CI health) → offline pytest = health (T3+); live `verify.sh`/`test_*_live` = completion (T5–T11).
- Part 1: 00 → T4; 01 → T5; 02 → T6–T7; 03 native + Airflow-3 fixes + CI-skip (no `databricks.yml`) → T8.
- Part 2: target `atlas_elt` + decomposition → T10; per-dataset artifacts + orchestration + port-not-rewrite + contracts-as-spec-only (no `contract:migrate`) → T11; verify (offline/live) → T11; removing `atlas_elt_demo` → T12.
- Global constraints (Airflow 3.x, dbt 1.11, names not prefixed, contract publish out of scope, native parity) → encoded in Global Constraints + asserted in T3/T8/T11/T12.

**Placeholder scan:** ported bulk (dbt models, DAG, guides) is specified as copy-from-exact-path + explicit transformation, not "TBD"; all new artifacts (mise tasks, tests, stub template, verify scripts, edits) show complete content.

**Type/name consistency:** `conftest.py` `repo_root()`/`challenge_dirs()` defined in T1 and reused unchanged; `challenge:reset` restores from `stubs/` (T2) with per-challenge target overrides declared in T8/T11; product names `portfolio_analytics`/`atlas_elt` used consistently; `DBT_MODELS_DIR` introduced in T6 `verify.sh` and reused by its live test.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-28-training-challenges-and-atlas-capstone-port.md`. Two execution options:

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks, fast iteration (`superpowers:subagent-driven-development`).
2. **Inline Execution** — execute tasks in this session with checkpoints (`superpowers:executing-plans`).

## Implementation outcomes (as-built, 2026-07-28)

Deviations from the planned tasks, found during implementation. Full rationale is in the
design doc's "Implementation notes (as-built)"; this maps them to the tasks above.

- **T6/T7 (02) — sources ship as seeds, not "already provisioned."** Step 3.3 dropped the
  "sources already provisioned" framing assuming the raw tables existed; they did not — the
  preflight's `provision-raw-sources.sql` (a manual "run before verify" script) was never
  ported. That script's data now ships as CSV seeds
  (`challenges/02-dbt-pipeline/dbt/seeds/*_raw.csv`) — same author values, delivered via the
  dbt/mise flow — with `sources.yml` pinning `database`/`schema` to the dbt target so
  `source()` resolves to the seeded relation. Step 3.4's `verify.sh` is now **seed → run →
  test** through `dbt_wrapper.py` (not `dbt debug` + `dbt build`), and a `challenge:seed
  <NN>` mise task was added.
- **T6/T7 (02) — scaffolding restore (trainee walkthrough).** A later walkthrough found the
  port also dropped the `models:` block (folder `+tags`/`+materialized`/marts ZORDER
  post-hook) and both `schema.yml` files. Restored the `models:` block to `dbt/` **and**
  `stubs/` (so `challenge:reset` stops clobbering the seed post-hook and erroring `source
  freshness`); shipped `marts/schema.yml` (C5) and kept `staging/schema.yml` in `solution/`
  only (S8 authors it). The capstone mart + `reconcile_daily_exposure` test are now
  trainee-created in C10 (removing the shipped stubs that broke C7's full build and
  mis-counted models); `assert_nav_within_tolerance` ships as a failing stub. The three
  `show --inline "<SQL>"` checks (mise word-splitting + `*` glob-expansion) became
  `show --select` / build-log checks. Offline guards in `test_ch02.py` lock these in.
- **T8 (03) — verify is a static wiring gate; astro-runtime fixes added.** A DagBag load
  renders Cosmos via `dbt ls` (only viable in the configured astro runtime), so `verify.sh`
  statically checks the DAG wiring (`start → source_freshness_check → dbt_pipeline →
  publish_to_catalog → end`) with `ast`. Registering the DAGs in astro also required: a
  `sys.path` bootstrap (`airflow_local_settings.py` + a `docker-compose.override.yml`
  mount), `ExecutionConfig(dbt_executable_path=…)` on the `DbtTaskGroup`, Cimon
  `usage-id`/`cost-center` tags, and `PythonOperator` in place of `BashOperator`
  (Cimon-blocked) — with the guide updated to teach the `PythonOperator` pattern. A real
  `astro dev start` + trigger (beyond parse) then required, for a green 24/24 run:
  freshness-gate auth via the `databricks_default` connection token (not the static oauth
  profile, which hangs on interactive browser OAuth); Cosmos `DatabricksTokenProfileMapping`
  + explicit `http_path` (the OAuth-M2M mapping needs a `client_id` the local token
  connection lacks); forwarding `DBT_SCHEMA`/`DBT_CATALOG` into the containers; and
  provisioning the raw feeds by reusing `challenge:seed 02` (with a post-hook refreshing
  `_extracted_at`). A later trainee walkthrough surfaced a **cold-start** failure:
  `http_path`/`DBT_SCHEMA`/`DBT_CATALOG` are captured from the shell env **at `astro dev
  start` time** (Cosmos needs `http_path` at DAG parse time), so booting the stack before
  `mise run setup:databricks` populated `~/.config/dpc/databricks.env` — easy during the
  devcontainer's multi-minute first-run init — left the containers empty and Cosmos/the gate
  failed with *"The config 'http_path' is required"*. Fixed by booting the stack in the
  **Prerequisites** (after setup + seeding), warning to wait for setup and `astro dev
  restart` on a cold start, and making the freshness gate capture dbt's output and report a
  connection failure distinctly from a stale-feed breach (it previously said "breached
  error_after" for every failure). Guide sections 4/5 also dropped their vacuous `astro dev
  parse` prefix (their checks run the task in the live scheduler). The guide's CLI commands
  were also retargeted from bare `airflow …` to
  `astro dev run …` (Airflow 3 syntax), and the parity check to `show --select` (mise
  word-splits `show --inline` SQL). Phase 2's checks were made trainee-runnable too:
  `test_dag_structure.py` is now a static ast/text test (no DagBag — airflow is only in the
  astro containers) checking callbacks/SLA/no-secrets and passing on stub + solution (the
  chain stays the `verify.sh` gate); `python -m pytest` -> bare `pytest` and the yaml panel
  count -> `grep` (the trainee's `.venv` lacks pytest/PyYAML); and the "no Slack" greps were
  scoped to real usage, not the anti-goal wording the docs use.
- **T11 (04) — trainee walkthrough fixes.** A fresh-eyes subagent walkthrough surfaced the
  real gaps: the port shipped `dbt_project.yml` with a bare `models: {+materialized: view}`
  and **no alignment tags**, so the guide's `--select tag:source-aligned|domain-aligned|
  consumer-aligned` build flow matched 0 nodes and the whole capstone cascaded into
  `TABLE_OR_VIEW_NOT_FOUND`. Fixed by declaring the layer tags folder-by-folder (a full
  `dbt build` then runs 40/40 green). Also: §4/§6 `show --inline "<SQL>"` -> `show --select`
  (mise word-split, as in 02/03); and `databricks bundle validate` (Terraform `openpgp: key
  expired`, environmental) is now a **non-fatal warning** so it no longer aborts the verify
  gate. Offline guards added to `test_ch04_structure.py`.
- **Verify learner-gate + wrapper standardization (all challenges).** `verify.sh` builds
  the trainee's own working tree — RED on unsolved stubs, GREEN when solved — and challenge
  dbt runs go through `dbt_wrapper.py` with an explicitly resolved interpreter. Offline
  contract tests in `tests/challenges/offline/` lock these behaviours.
