# fund_nav migration

Atlas ELT migration notes for the `fund_nav` dataset.

## Pattern

- Keep schema-change SQL files in `contract/migrations/`.
- Name migration files with the repository Flyway-style version prefix when a table change is introduced.
- Keep this note with the dataset so bundle and contract reviewers can find the migration context next to the artifacts.
