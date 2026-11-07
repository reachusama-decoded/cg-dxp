# TS-SECURITY: Security

XSS, dynamic code, auth tokens, input validation, URL encoding.

## TS-SECURITY-001 — Never render raw HTML from external sources

**Severity:** error
**Since:** v0.1.0
**Linter:** ESLint `react/no-danger`

**Decision.** Don't bypass JSX escaping. Don't use React's raw-HTML
injection prop with external content.

**Why.** JSX escaping is the primary XSS defense.

**Exception.** When unavoidable, sanitize with DOMPurify and document
the business justification in a comment.

## TS-SECURITY-002 — No dynamic code execution

**Severity:** error
**Since:** v0.1.0
**Linter:** ESLint `no-eval`, `no-implied-eval`, `no-new-func`

**Decision.** No `eval`. No `Function()` constructor. No
`setTimeout(string)`. No dynamic code generation from user input.

## TS-SECURITY-003 — Auth tokens in httpOnly cookies; never localStorage

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Store JWTs, session tokens, and API keys in httpOnly
cookies. Never `localStorage`, `sessionStorage`, or
JavaScript-accessible cookies.

**Why.** httpOnly is invisible to XSS payloads. localStorage is not.

## TS-SECURITY-004 — Validate external input with `zod` at the API boundary

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** API responses, URL params, form input, and any other
external data are validated by a `zod` schema before use. Internal code
operates on the validated type.

**Why.** Without runtime validation, the TypeScript type is an
unverified claim. A malformed payload becomes a `TypeError` at runtime.

## TS-SECURITY-005 — Encode user input in URLs

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `encodeURIComponent` or the `URL` API. Never
interpolate user input into URLs as raw strings.

## TS-SECURITY-006 — `rel="noopener noreferrer"` on external links

**Severity:** error
**Since:** v0.1.0
**Linter:** ESLint `react/jsx-no-target-blank`

**Decision.** External links with `target="_blank"` set
`rel="noopener noreferrer"`.

**Why.** Without `noopener`, the linked page can manipulate
`window.opener`. Without `noreferrer`, referrer headers leak.
