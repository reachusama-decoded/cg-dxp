# Seed Data Rules (S1–S17)

Apply ALL rules to every test case. Violations cause silent empty output.

| Rule | Summary |
|------|---------|
| S1 | Include EVERY WHERE / JOIN ON / BETWEEN / subquery filter column in seed rows — NULL in a filter column eliminates all rows. |
| S2 | For `BETWEEN dl_business_start_date AND dl_business_end_date` joins, the fact table's `position_date` MUST fall within the dimension's date range. |
| S3 | FK=PK ON condition values MUST match exactly across seed tables. |
| S4 | `dl_current_indicator='Y'` for expected-output rows; `'N'` only for exclusion scenarios. |
| S5 | Use the SAME `dl_system_start_timestamp` across all rows of a source table so `MAX()` subquery filters match. |
| S6 | `pandas_query` expressions MUST use EXACT output column names from the Output Columns table. |
| S7 | For zero-output scenarios set `pandas_query` to `"False"`. |
| S8 | Trace the full CTE dependency chain — every source table must have rows passing ALL intermediate WHERE / JOIN / BETWEEN filters; an unseeded intermediate table means zero output. |
| S9 | When a source table appears in multiple CTEs, include ALL columns needed across ALL usages in one seed entry. |
| S10 | Never use sentinel/magic values that trigger exclusion flags in happy-path seeds. |
| S11 | When targeting a CASE WHEN branch, ensure ALL earlier WHEN conditions evaluate FALSE for seeded rows (SQL short-circuits at first match). |
| S12 | For CASE WHEN results feeding a downstream WHERE filter, verify the ELSE branch doesn't produce the excluded value for happy-path seeds. |
| S13 | Every column in any CTE's GROUP BY or SELECT from seeded tables must be present (non-NULL) — NULL FK columns cause all downstream INNER JOINs to return 0 rows. |
| S14 | For `WHERE COALESCE(a + b + ..., 0) <> 0`: ALL LEFT-JOINed value columns in the arithmetic must be non-NULL — seed all dimension JOINs. |
| S15 | NEVER seed a CTE-derived table — only seed actual Jinja source tables (`{{schema}}.{{'table'}}` references). |
| S16 | Never use reserved/excluded portfolio UIDs (e.g. 402325, 463906) in happy-path seeds — use neutral UIDs like `99999`. |
| S17 | When seeding INNER JOIN dimension tables, include ALL columns the SQL reads from that alias — NULL currency-code columns cause rows to disappear from aggregates. |
