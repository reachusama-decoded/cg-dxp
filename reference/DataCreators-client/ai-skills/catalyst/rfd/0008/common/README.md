# Common Standards

This directory holds standards and supporting design references that span
multiple languages or platforms — patterns where the same rule applies
regardless of the implementation language.

## Contents

| File | Topic |
|------|-------|
| [`bi-temporal.md`](bi-temporal.md) | Bi-temporal table design patterns for foundation data models. |

## Future cross-cutting rules

Cross-language rules that surface in code (rather than design references)
will land here as `COMMON-{CATEGORY}-{NNN}` rules — for example a single
`COMMON-LOG-001` for the structured-logging shape that Python, Rust, Java,
and TypeScript all follow. Today these live as language-specific rules in
each language's `log.md` (or equivalent). Promotion to `COMMON-*` happens
when the rule body is genuinely identical across languages and the
language-specific rules can defer to it.

## Why this exists

The per-language guides cover idiomatic implementation in each language.
Some patterns — bi-temporal modeling, identity formats, error envelopes,
audit trail shapes — are language-agnostic. Documenting them once here
means the language guides can reference rather than duplicate.
