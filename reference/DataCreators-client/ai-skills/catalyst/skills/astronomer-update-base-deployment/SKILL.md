---
name: astronomer-update-base-deployment
description: |
  Update the base scaffolding of an existing Astronomer deployment repo
  (previously vended from the
  `cg-open-itg/template-copier-astro-infra-bundle` template) with the latest
  Astro / IAC template. Sources the template from the `main` branch of
  https://github.com/cg-open-itg/template-copier-astro-infra-bundle by
  default (clones on demand, cached under `~/.cache/catalyst/…`).
  Auto-detects Airflow 2 vs 3 from the target's Dockerfile, then
  classifies every template-owned file as missing / identical / divergent
  and overwrites divergent files in place by default so `git diff` and
  `git checkout` are the review/rollback tools. Also supports 3-way git
  merge, a preserve mode that keeps FILE.template-new siblings, or
  skipping divergent files. Never touches user data products or rendered
  per-env configs.
  Trigger phrases: "update the base of my astronomer deployment",
  "refresh scaffolding from template-copier-astro-infra-bundle", "sync my
  vended astro repo with the template", "pull latest astro/iac scaffolding",
  "migrate airflow 2 to 3 scaffolding", "astronomer update base deployment".
allowed-tools: Read Bash Write
metadata:
  tier: capability
  lifecycle-phase: cross-cutting
  dependencies: []
  consumes: []
  standards: []
  shared-components:
    core: []
    platforms: [astronomer, aws]
---

# astronomer-update-base-deployment

