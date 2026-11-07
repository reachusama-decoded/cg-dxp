# TS-TEST: Testing

Vitest, React Testing Library, MSW, snapshot policy.

## TS-TEST-001 — Vitest framework

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Tests use Vitest. No Jest in new projects.

## TS-TEST-002 — React Testing Library for components

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Component tests use React Testing Library. No Enzyme. No
shallow rendering.

## TS-TEST-003 — Test user behavior, not implementation

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Query elements by role, label, and visible text. Use
`data-testid` only as a last resort. Never query by class name or
component internals.

## TS-TEST-004 — MSW for API mocking

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Mock APIs with Mock Service Worker (MSW). Never mock
`fetch` or `axios` directly.

**Why.** MSW intercepts at the network level, exercising the real fetch
code. Direct mocks bypass the code under test.

## TS-TEST-005 — Tests colocated with `{name}.test.tsx`

**Severity:** error
**Since:** v0.1.0
**Linter:** Vitest discovery

**Decision.** Tests live next to the source file as
`{name}.test.ts(x)`.

## TS-TEST-006 — No snapshot tests for component output

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** No `toMatchSnapshot` for rendered components.

**Why.** Snapshots are brittle, produce meaningless diffs, and
encourage `--updateSnapshot` without review.

**Exception.** Pure data structures (e.g., normalized AST output) where
the snapshot is the contract.

## TS-TEST-007 — 80% coverage on core business logic

**Severity:** warning
**Since:** v0.1.0
**Linter:** Vitest coverage

**Decision.** Coverage greater than or equal to 80% on core business
logic. UI components are tested by user-behavior tests rather than line
coverage.

### Security
