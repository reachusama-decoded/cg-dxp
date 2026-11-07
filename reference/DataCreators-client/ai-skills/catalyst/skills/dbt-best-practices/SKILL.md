---
name: dbt-best-practices
description: |
  Generation-time best practices for dbt projects on Databricks. Loads
  RFD 0008 SQL coding standards + dbt-project-evaluator categorical
  rules (modeling, testing, documentation, structure, performance,
  governance) + Capital Group's prototype-grounded patterns
  (source-wrapper, bitemporal-incremental, audit-columns, checkpoint-table,
  surrogate-key). Applies mode-aware severity (prototype / production /
  lift-and-shift) so creators can iterate without DPLC rigor and tighten
  on promotion.
  Trigger phrases: "dbt best practices", "should I do X in dbt",
  "test coverage", "model materialization", "dbt naming conventions",
  "audit columns", "bitemporal load".
allowed-tools: Read
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards:                          # cross-cuts most RFD 0008 SQL rules
    - SQL-NAMING-001
    - SQL-NAMING-002
    - SQL-MODEL-002
    - SQL-MODEL-004
    - SQL-TEST-001
    - SQL-TEST-002
    - SQL-TEST-003
    - SQL-INCR-002
    - SQL-INCR-006
    - DBX-DELTA-001
---

# dbt Best Practices for Catalyst

> Generation-time guidance for every dbt-writing skill. Load this as Step 1 of `/dplc-build` model authoring; consult the per-mode severity table to decide what to enforce vs warn.

## Mode-aware rule severity

See `references/rule-severity-by-mode.md` for the full per-rule severity table across prototype / production / lift-and-shift modes.

## Rule sources (3 layers)

1. **RFD 0008 SQL coding standards** — 60+ rules across 11 categories (`cte`, `fmt`, `idiom`, `incr`, `jinja`, `model`, `naming`, `perf`, `security`, `test`, `version`). [RFD 0008 — SQL & Databricks coding standards (forthcoming — see `docs/superpowers/specs/2026-05-14-dplc-build-skills-design.md` for the canonical rule list)]
2. **dbt-project-evaluator gaps** — rules from the package's 6 categories (Modeling / Testing / Documentation / Structure / Performance / Governance) that RFD 0008 doesn't cover: DAG fanout, Source Fanout, Rejoining of Upstream, Public-without-contract, Test Coverage thresholds, Documentation Coverage thresholds. See `references/dpe-categorical-rules.md` for the full rule set with "what it checks / when it matters / how Catalyst applies it" detail.
3. **Capital Group pattern implementations** — vendor-renameable patterns (source wrapper, bitemporal-incremental, audit columns, checkpoint table, surrogate key, audit-column injection). See `references/pattern-*.md` for each pattern's intent + macro signature contract + concrete impl examples.

## Absorbed analytics-engineering body of knowledge

`references/absorbed-*.md` contains the dbt-labs `using-dbt-for-analytics-engineering` skill's reference files (planning models, discovering data, writing tests, debugging errors, evaluating impact, writing documentation, managing packages) absorbed under Apache 2.0. Read these when you need deep guidance on a specific dbt activity.

## How skills consume this

- `/setup-dbt-project` reads it once for `.sqlfluff` rule selection + `dbt_project.yml` defaults.
- `/dplc-build` model-authoring step reads it before invoking authoring leaves.
- `/source-aligned`, `/domain-aligned`, `/consumer-aligned` (existing) compose it during model generation.

## Mode-dependent fallbacks

When a DPLC artifact is absent (`data-model.md` missing → materialization choice), fall back to:
- staging → `view`
- intermediate → `view` or `ephemeral`
- marts → `table` (or `incremental` if profiling-reported row count > 10M)

See the per-artifact priority table in `references/rule-severity-by-mode.md`.
