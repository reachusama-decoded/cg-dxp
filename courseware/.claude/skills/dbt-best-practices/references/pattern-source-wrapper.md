# Pattern: source-wrapper

## Intent

Parameterize the catalog and schema in `{{ source(...) }}` calls so the same dbt project compiles against multiple Databricks catalogs (dev / qa / prod) without code edits.

## Required behavior

A macro that:

1. Takes 3 arguments: `(catalog, schema, table)`.
2. Returns a `{{ source(...) }}` reference wrapped to use the catalog parameter.
3. Reads `var('caspian_catalog')` (or the team-renamed catalog var) for the catalog name.

## Concrete implementations seen

- **Caspian (prototype):** `cspn_source(catalog, schema, table)` reading `var('caspian_catalog')`.
- **Greenfield (recommended for new teams):** plain `{{ source(...) }}` if catalog parameterization isn't needed; otherwise a team-namespaced macro following Caspian's signature.

## Discovery

`/setup-dbt-project` scans `macros/` for a macro matching:
- function name ending in `_source`
- 3 positional args
- emits `{{ source(catalog ~ "." ~ schema, table) }}` or equivalent

If found, store the macro name in `.catalyst-build.yml#patterns.source-wrapper.macro`. If not, prompt the user.

## When skills use this

- `/source-aligned` (existing) emits `{{ <macro>(var('<catalog-var>'), '<schema>', '<table>') }}` when authoring staging models.
