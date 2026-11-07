# UV Migration Certificate Handling Design

**Date:** 2026-07-22  
**Repository:** `edo-training-data-products`  
**Status:** Draft for review

## 1. Goal

Adopt uv as the default package installer where it provides measurable speed benefit, while preserving reliable corporate TLS behavior and existing Python 3.13 SSL strictness compatibility in this repo.

## 2. Scope and Decision

**Decision:** migrate **both** surfaces, in phases:

1. **Phase 1:** devcontainer uv hardening first.
2. **Phase 2:** Astro image build stages in root `Dockerfile` (stage2/stage3) from pip to uv.

This repo uses `astro-runtime:...-base`, so the relevant migration surface is Dockerfile build steps, **not** ONBUILD hooks.

## 3. Why this is worth doing

Repo-specific benchmark results (cold-cache dry runs on current requirements) show consistent speedup:

- `.devcontainer/requirements.txt`: uv ~2.47x faster than pip
- `requirements.txt` set used by Astro image dependency install: uv ~2.78x faster than pip

The migration is justified on developer iteration speed alone, provided TLS reliability is preserved.

## 4. Current State (relevant facts)

1. `sitecustomize.py` disables `VERIFY_X509_STRICT` for Python TLS contexts.
2. Pip trust wiring is explicit (`/etc/pip.conf`, `PIP_CERT`, trusted-host/index patterns).
3. uv is already present and partially used in devcontainer utilities.
4. Root `Dockerfile` currently performs package install work with pip in stage2/stage3.

## 5. Alternatives considered

### A) Devcontainer-only migration

**Pros:** lowest risk, immediate speedup for local setup.  
**Cons:** leaves slower and inconsistent installer behavior in Astro image builds.

### B) Astro-build-only migration

**Pros:** simplifies one surface in production-like image path.  
**Cons:** misses immediate local setup gains and keeps dual-operating model for engineers.

### C) Both surfaces with phased rollout (**recommended**)

**Pros:** captures full speedup while controlling blast radius.  
**Cons:** requires disciplined test/docs updates and explicit rollback path.

## 6. Recommended Architecture

### 6.1 Shared installer contract

Define a small shared env contract for installer TLS/index behavior used by scripts/checks:

- `UV_NATIVE_TLS=1`
- `UV_INDEX_URL=https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/`
- `UV_EXTRA_INDEX_URL=https://cgrepo.capgroup.com/repository/cgpypi/simple/`
- `PIP_CERT=/cacert.pem` (kept for pip fallback)

### 6.2 Keep Python strictness workaround unchanged

Do not modify `sitecustomize.py` in this migration.  
Its role remains Python-runtime TLS compatibility. uv network behavior must be configured with uv-native flags/env.

### 6.3 Phase 1 delivery (devcontainer)

1. Standardize uv invocations to include native TLS + explicit index URLs.
2. Extend health checks so uv resolution against corp index is validated.
3. Keep pip fallback documented.

### 6.4 Phase 2 delivery (Astro base-image build)

1. Replace pip install commands in root `Dockerfile` stage2/stage3 with uv equivalents.
2. Keep constraints and index semantics explicit.
3. Validate via `astro dev start --wait 3m` and targeted tests.

## 7. Error handling and rollback

1. No silent fallback: if uv install fails, surface exact failing command and host.
2. Document a deterministic rollback: revert Dockerfile install commands to pip equivalents and re-run startup.
3. Keep rollback bounded to installer steps only; do not alter unrelated runtime/auth behavior.

## 8. Testing strategy

1. **Unit/static tests**
   - Assertions on script/Dockerfile wiring for uv flags, indexes, and cert contract.
2. **Local integration checks**
   - `dpc-check` includes uv resolution verification.
3. **Startup gate**
   - `astro dev start --wait 3m` succeeds without TLS `UnknownIssuer` at dependency install step.

## 9. Non-goals

1. No change to Databricks OAuth flow.
2. No runtime family/version switch as part of this migration.
3. No removal of pip from the repo; pip remains an explicit rollback path.

## 10. Success criteria

1. uv is the default installer in both devcontainer setup and Astro Dockerfile dependency stages.
2. Existing certificate-handling behavior remains reliable in corp network conditions.
3. Documented rollback is tested and clear.
4. Existing related tests pass with updated assertions.

## 11. Constraint-file analysis addendum (2026-07-23)

Question investigated: can we replace repo-level dependency pins with an Airflow constraints file again?

Findings:

1. The Astro base image constraint file (`/etc/pip-constraints.txt`) is **not equivalent** to our repo pins; it currently contains only:
   - `apache-airflow==3.1.8+astro.4`
   - `apache-airflow-task-sdk==1.1.8+astro.4`
   - `SQLAlchemy==1.4.54`
2. The previous Dockerfile implementation (initial commit `e97eb8c`) used Apache constraints from
   `constraints-3.1.3/constraints-3.12.txt`. That file matched many of our selected provider/data pins, but it also pinned:
   - `apache-airflow-providers-cncf-kubernetes==10.9.0`
   - `kubernetes==33.1.0`
   - `kubernetes_asyncio==33.3.0`
3. Current Astro runtime includes `astronomer-kubernetes-executor==10.17.1+astro.1`, which requires
   `kubernetes>=35.0.0,<36.0.0`. That is incompatible with the `kubernetes==33.1.0` constraint from Airflow 3.1.3.
4. Airflow 3.1.8 Apache constraints exist, but they shift a broader stack (for example databricks provider, amazon provider, pandas/numpy/fsspec/s3fs), which is a larger compatibility change than the targeted resolver fix.

Decision recorded:

- Keep explicit, repo-owned pins in `requirements-pypi.txt` for now (known-good build path).
- Do **not** reuse `constraints-3.1.3`.
- Revisit optional adoption of `constraints-3.1.8` only with a dedicated compatibility pass across local Astro startup + DAG runtime smoke tests.
