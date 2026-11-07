# TODO — Data Quality Skill Coverage

**Created:** 2026-05-15
**Surfaced by:** /generate-dag design review

> **Update (2026-08-05, AICAT-281):** the **design-time authoring** gap is now
> partly closed. `/data-quality-controls-plan` (Phase-3 leaf) proposes a focused
> set of DQ controls from profiling + requirements, aligned to the EDGC **DQ
> Rule Patterns Guidance** (named patterns, STOP/WARN actions, DQ Next/DQF
> checks), and feeds `data-contract` §4. A DQ **RACI/DQMS** artifact and a
> proposed **§4 DQ Dimension column** are routed to **RFD 0019** (prediscussion)
> rather than shipped. The **runtime/enforcement** family below
> (`/generate-dq-rules`, `/run-dq-checks`, `/dq-threshold-policy`,
> `/dq-incident-handler`) is still open — the controls plan's DQ Next checks are
> the natural input to it. Note the RFD 0009 gap: the ODCS/Data-Contract
> Standard is referenced repo-wide but not yet written.

## Problem

DQ (data quality) coverage across Catalyst skills is sparse and inconsistent:

| What exists | What it does | What it doesn't |
|---|---|---|
| `/data-quality-sign-off` | Phase 5 artifact — produces a DQ sign-off doc | Doesn't author DQ rules, doesn't run checks |
| `<dataset>.dq.yml` emitted by `/generate-dag` | YAML structure for DQ checks | No enforcement engine; structure not validated; not derived from data contract DQ rules |
| `skills/dbt-best-practices/references/dpe-categorical-rules.md` | Mentions DQ thresholds (test coverage, documentation coverage) | Reference doc only; no skill emits these as enforced policy |
| dbt tests via `schema.yml` (existing `/source-aligned`, `/domain-aligned`, etc.) | unique / not_null / accepted_values on columns | Limited to dbt's built-in test types; no row-level invariants, no cross-table checks |

## What's missing

1. **`/generate-dq-rules`** — read a data contract's `data_quality:` section and emit a runnable `.dq.yml` against a DQ engine (Great Expectations / Soda / Caspian DQF / dbt-data-tests).
2. **`/run-dq-checks`** — invoke a DQ runner against a target table; record results to a DQ history table; emit Datadog metrics on failures.
3. **`/dq-threshold-policy`** — define environment-aware thresholds (e.g., `null_rate < 1% in prod`, `< 5% in dev`).
4. **`/dq-incident-handler`** — what happens when a DQ check fails? Block the DAG? Alert? Quarantine the partition?

## Why this matters

- RFD 0011 §9 (Testing) calls for DQ checks but Catalyst doesn't have a skill that *authors* them.
- The data contract template has a DQ rules section but no skill *consumes* it.
- The `.dq.yml` file `/generate-dag` emits is structurally aligned with no specific engine.
- Without a DQ skill set, teams default to ad-hoc dbt tests + manual review, which scales poorly.

## Adjacent open questions

- **DQ engine choice** — Great Expectations, Soda, Caspian DQF, dbt-data-tests, or a thin Catalyst wrapper around several? Open question; depends on what Capital Group's platform team standardizes on.
- **RFD-worthy?** A DQ skill family probably warrants an RFD (similar weight to RFD 0011). Could be RFD 0012 (DAG Standards is already 0011; numbering pending).
- **Phase 4 vs Phase 5** — DQ rule authoring happens during build (Phase 4) but checks run during validate (Phase 5) and operate. Spans phases.

## What to do next

1. **Audit:** read every Catalyst skill that mentions "data quality", "DQ", "dq.yml", "data tests", or "expectations" — get a complete picture of current coverage.
2. **Engine decision:** confirm with platform team which DQ engine Catalyst should target.
3. **Draft RFD or design spec:** scope a DQ skill family (probably 3–4 skills similar to the `/generate-dag` set).
4. **Plan + execute:** standard Catalyst brainstorm → spec → plan → build flow.

## Cross-references

- `/generate-dag` spec at `docs/superpowers/specs/2026-05-15-generate-dag-design.md` (OQ-6 references this TODO).
- `skills/data-quality-sign-off/SKILL.md` (existing Phase 5 artifact skill).
- `skills/dbt-best-practices/references/dpe-categorical-rules.md` (DQ-adjacent generation-time guidance).
- RFD 0011 §9 — Testing directive citing DQ checks.
