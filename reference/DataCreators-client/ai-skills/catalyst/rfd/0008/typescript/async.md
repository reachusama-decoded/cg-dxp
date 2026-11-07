# TS-ASYNC: Async

async/await, floating promises, parallel patterns.

## TS-ASYNC-001 — `async`/`await` only

**Severity:** error
**Since:** v0.1.0
**Linter:** `@typescript-eslint/promise-function-async`

**Decision.** Use `async`/`await`. No raw `.then()`/`.catch()` chains.

## TS-ASYNC-002 — No floating promises

**Severity:** error
**Since:** v0.1.0
**Linter:** `@typescript-eslint/no-floating-promises`

**Decision.** Every promise is `await`ed, returned, or explicitly voided
with `void`.

## TS-ASYNC-003 — `Promise.all` for parallel; `Promise.allSettled` for independent failures

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `Promise.all` when all promises must succeed. Use
`Promise.allSettled` when failures are tolerable per-promise.

### Error Handling
