# TS-IMPORT: Imports

Import grouping and named-export policy.

## TS-IMPORT-001 — Group import order

**Severity:** error
**Since:** v0.1.0
**Linter:** ESLint `import/order`

**Decision.** Five groups, separated by blank lines, alphabetized within
each:

1. React (`react`, `react-dom`)
2. Third-party packages (`@tanstack/react-query`, `zod`, `date-fns`)
3. Internal aliases (`@/components`, `@/hooks`, `@/utils`)
4. Relative imports (`./UserCard`, `../hooks/useAuth`)
5. Type-only imports inline via `import { type X }`

## TS-IMPORT-002 — Type imports use the `type` keyword

**Severity:** error
**Since:** v0.1.0
**Linter:** `@typescript-eslint/consistent-type-imports`

**Decision.** Type-only imports use `import type` or inline `import { type X }`.

**Why.** Type-only imports are erased at runtime. Without the `type`
keyword, the bundler may emit unnecessary side-effecting imports.

## TS-IMPORT-003 — Named exports only; no default exports

**Severity:** error
**Since:** v0.1.0
**Linter:** ESLint `import/no-default-export`

**Decision.** Use named exports. No `export default`.

**Why.** Default exports allow importers to choose any name, which
makes refactoring brittle and import names inconsistent.

**Exception.** Files where a framework requires a default export (Next.js
pages, dynamic imports). Document in a comment.

### Naming