Use this skill when asked to *update the base scaffolding* of a downstream
Astronomer deployment repository that was previously vended from
[`cg-open-itg/template-copier-astro-infra-bundle`](https://github.com/cg-open-itg/template-copier-astro-infra-bundle)
(e.g. `edo-ig-data-products`, `sample-data-products`) with the latest
Astro / IAC scaffolding. The vended repo does not carry the `templates/`
folder, so it can drift from the current template contents; this skill
closes that drift.

The comparison source is always the **template repo on GitHub** — by
default the `main` branch of
`https://github.com/cg-open-itg/template-copier-astro-infra-bundle`,
cloned/fetched on demand into a local cache. Pin a different ref (tag,
branch, SHA) with `--template-ref`, or point at a local checkout with
`--template-root` to bypass the network entirely.

Primary executor script (deterministic):

- `skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh`

## When to use

- A vended deployment repo needs to pick up template changes since its
  last vend (Dockerfile bumps, new IAC files, updated `justfile`, etc.).
- A cross-version migration (Airflow 2 → 3) is required and you want a
  reviewable file-level plan before running `copier update --trust`.

## When NOT to use

- Bootstrapping a brand-new deployment repo from scratch — that is
  `copier copy` from the template, not this skill.
- Refreshing the parameterized `.copier` stencils (`.astro/config.yaml.copier`
  etc.) — those need copier variables. If the target has
  `.copier-answers.yml`, prefer `copier update --trust` in the target
  repo. This skill's overlay complements that path when the answers file
  is missing or you want a targeted file-level refresh.
- Modifying user data products under `data_products/*` (excluding
  `data_products/utils/`) or rendered per-env Terraform configs.

## Inputs

- `--target <path>` (optional): path to the vended deployment repo. Default:
  current working directory.
- `--template-repo <url>` (optional): git URL of the template repo. Default:
  `https://github.com/cg-open-itg/template-copier-astro-infra-bundle.git`.
- `--template-ref <ref>` (optional): branch, tag, or SHA to source from.
  Default: `main`.
- `--template-cache <path>` (optional): where to cache the shallow clone.
  Default: `${CATALYST_CACHE_DIR:-$HOME/.cache/catalyst}/astronomer-update-base-deployment`.
  An existing non-git directory must be empty; the skill refuses to remove
  caller-supplied contents.
- `--template-root <path>` (optional): path to a local checkout of the
  template repo. When set, the script uses it directly and skips the
  git fetch. Useful for offline runs or testing an unpublished branch.
- `--dry-run` / `--apply`: preview vs. actually write. Default is `--dry-run`.
- `--to-version 2|3` (optional): override the auto-detected Airflow major.
  Required for a cross-version upgrade (e.g. Airflow 2 → 3).
- `--strategy overwrite|merge|preserve|skip` (optional): how to handle files
  that already exist in the target **and differ** from the template. Default:
  `overwrite`. See [Divergence handling](#divergence-handling) below.
- `--baseline-ref <git-ref>` (optional): git ref inside the target repo whose
  content is the common ancestor for `--strategy merge`. If omitted, the merge
  auto-detects a per-file baseline (the commit that first added the file).
- `--backup`: with `--apply --strategy overwrite`, keep a `<file>.bak` next to
  every overwritten file. Rarely useful when the target is a git working tree.
- `--yes` / `-y`: skip the interactive confirmation prompt.

## Airflow version detection

The script picks the source template by classifying the target's Dockerfile.
Three signals are checked in order; the first one that answers wins:

1. **Presence of Airflow-3-only files.** If `requirements-pypi.txt` or
   `os-packages.txt` exists at the target root, it is Airflow 3.
2. **Dockerfile constraints URL.** The line
   `ADD https://raw.githubusercontent.com/apache/airflow/constraints-<X>.<Y>.<Z>/...`
   pins the constraints file that matches the base image's Airflow. The major
   version there (`2` or `3`) is authoritative for a working build.
3. **Dockerfile `FROM` line.** Astronomer Runtime `12.x` / `13.x` maps to
   Airflow 2; the new scheme `runtime:3.x-y` maps to Airflow 3.

Pass `--to-version 2|3` to override this (typically when migrating).

| Airflow major | Selected source                                  |
| ---           | ---                                              |
| `2`           | `<template-root>/templates/astro-2.x/`           |
| `3`           | `<template-root>/templates/astro-3.x/`           |

## Divergence handling

Every template-owned file (see full list below) is classified into one of five
buckets. The classification alone drives what happens — the `--strategy` flag
only changes the action for the **DIVERGENT** bucket.

| Bucket        | Meaning                                                     | Action                                                                                          |
| ---           | ---                                                         | ---                                                                                             |
| `MISSING`     | file exists in template, not in target                      | Always added. Safe.                                                                             |
| `IDENTICAL`   | file exists in both, byte-for-byte equal                    | No-op.                                                                                          |
| `DIVERGENT`   | file exists in both and content differs (target customized) | Follows `--strategy` (default `overwrite`).                                                     |
| `PARAM`       | `.copier` stencil (needs copier variables)                  | Skipped. Report suggests `copier update --trust` if `.copier-answers.yml` exists in the target. |
| `USER-OWNED`  | path is in the never-touch list (see below)                 | Skipped.                                                                                        |

### `--strategy` options for DIVERGENT files

- **`overwrite`** (default). Replace the target file with the template file.
  Because the target is a git working tree, `git diff` shows exactly what
  changed, `git checkout -- <file>` reverts a single file, and `git stash` /
  `git reset` are available for wholesale rollback. This is the standard
  workflow when the target's local edits are already committed and the goal
  is to see the incoming template delta in a normal review flow. Pass
  `--backup` if you want an extra `<file>.bak` sibling for peace of mind
  (rarely needed with git).

- **`merge`**. Attempt a real 3-way merge with `git merge-file`. The common
  ancestor is either `--baseline-ref` if given, or auto-detected per file (the
  earliest commit that added that file in the target repo). Outcomes:
  - clean merge → the target file is rewritten in place with both sides
    combined.
  - conflict → the target file is **left intact** and `<file>.template-new`
    is written for manual review.
  - no ancestor found → falls back to writing `<file>.template-new` for that
    file.

- **`preserve`**. Keep the target file exactly as it is. Write the new
  template content beside it as `<file>.template-new` so it shows up in
  `git status` as an untracked sibling. Non-destructive: no local edits are
  touched, but nothing is applied either. Use when the target is not a git
  working tree, or when you explicitly want to eyeball every divergence before
  adopting any of it.

- **`skip`**. Leave the target alone and do not write `.template-new`. Useful
  when you know a specific set of files is intentionally divergent (e.g. after
  an audit) and you want a clean plan run against remaining drift.

## Template scaffolding covered

Everything below is *considered* by the classifier (missing/identical/divergent).
Files are only actually copied when the classification + strategy calls for it.

**Root scaffolding (both versions):**

- `Dockerfile`
- `docker-compose.override.yml`
- `justfile`
- `packages.txt`
- `requirements.txt`
- `requirements-venv-cosmos.txt`
- `pyproject.toml`
- `pre-commit-config.yaml`
- `.dockerignore`
- `.gitignore`
- `README.md`
- `VERSION`

**Astro-2.x extras:** `README.test.md`

**Astro-3.x extras:** `os-packages.txt`, `requirements-pypi.txt`

**Infrastructure-as-Code (`iac/`):**

- `iac/.gitignore`, `iac/README.md`
- `iac/airflow_connections.tf`, `iac/airflow_variables.tf`
- `iac/databricks_rotation.tf`, `iac/datadog_dashboard.tf`
- `iac/main.tf`, `iac/outputs.tf`, `iac/providers.tf`, `iac/variables.tf`
- `iac/lambda/**` (Databricks token rotation Lambda)
- **Astro-3.x only:** `iac/iam.tf`, `iac/locals.tf`, `iac/lookup.tf`

**Astro utilities & fixtures:**

- `data_products/utils/autosys_scrape_calendar.dag.py`
- `plugins/README.md`
- `tests/data_products/**`

## What is preserved (user-owned)

The overlay never touches these paths, even when they exist inside the template
tree — they were rendered at vend time from copier variables or are user code:

- `data_products/*` **except** `data_products/utils/` (user data products,
  including anything scaffolded by `new-data-product-scaffold` /
  `new-dataset-scaffold`)
- `.astro/` (deployment metadata; includes the parameterized `config.yaml.copier`
  stencil which needs `astro_deployment_name`)
- `iac/config/deployment/{dev1,sqa1,prd1}/` and `iac/config/deployment/__ENV__/`
  (rendered per-env Terraform configs and `backend.tf`, `terraform.auto.tfvars`)
- `.env`, `.env.copier`, `.copier-answers.yml`, `.git/`
- Anything not shipped by the selected template

## Parameterized stencils (skipped, not applied)

The template contains a small set of files that end in `.copier` and depend on
copier variables such as `{{astro_deployment_name}}` or `{{project_atm_id}}`.
These cannot be overlaid by a plain file copy — they need to be rendered. The
script lists them in the plan and skips them.

Current stencils:

| Path                                                              | Renders from                     |
| ---                                                               | ---                              |
| `.astro/config.yaml.copier`                                       | `astro_deployment_name`          |
| `.env.copier` *(astro-3.x only)*                                  | multi-var deployment env         |
| `iac/config/deployment/__ENV__/backend.tf.copier`                 | `project_atm_id_lowered`, env    |
| `iac/config/deployment/__ENV__/__ENV___tfe_backend.config.copier` | env-scoped                       |
| `iac/config/deployment/__ENV__/terraform.auto.tfvars.copier`      | many copier vars                 |

If the target has `.copier-answers.yml`, `copier update --trust` in the target
repo is the correct way to refresh these stencils and is called out in the
script's report.

## Execution

### Preview (default)

```bash
./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \
  --target ../my-vended-repo
```

On first run, the script performs a shallow clone of the template repo's
`main` branch into `~/.cache/catalyst/astronomer-update-base-deployment/`
and prints the resolved template commit SHA in the report banner.
Subsequent runs `git fetch` the ref and fast-forward. The script then
prints:

- The template repo URL, requested ref, and resolved commit SHA
- The detected & selected Airflow major and the chosen template directory
- **Files to ADD** (missing in target)
- **Files IDENTICAL** to the template (no action)
- **DIVERGENT files** (target modified) — with the strategy-specific action
- Parameterized stencils that were skipped (with why)
- User-owned paths that were skipped

### Apply (overwrite — the git-first default)

```bash
./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \
  --target ../my-vended-repo --apply
```

This will:

- Add missing files.
- Do nothing to files identical to the template.
- Overwrite divergent files with the template content in the target working
  tree.

Because the target is a git repo, you review with `git diff` and revert with
`git checkout -- <file>`. Any uncommitted local edits to a divergent file are
shadowed by the template content in the working tree — make sure the target
has a clean working tree (or your edits are already committed / stashed)
before running with `--apply`.

### Apply with 3-way merge

When the target has a git ref that represents the last vended-template state
(e.g. a `last-vend` tag committed right after the last `copier copy`):

```bash
./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \
  --target ../my-vended-repo --apply --strategy merge --baseline-ref last-vend
```

Each divergent file goes through `git merge-file -p <target> <ancestor> <template>`.
Clean merges overwrite the target; conflicts leave the target intact and drop
`<file>.template-new` alongside. If `--baseline-ref` is omitted, the ancestor is
auto-detected per file as the earliest commit that added that file in the
target repo (heuristic — fine for files never edited between add and now).

### Apply with preserve (`.template-new` siblings, non-destructive)

```bash
./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \
  --target ../my-vended-repo --apply --strategy preserve
```

Adds missing files but never touches divergent files. Instead it writes
`<file>.template-new` next to each one for hand-review. Use this when the
target is not a git working tree, or when you want a strictly non-destructive
audit before adopting anything.

After reviewing/merging:

```bash
find . -name '*.template-new'          # inspect
diff Dockerfile Dockerfile.template-new
# ... hand-merge what you want ...
find . -name '*.template-new' -delete  # clean up
```

### Cross-version upgrade (Airflow 2 → 3)

This is a significant change (different base image, different requirements
layout, additional Terraform files). Always run a dry-run first, review the
plan, and understand that:

- `packages.txt` semantics change (v2 has real packages; v3 is intentionally
  empty because ONBUILD triggers no-op it — real OS packages move to
  `os-packages.txt`).
- `requirements.txt` in v3 is a placeholder; the real Python list is
  `requirements-pypi.txt`.
- `iac/` gains `iam.tf`, `locals.tf`, `lookup.tf` and `main.tf` becomes a
  self-contained `astro_deployment` resource (v2 used a TFE module).
- The `Dockerfile` bakes in a lot of Airflow-3 defaults that v2 set via
  Terraform (`AIRFLOW__CORE__XCOM_BACKEND`, `AIRFLOW__SECRETS__BACKEND`,
  remote logging, kafka topics, datadog).

```bash
# Preview
./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \
  --target ../my-vended-repo --to-version 3

# Apply — default overwrite; commit or stash local edits first so `git diff`
# gives a clean picture of the incoming template delta.
./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \
  --target ../my-vended-repo --to-version 3 --apply

# Alternatively, preview the incoming diff without touching any file:
./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \
  --target ../my-vended-repo --to-version 3 --apply --strategy preserve
```

### Pinning or overriding the template source

By default, comparisons are against the tip of `main` on
`cg-open-itg/template-copier-astro-infra-bundle`. Two override paths:

```bash
# Pin to a specific tag or SHA (release-style upgrade)
./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \
  --target ../my-vended-repo --template-ref v1.4.0

# Use a local checkout (offline, unpublished branch, or template dev)
./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \
  --target ../my-vended-repo \
  --template-root ../template-copier-astro-infra-bundle
```

`--template-root` skips the git fetch entirely; the local path must contain
`templates/astro-2.x/` and `templates/astro-3.x/`.

## Post-upgrade validation

1. `cd <target> && git status` — review the diff before committing. With the
   default `overwrite` strategy, divergent files show up as modified in the
   working tree; use `git diff <file>` to inspect and
   `git checkout -- <file>` to revert individual files.
2. If you used `--strategy preserve` or `--strategy merge`,
   `find <target> -name '*.template-new'` — iterate through them; either
   `diff` + hand-merge relevant changes into the target file, or delete the
   `.template-new` if nothing new is worth adopting.
3. `astro dev parse` — confirm DAGs still parse under the (possibly new) image.
4. `cd <target>/iac && terraform validate` — sanity-check TF.
5. If the target has `.copier-answers.yml`, follow up with
   `copier update --trust` to refresh the parameterized stencils.

## Guardrails

- The target must be a git working tree if you use the default `overwrite`
  strategy — that is where local edits go for review and rollback. If the
  target has no git history (or you want a strictly non-destructive audit),
  use `--strategy preserve` instead.
- Never overwrite files under `data_products/` other than `data_products/utils/`.
- Never overwrite `.astro/`, `iac/config/deployment/{dev1,sqa1,prd1,__ENV__}/`,
  `.copier-answers.yml`, or `.env`.
- Refuse to classify or write through symlinked parent components, symlinked
  destinations, directories, or other non-regular target paths.
- Default mode is `--dry-run`; `--apply` must be explicit and prompts for
  confirmation unless `--yes` is passed.
- For a full semantic upgrade including parameterized stencils, prefer
  `copier update --trust` in the target when copier state exists. This skill's
  overlay complements that path when the answers file is missing or you want a
  targeted file-level refresh.
- The report banner always shows the resolved template commit SHA so the
  upgrade is reproducible; capture it in the PR description if you want an
  auditable record of which template revision was applied.

## Design Notes

The executor is intentionally Bash because its controlling operations are the
native git and filesystem primitives that define the safety model: `git`
provides revision lookup and 3-way merge, while `find`, `cmp`, and `cp -p`
support deterministic path classification and preservation of file metadata.
Keeping those operations in one directly runnable script also makes the
dry-run/apply boundary visible at the command line. Extend the Bash entrypoint
while the logic remains shell-shaped; extract a helper only if the merge or
classification rules outgrow shell's ability to express them clearly.
