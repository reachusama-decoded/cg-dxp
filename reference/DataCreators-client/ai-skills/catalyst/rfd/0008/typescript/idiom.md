# TS-IDIOM: Idioms

Boolean expressions, ternaries, useReducer, zod validation.

## TS-IDIOM-001 — Logical AND with explicit boolean

**Severity:** error
**Since:** v0.1.0
**Linter:** `@typescript-eslint/strict-boolean-expressions`

**Decision.** When using `&&` for conditional rendering, the left side
is an explicit boolean. Never a number, string, or object.

**Why.** `0 && X` renders `0`. Empty string short-circuits. The bugs are
silent.

## TS-IDIOM-002 — No nested ternaries

**Severity:** warning
**Since:** v0.1.0
**Linter:** ESLint `no-nested-ternary`

**Decision.** Never nest ternary expressions. Use early returns or a
switch/lookup function.

## TS-IDIOM-003 — `useReducer` with discriminated union actions

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When state has multiple sub-values or transitions, use
`useReducer` with a discriminated union for the action type. Combined
with `switch-exhaustiveness-check`, the compiler verifies you handle
every action.

## TS-IDIOM-004 — `zod` for runtime validation of external data

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Validate API responses, URL params, form input, and other
external data with `zod` (or another runtime validator). The validator
output type drives the rest of the code.

## TS-IDIOM-005 — Compound components for related UI

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Group related UI primitives into a compound component
(`Tabs.Tab`, `Tabs.Panel`) when they share context.

### Async
