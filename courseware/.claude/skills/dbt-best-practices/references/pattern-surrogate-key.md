# Pattern: surrogate-key

## Intent

Generate a **stable, deterministic surrogate key** for each row by hashing a set of business key columns, so that joins across systems and history tables use a consistent, collision-resistant identifier that is independent of source system sequence numbers.

This is the recommended alternative to IDENTITY columns when the surrogate key must be reproducible from the source data (e.g., for idempotent re-runs, cross-repo joins, or CDC comparisons).

## Required behavior

A macro that:

1. Accepts a list of column expressions (business key columns, in a canonical order).
2. Returns a deterministic hash (SHA-256 or MD5 of the concatenated, null-safe string of the inputs).
3. Is null-safe: null inputs produce a consistent sentinel (e.g., hash of empty string or `'__null__'`), not `NULL`.
4. Is stable across dbt versions and Python/Databricks runtime upgrades (SHA-256 preferred over MD5 due to collision resistance; avoid hash functions whose output changes across runtime versions).

## Concrete implementations seen

- **Caspian (prototype):** `generate_surrogate_key_v3(column_list)` — wraps dbt's built-in `dbt_utils.generate_surrogate_key` but pins version 3 of the hash function to ensure stability across dbt-utils upgrades. Called via `{{ generate_surrogate_key_v3(['col_a', 'col_b']) }}` in a SELECT expression.
- **dbt-utils built-in:** `{{ dbt_utils.generate_surrogate_key(['col_a', 'col_b']) }}` — acceptable for greenfield teams that do not need version pinning. Note: the hash function used by `dbt_utils.generate_surrogate_key` changed in dbt-utils 1.0 (MD5 → SHA-256); ensure a consistent version is locked in `packages.yml`.
- **Databricks IDENTITY column alternative:** `id BIGINT GENERATED ALWAYS AS IDENTITY` — use when no natural business key exists AND the surrogate key does not need to be reproducible from source data. Document as PK in `schema.yml`.

## Discovery

`/setup-dbt-project` scans `macros/` for a macro whose name contains `surrogate_key` or whose body calls `dbt_utils.generate_surrogate_key` or `md5` / `sha2`.

If found, store the macro name in `.catalyst-build.yml#patterns.incremental-bitemporal.surrogate_key_macro`. If using `dbt_utils`, note the dbt-utils version pinned in `packages.yml` so the hash function is known.

## When skills use this

- `/domain-aligned` (existing) calls the surrogate-key macro when authoring dimension models to generate `dl_row_uid` (or team-renamed equivalent) as the PK.
- `pattern-bitemporal-incremental.md` relies on the surrogate-key macro to produce a stable row identifier for each history version (each SCD2 row gets a unique surrogate combining the business key + effective start date).
- Rule `SQL-TEST-001` (`unique` + `not_null` on every PK) applies to the surrogate key column — enforced in production mode.
