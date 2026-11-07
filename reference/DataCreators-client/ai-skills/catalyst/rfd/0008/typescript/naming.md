# TS-NAMING: Naming

Identifier casing and file naming conventions.

## TS-NAMING-001 — Identifier casing per table

**Severity:** error
**Since:** v0.1.0
**Linter:** `@typescript-eslint/naming-convention`

**Decision.** Use the casing in this table:

| Item | Convention | Example |
|------|-----------|---------|
| Interfaces | `PascalCase` | `UserProfile` |
| Type aliases | `PascalCase` | `ApiResponse` |
| Enums | `PascalCase` | `OrderStatus` |
| Enum members | `PascalCase` | `OrderStatus.Pending` |
| Components | `PascalCase` | `DataTable` |
| Hooks | `camelCase` with `use` prefix | `useTableData` |
| Functions | `camelCase` | `fetchProfile` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| Variables | `camelCase` | `rowCount` |
| Type parameters | `T` or `PascalCase` | `T`, `TResponse` |
| Private fields | `#` prefix (ES private) | `#cache` |

## TS-NAMING-002 — File naming

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** File naming by content type:

- Components: `PascalCase.tsx` — `UserProfile.tsx`
- Utilities: `camelCase.ts` — `formatDate.ts`
- Tests: `{name}.test.ts(x)` — `UserProfile.test.tsx`
- Types: `{name}.types.ts` — `api.types.ts`

## TS-NAMING-003 — Hooks prefixed with `use`

**Severity:** error
**Since:** v0.1.0
**Linter:** `react-hooks/rules-of-hooks`

**Decision.** Custom hooks start with `use` and follow camelCase.

## TS-NAMING-004 — No `I` prefix on interfaces

**Severity:** error
**Since:** v0.1.0
**Linter:** `@typescript-eslint/naming-convention`

**Decision.** TypeScript interfaces don't use `I` as a prefix.

**Why.** That convention is C#. The Airbnb guide forbids it.

## TS-NAMING-005 — No `Enum` suffix on enums

**Severity:** error
**Since:** v0.1.0
**Linter:** `@typescript-eslint/naming-convention`

**Decision.** Enums are named for the concept, not the syntax: `Status`,
`OrderPhase`, `Severity`.

## TS-NAMING-006 — Boolean variables use `is`/`has`/`should`

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Boolean variables and properties read as predicates:
`isLoading`, `hasError`, `shouldUpdate`.

## TS-NAMING-007 — No generic standalone names

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Avoid `data`, `info`, `temp`, `item`, `stuff`, `result`,
`value` as standalone variable names.

**Exception.** Higher-order function callbacks (`items.map((x) => x.id)`),
loop indices, and generics.

### Type Safety
