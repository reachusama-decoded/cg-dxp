# TS-REACT: React

Functional components, hooks, server state, rendering rules.

## TS-REACT-001 — Functional components only

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** No class components. No `React.Component`,
`React.PureComponent`, or lifecycle methods.

## TS-REACT-002 — Props interface required

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Every component declares a Props interface (or type alias)
colocated with the component.

## TS-REACT-003 — Composition over prop drilling beyond 2 levels

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When a prop passes through more than two component levels,
use Context, composition (children/render props), or a state management
library.

## TS-REACT-004 — Derive state; never `useEffect`-sync derived state

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** If a value can be computed from props or other state,
compute it inline. Never use `useEffect` to mirror derived state into
`useState`.

## TS-REACT-005 — Early returns for conditional rendering

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use guard clauses at the top of the component for
loading/error states. Don't deeply nest ternaries.

## TS-REACT-006 — Extract reusable logic into custom hooks

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Logic shared between two or more components is extracted
into a custom hook with a typed return shape.

## TS-REACT-007 — Type `useState` parameter when not inferable

**Severity:** error
**Since:** v0.1.0
**Linter:** tsc

**Decision.** Pass an explicit type parameter to `useState` when the
initial value doesn't fully determine the type.

## TS-REACT-008 — `useCallback` only when needed

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `useCallback` only when the callback is passed to a
memoized child or used in a dependency array. Don't wrap every handler.

**Why.** Unnecessary `useCallback` adds noise without benefit.

## TS-REACT-009 — TanStack Query for server state

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Server data is managed by TanStack Query (`useQuery`,
`useMutation`). Never manage server state with `useState` + `useEffect`.

**Why.** Manual fetch logic recreates caching, deduplication, refetch,
and stale/fresh handling badly. TanStack Query gets these right.

## TS-REACT-010 — Stable unique keys; never array index

**Severity:** error
**Since:** v0.1.0
**Linter:** ESLint `react/no-array-index-key`

**Decision.** Always use a stable unique identifier as the React key.
Never use array index. Don't generate keys at render time.

## TS-REACT-011 — Type event handlers explicitly

**Severity:** error
**Since:** v0.1.0
**Linter:** tsc

**Decision.** Event handlers declare their event type
(`React.ChangeEvent<HTMLInputElement>`,
`React.FormEvent<HTMLFormElement>`,
`React.KeyboardEvent<HTMLInputElement>`).

## TS-REACT-012 — Error boundaries wrap routes and async-loading components

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `react-error-boundary`. Wrap route-level components
and any component that loads async data.

### Idioms
