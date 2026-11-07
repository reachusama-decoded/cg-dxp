# Astro TLS/uv Write-up Design

**Date:** 2026-07-16  
**Repository:** `edo-training-data-products`  
**Status:** Approved design (ready for implementation planning)

## 1. Goal

Add an in-repo troubleshooting write-up that explains why `astro dev start` can fail with TLS `UnknownIssuer` errors in this environment, and why the repo currently forces pip for Astro ONBUILD dependency installation while keeping the newer runtime image.

## 2. Placement

Primary source of truth: `.devcontainer/TROUBLESHOOTING.md`.

Rationale: This is an operational startup/debugging issue, and that file already collects startup failures and remediation paths.

## 3. Content Design

Add a new troubleshooting section under Airflow/startup troubleshooting:

1. **Symptoms**
   - Concrete error signatures (`UnknownIssuer`, `Failed to fetch`, ONBUILD dependency install failures).
2. **Root Cause**
   - Astro Runtime ONBUILD consumes root `requirements.txt`.
   - Without the pip-forcing contract there, ONBUILD can use uv path that fails in corp TLS trust conditions.
3. **Why pip is forced**
   - Stability decision in this repo for ONBUILD stage.
   - Keep newer runtime image; force pip only for this build phase.
4. **What changed in this repo**
   - Root `requirements.txt` contains `ASTRO_RUNTIME_USE_PIP` and trusted-host/index directives for ONBUILD path.
5. **Verification commands**
   - Quick checks for config and behavior.
6. **Future uv path (non-default)**
   - uv is not impossible; it requires explicit trust wiring in ONBUILD context.

## 4. Adjacent Accuracy Fix

Update stale command format in troubleshooting:
- `astro dev start --wait 180` → `astro dev start --wait 3m`

Reason: current Astro CLI expects duration units.

## 5. Non-Goals

- No runtime downgrade in this change.
- No broad refactor of unrelated troubleshooting sections.
- No behavior changes outside documentation unless required by validation.

## 6. Success Criteria

1. Troubleshooting contains a clear, internally consistent explanation of TLS `UnknownIssuer` startup failures.
2. Documentation explicitly states why pip is forced in ONBUILD while keeping newer runtime.
3. Command examples are valid for current Astro CLI (`--wait 3m` style).
4. Engineers can follow the section to diagnose and verify the issue without external context.
