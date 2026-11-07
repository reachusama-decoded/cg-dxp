# SQL / dbt Coding Standards

## Governing Authority

These standards are derived from and comply with:

- [dbt Style Guide](https://docs.getdbt.com/best-practices/how-we-style/0-how-we-style-our-dbt-projects)
- [SQLFluff Documentation](https://docs.sqlfluff.com/en/stable/)
- [Databricks SQL Language Reference](https://docs.databricks.com/en/sql/language-manual/index.html)
- [dbt Best Practices](https://docs.getdbt.com/best-practices)
- [Unity Catalog Documentation](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)

Where this document is silent, the dbt Style Guide applies.

## Rule Format

Same shape as the rest of RFD 0008:

```
### SQL-{CATEGORY}-{NNN} — one-line directive

**Severity:** error | warning | advisory
**Since:** v0.1.0
**Linter:** SQLFluff rule codes / advisory

**Decision.** What to do.
**Why.** Rationale.
**Exception.** When the rule does not apply, or "None."
**Examples.** good / bad code.
```

Categories: `VERSION`, `FMT`, `NAMING`, `CTE`, `MODEL`, `INCR`, `TEST`,
`JINJA`, `IDIOM`, `PERF`, `SECURITY`.

## Tooling

### Linter and Formatter: SQLFluff

SQLFluff is the **only** SQL linter and formatter. Do not use sqlfmt,
sql-formatter, or IDE-specific formatters.

```ini
# .sqlfluff
[sqlfluff]
dialect = databricks
templater = dbt
max_line_length = 100
indent_unit = space
tab_space_size = 4
large_file_skip_byte_limit = 25000

[sqlfluff:templater:dbt]
project_dir = ./
profiles_dir = ./
profile = default
target = dev

[sqlfluff:indentation]
indent_unit = space
tab_space_size = 4
indented_joins = false
indented_ctes = false
indented_on_contents = true
indented_using_on = true

[sqlfluff:layout:type:comma]
spacing_before = touch
line_position = trailing

[sqlfluff:rules:capitalisation.keywords]
capitalisation_policy = lower

[sqlfluff:rules:capitalisation.identifiers]
capitalisation_policy = lower

[sqlfluff:rules:capitalisation.functions]
extended_capitalisation_policy = lower

[sqlfluff:rules:capitalisation.literals]
capitalisation_policy = lower

[sqlfluff:rules:capitalisation.types]
extended_capitalisation_policy = lower

[sqlfluff:rules:aliasing.table]
aliasing = explicit

[sqlfluff:rules:aliasing.column]
aliasing = explicit

[sqlfluff:rules:aliasing.length]
min_alias_length = 3

[sqlfluff:rules:convention.select_trailing_comma]
select_clause_trailing_comma = require

[sqlfluff:rules:convention.casting_style]
preferred_type_casting_style = shorthand

[sqlfluff:rules:references.consistent]
single_table_references = unqualified

[sqlfluff:rules:references.keywords]
quoted_identifiers_policy = none

[sqlfluff:rules:layout.long_lines]
ignore_comment_lines = true
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml (relevant excerpt)
repos:
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: 3.2.5
    hooks:
      - id: sqlfluff-lint
        args: [--dialect, databricks]
        additional_dependencies: ["dbt-databricks>=1.8"]
      - id: sqlfluff-fix
        args: [--dialect, databricks, --force]
        additional_dependencies: ["dbt-databricks>=1.8"]
```

---

## Rule index

Rules are split by category. Each category file has the rules in numeric order.

- [`cte.md`](cte.md) — **CTE Patterns** (7 rules). CTE patterns: import CTEs, single-step rule, final CTE convention.
- [`fmt.md`](fmt.md) — **Formatting** (8 rules). Keyword case, indentation, joins, where, group by, case formatting.
- [`idiom.md`](idiom.md) — **Idioms** (6 rules). Anti-pattern inverses: select *, subqueries, OR joins, distinct fixes.
- [`incr.md`](incr.md) — **Incremental Models** (6 rules). Incremental materialization, merge strategy, lookback windows.
- [`jinja.md`](jinja.md) — **Jinja and Macros** (6 rules). Macro discipline, template-vs-code separation, env_var policy.
- [`model.md`](model.md) — **Model Organization** (8 rules). Model organization, ref/source, schema YAML, staging discipline.
- [`naming.md`](naming.md) — **Naming** (4 rules). Model prefixes, source naming, column conventions, test naming.
- [`perf.md`](perf.md) — **Performance** (6 rules). Partition pruning, Z-ORDER, expensive operations, window functions.
- [`security.md`](security.md) — **Security** (4 rules). Hardcoded secrets, PII in fixtures, dbt var validation, UC RLS.
- [`test.md`](test.md) — **Testing** (6 rules). Generic tests, singular tests, dbt unit tests, severity policy.
- [`version.md`](version.md) — **Version** (3 rules). dbt, Databricks Runtime, and SQLFluff version policy.
