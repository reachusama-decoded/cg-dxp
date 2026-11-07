# Contributing to AI Catalyst

Thanks for helping build Catalyst. This repo is a library of AI **skills** that
accelerate the [Data Product Lifecycle (RFD 0002)](rfd/0002/README.md). This
guide is a cookbook — follow it and your change will pass review the first time.

This model follows widely-shared open-source practice — see GitHub's
[Open Source Guide](https://opensource.guide/) — distilled to three things: the
process is **documented** (this file), the **mechanics are mechanical** (a test
suite + linters, not reviewer taste), and the **barrier to contribute is low**.
You run those checks yourself *before* you open a PR — there is no CI doing it
for you today — and once they pass and one admin approves, a project admin
merges. Catalyst diverges from the lightest-weight open-source defaults in three
ways — a *mandatory* quality gate, decisions recorded as RFDs, and no contributor
sign-off — each of which is described in context below.

---

## What belongs here

A contribution belongs in Catalyst if it **supports the Data Product Lifecycle**:

- ✅ A skill that accelerates a lifecycle phase (discovery, design, build,
  validate, publish, operate) or generates a lifecycle artifact.
- ✅ A capability skill that lifecycle skills compose (connect to Databricks,
  profile a table, trace lineage).
- ❌ General-purpose or single-team tooling that doesn't support the DPLC.
- ❌ Meta-tooling *about this repo* (contribution helpers, CI scripts as skills)
  — `skills/` is reserved for DPLC skills. Repo tooling lives in `scripts/` or
  this document.

If you're unsure whether an idea fits, open an issue first, or — for anything
that sets precedent — write an [RFD](rfd/0001/README.md) before the code.

The full strategy, four-tier taxonomy, and quality bar live in
[RFD 0006](rfd/0006/README.md). This guide is the hands-on version.

---

## A skill in a nutshell

A skill is a folder under `skills/` containing a `SKILL.md` and optional
supporting files:

```
skills/<skill-name>/
├── SKILL.md          # required — instructions + YAML frontmatter
├── references/       # optional — long-form docs loaded on demand
├── templates/        # optional — artifact templates the skill fills
└── scripts/          # optional — deterministic Python the skill calls
```

- Folder name is **kebab-case** and **must match** the `name:` in frontmatter.
- The filename is exactly `SKILL.md` (case-sensitive). No `README.md` inside a
  skill folder.

The offline suite enforces a frontmatter contract (`tests/ci/test_skill_frontmatter_contract.py`).
Every skill needs:

```yaml
---
name: my-skill                 # kebab-case, matches the folder name
description: |                  # WHAT it does + WHEN to use it + trigger phrases
  One or two sentences on what the skill does. Use when the user asks to
  "do the thing", "phrase two", "phrase three".
allowed-tools: Read Grep       # non-empty; the tools the skill may use
metadata:
  tier: capability             # orchestrator | workflow | document | capability
  lifecycle-phase: phase-3-design   # which DPLC phase (or "none" for utilities)
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: []
---
```

Keep `SKILL.md` under ~5,000 words; move long-form detail into `references/`.
No MCP references anywhere (`tests/ci/test_skill_no_mcp.py` enforces this). Any
`pip install` in a code block must route through cgrepo — see
[CLAUDE.md](CLAUDE.md) (`tests/ci/test_skill_cgrepo_compliance.py` enforces this).

---

## Add a new skill

1. **Branch.** `git checkout -b feature/<skill-name>`.
2. **Create the folder** `skills/<skill-name>/` with a `SKILL.md`. Copy the
   frontmatter of a similar existing skill (e.g.
   [`connect-databricks`](skills/connect-databricks/SKILL.md) for a capability,
   [`data-contract`](skills/data-contract/SKILL.md) for a document skill) and
   adapt it. Pick the right `tier` and `lifecycle-phase`.
3. **Register it** in [`plugin.json`](plugin.json) — add `"skills/<skill-name>"`
   to the `skills` array. The offline suite enforces a strict skill-dir ↔ `plugin.json`
   bijection (`tests/ci/test_plugin_json_consistency.py`); a skill that isn't
   registered (or a registration without a folder) fails the build.
   Nothing to do for Claude Code — it auto-discovers `skills/<name>/SKILL.md`,
   so `.claude-plugin/` carries no skills list to keep in step.
4. **List it** in [`skills/README.md`](skills/README.md) under the right tier.
5. **Refresh the skills graph** — `python scripts/build_skills_graph.py`. It
   re-derives [`docs/skills-graph/graph.json`](docs/skills-graph/README.md) from
   frontmatter in well under a second. The offline suite fails if you forget, so
   this is checked rather than remembered.
6. **Run the checks locally** (see below).
7. **Open a PR.**

---

## Update an existing skill

1. **Branch.** `git checkout -b fix/<skill-name>-<short-desc>`.
2. **Edit** `skills/<skill-name>/SKILL.md` (and its `references/` / `templates/`
   as needed). If you change behavior, update the `description` so the skill
   still auto-loads on the right prompts.
3. **Run the checks locally.**
4. **Open a PR** describing what changed and why.

Small, focused PRs review fastest. One logical change per PR.

---

## Evolve or retire a skill

- **Rename a skill:** rename the folder, update `name:` in frontmatter, and
  update the entry in both `plugin.json` and `skills/README.md`. Grep the repo
  for the old name (`grep -rn old-name skills/ rfd/`) and fix references so
  `tests/ci/test_no_legacy_skill_references.py` stays green.
- **Split or merge skills:** treat the new skills as *adds* and the old ones as
  *removals*; keep the `plugin.json` bijection intact in the same PR.
- **Deprecate / remove a skill:** delete the `skills/<name>/` folder **and** its
  `plugin.json` entry **and** its `skills/README.md` row in the same PR (all
  three, or the suite fails). Note the removal in [`CHANGELOG.md`](CHANGELOG.md).

Any of these change frontmatter, so rerun `python scripts/build_skills_graph.py`
before opening the PR.

Anything that changes how skills are structured, tiered, or governed across the
repo warrants an [RFD](rfd/0001/README.md) before the code.

---

## Run the checks locally

This is the "automate the mechanics" half of the model: run these before every
PR.

> **This run is the gate.** No CI workflow runs these checks for you when you
> open a PR. If you don't run them locally, they don't get run. The repo has no
> workflow files at all — repo-owned GitHub Actions are not enabled in this org,
> so the only automation on a PR is GitHub's own Copilot review. Wiring the
> suite itself into CI is proposed in RFD 0023 §5.

```bash
# Structural + contract checks (offline, fast — no network, no LLM):
python -m pytest tests/ci tests/skills -q
```

The suite verifies:

- **`plugin.json` bijection** — every skill folder is registered, and vice versa.
- **Frontmatter contract** — `name` matches the folder; `description`,
  `metadata.tier`, `metadata.lifecycle-phase`, and `allowed-tools` are present
  and valid.
- **cgrepo compliance** — no public-registry `pip install` (must use cgrepo).
- **MCP ban** — no MCP tools/servers referenced.
- **No legacy skill references** — renamed/removed skills aren't left dangling.
- **Skills-graph freshness** — `docs/skills-graph/graph.json` still matches the
  frontmatter on disk. If it doesn't, the failure names the drift and the fix is
  `python scripts/build_skills_graph.py`.

If your change includes Python, SQL, or other code, also run the relevant
[RFD 0008](rfd/0008/README.md) linters for that language (e.g. `ruff` for
Python, `sqlfluff` for SQL) — the per-language tooling is documented in
`rfd/0008/<language>/README.md`.

Fix every failure before opening the PR. Don't skip hooks (`--no-verify`) to
force a green state.

---

## Behavior tests (optional for contributors; admins run them before merge)

Catalyst also has an LLM-judged **behavior test harness** (`bin/bt`, see
[`tests/behavior/README.md`](tests/behavior/README.md)) that drives real
`SKILL.md` prompts end-to-end and grades the output against a rubric. It is
**not a required pre-submit gate**: it needs a *test* Databricks workspace,
Confluence fixtures, and an LLM gateway that outside contributors won't have,
and each run bills tokens.

- **Outside contributors:** you don't need to run it. A project admin runs the
  relevant behavior case(s) before merging your PR.
- **Contributors with a test workspace** (internal teammates): running the case
  for the skill you touched is encouraged, best-effort:
  ```bash
  bin/bt smoke <skill>.case-01-happy-path
  ```
- **Adding a new skill?** Please add a behavior case under
  [`tests/behavior/cases/`](tests/behavior/README.md), even if you can't run it
  live — validate its schema and wiring for free with the fake runner:
  ```bash
  BEHAVIOR_TESTS_USE_FAKE_RUNNER=1 python -m tests.behavior --case <id>
  ```
  A project admin runs it live before merge.

---

## Open a pull request

1. Push your branch and open a PR against `main`.
2. **Title:** a short, descriptive summary (e.g. `Add profile-columns skill`,
   `Fix data-contract SLA freshness default`).
3. Fill in the [PR template](.github/PULL_REQUEST_TEMPLATE.md) — link the issue
   or RFD and complete the checklist.
4. Keep the PR focused: one skill or one logical change.

### Review & merge

- A PR is ready to merge when **the offline suite passes** (run locally — see
  above) and **one project admin approves** — deliberately low-ceremony. The
  branch ruleset enforces the pull request and the approval; the test run is on
  you.
- Reviewers focus on judgment: *is this the right skill, well-shaped, in the
  right tier?* The mechanical checks are the suite's job.
- **Only project admins merge.** Outside contributors (and skill authors) do not
  merge their own PRs, even once approved; a project admin performs the squash
  merge. Note this is currently a convention rather than an enforced control —
  the ruleset does not yet restrict who may merge, and RFD 0023 §5 proposes
  changing that.

---

## Bigger changes: write an RFD

If your change sets precedent — a new skill tier, a change to the frontmatter
contract, a cross-cutting convention — write an [RFD](rfd/0001/README.md) first
so the decision is discussed and recorded before the code. Day-to-day skill adds
and updates don't need one.

---

## Questions

Open an issue, or see the [Feedback](README.md#feedback) section of the README.
For the strategy behind these guidelines, see [RFD 0006](rfd/0006/README.md).
