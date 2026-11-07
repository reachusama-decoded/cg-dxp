# Astro TLS/uv Write-up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a clear troubleshooting write-up that explains the Astro `UnknownIssuer` TLS failure mode and the repo’s pip-forced ONBUILD strategy while keeping the newer runtime image.

**Architecture:** Update one operational documentation surface (`.devcontainer/TROUBLESHOOTING.md`) with a focused subsection containing symptoms, root cause, rationale, verification steps, and future uv guidance. Keep the change tightly scoped to troubleshooting and command accuracy. Validate references and command formats after edits.

**Tech Stack:** Markdown documentation, ripgrep.

## Global Constraints

- Primary source of truth must be `.devcontainer/TROUBLESHOOTING.md`.
- Explain root cause: Astro Runtime ONBUILD consumes root `requirements.txt`.
- Explain rationale: keep newer runtime image, force pip only for ONBUILD stability.
- Include explicit verification commands.
- Include future uv path note (possible, but not current default).
- Correct stale wait command format to `astro dev start --wait 3m`.
- Do not broaden scope into unrelated doc refactors.

---

### Task 1: Add the TLS/uv troubleshooting write-up

**Files:**
- Modify: `.devcontainer/TROUBLESHOOTING.md`
- Test: N/A (documentation change)

**Interfaces:**
- Consumes: Existing troubleshooting section structure and headings in `.devcontainer/TROUBLESHOOTING.md`.
- Produces: New troubleshooting subsection for `UnknownIssuer`/uv behavior with root-cause narrative and commands.

- [ ] **Step 1: Add new subsection under Airflow issues**

Insert a subsection with this structure and content scope:

```md
### `astro dev start` fails with TLS `UnknownIssuer` / dependency fetch errors

**Symptoms:** ...
**Root cause in this repo:** ...
**Why pip is forced (and runtime is still new):** ...
**Verify current wiring:** ...
**Future uv path (non-default):** ...
```

- [ ] **Step 2: Fill the section with exact repo-specific explanation**

Use concrete language tied to this repo:

```md
- Astro ONBUILD dependency install reads root `requirements.txt`.
- If ONBUILD takes uv path without corp trust wiring, HTTPS fetch can fail with `UnknownIssuer`.
- Repo mitigation: `ASTRO_RUNTIME_USE_PIP` + trusted-host/index directives in root `requirements.txt`.
- This changes installer behavior for ONBUILD; it does not require runtime downgrade.
```

- [ ] **Step 3: Add concrete verification commands**

Include command examples similar to:

```bash
grep -n "ASTRO_RUNTIME_USE_PIP" requirements.txt
grep -n -- "--trusted-host pip.astronomer.io" requirements.txt
astro dev start --wait 3m
```

- [ ] **Step 4: Commit write-up content**

```bash
git add .devcontainer/TROUBLESHOOTING.md
git commit -m "docs: add astro tls unknownissuer troubleshooting writeup"
```

### Task 2: Fix adjacent command accuracy and validate references

**Files:**
- Modify: `.devcontainer/TROUBLESHOOTING.md`
- Test: N/A (documentation change)

**Interfaces:**
- Consumes: Existing command examples in troubleshooting file.
- Produces: Updated command syntax and consistency with current Astro CLI duration format.

- [ ] **Step 1: Replace stale wait format**

Replace:

```md
astro dev start --wait 180
```

With:

```md
astro dev start --wait 3m
```

- [ ] **Step 2: Confirm no conflicting obsolete wait examples remain**

Run:

```bash
rg -n "astro dev start --wait 180|--wait [0-9]+$" .devcontainer/TROUBLESHOOTING.md
```

Expected: no stale `--wait 180` style commands remain.

- [ ] **Step 3: Commit command-accuracy update**

```bash
git add .devcontainer/TROUBLESHOOTING.md
git commit -m "docs: update astro wait command format"
```

## Self-Review

- **Spec coverage:** plan covers placement, root-cause explanation, pip rationale, verification commands, uv future note, and wait-format correction.
- **Placeholder scan:** no TBD/TODO placeholders; all steps include explicit file paths and concrete command content.
- **Type/contract consistency:** all references consistently target `.devcontainer/TROUBLESHOOTING.md`, root `requirements.txt`, and `astro dev start --wait 3m`.
