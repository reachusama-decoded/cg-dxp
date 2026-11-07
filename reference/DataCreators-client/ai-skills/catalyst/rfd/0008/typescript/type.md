# TS-TYPE: Types

Strict type safety: any, non-null, narrowing, satisfies, discriminated unions.

## TS-TYPE-001 — `strict: true` + extended strictness

**Severity:** error
**Since:** v0.1.0
**Linter:** tsc

**Decision.** Every `tsconfig.json` enables:
- `strict: true`
- `noUncheckedIndexedAccess: true`
- `exactOptionalPropertyTypes: true`
- `verbatimModuleSyntax: true`
- `noPropertyAccessFromIndexSignature: true`

**Why.** Each flag closes a specific footgun:
- `noUncheckedIndexedAccess`: array/record indexing returns `T | undefined`,
  catching out-of-bounds access at compile time.
- `exactOptionalPropertyTypes`: distinguishes `{ x?: string }` (may be
  missing) from `{ x: string | undefined }`.
- `verbatimModuleSyntax`: forces `import type` so type-only imports are
  erased at runtime.

## TS-TYPE-002 — Never `any`; use `unknown` and narrow

**Severity:** error
**Since:** v0.1.0
**Linter:** `@typescript-eslint/no-explicit-any`

**Decision.** Never `any`. Use `unknown` for type-erased values and
narrow with type guards.

**Exception.** In utility files where the boundary genuinely doesn't
have a stable type, suppress with `// eslint-disable-next-line` and a
comment explaining why.

## TS-TYPE-003 — Never non-null assertion `!`

**Severity:** error
**Since:** v0.1.0
**Linter:** `@typescript-eslint/no-non-null-assertion`

**Decision.** Don't use the `!` operator. Narrow, optional-chain, or
nullish-coalesce instead.

## TS-TYPE-004 — Always narrow `unknown` before use

**Severity:** error
**Since:** v0.1.0
**Linter:** `@typescript-eslint/no-unsafe-*`

**Decision.** `unknown` values are narrowed via type guards,
`instanceof`, `typeof`, or a discriminated union before access.

## TS-TYPE-005 — `satisfies` for type validation without widening

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `satisfies T` to validate a value's type while
preserving the narrowest inferred type.

## TS-TYPE-006 — `as const` for literal tuples and objects

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Add `as const` when an array or object should be a
readonly tuple of literal types.

## TS-TYPE-007 — Discriminated unions over optional fields for mutually exclusive state

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When state has multiple modes with different fields per
mode, use a discriminated union rather than optional fields.

## TS-TYPE-008 — Template literal types for string constraints

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use template literal types when a string has a known
shape.

### React
