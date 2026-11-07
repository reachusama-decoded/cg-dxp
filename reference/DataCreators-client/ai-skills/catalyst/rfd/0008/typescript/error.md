# TS-ERROR: Error Handling

catch unknowns, domain error classes, error chaining.

## TS-ERROR-001 — `catch` variables are typed `unknown`

**Severity:** error
**Since:** v0.1.0
**Linter:** tsc `useUnknownInCatchVariables`

**Decision.** Catch parameters are `unknown`. Narrow before accessing
properties.

## TS-ERROR-002 — Never swallow errors silently

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Every catch block re-throws, returns a meaningful
fallback, or reports the error (logging, error boundary, toast).

## TS-ERROR-003 — Define domain error classes

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Application-specific failures extend a base `AppError`
class with a stable `code`, optional `statusCode`, and an optional
`cause`.

## TS-ERROR-004 — Chain errors with the `cause` option

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When wrapping an error, pass the original via the `cause`
option (ES2022). Don't discard the original.

### Testing
