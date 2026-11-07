# SQL-SECURITY: Security

Hardcoded secrets, PII in fixtures, dbt var validation, UC RLS.

## SQL-SECURITY-001 — No hardcoded secrets in SQL files

**Severity:** error
**Since:** v0.1.0
**Linter:** gitleaks + advisory

**Decision.** Never hardcode tokens, passwords, or connection strings in
`.sql` files. Use `env_var()` in `profiles.yml` only.

## SQL-SECURITY-002 — No PII in test fixtures

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Unit test `given` rows use synthetic data only, never real
customer data.

**Why.** Test fixtures live in version control and propagate everywhere
the repo goes.

## SQL-SECURITY-003 — Validate `var()` inputs from user-controlled sources

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** If a dbt model accepts `var()` inputs that could come from
user-controlled sources, validate the value in a macro before
interpolating into SQL.

**Why.** Otherwise the dbt CLI becomes a SQL-injection vector.

## SQL-SECURITY-004 — Row-level security via Unity Catalog, not in dbt models

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use Unity Catalog row filters and column masks for
row-level security. Don't build security logic into dbt models.

**Why.** UC enforces RLS at the catalog layer regardless of which tool
queries the data. Logic embedded in dbt is bypassable.
