# TS-VERSION: Version

TypeScript, ECMAScript, React, and Node.js versions.

## TS-VERSION-001 — TypeScript 5.x with all strict flags

**Severity:** error
**Since:** v0.1.0
**Linter:** tsc

**Decision.** TypeScript 5.x. Every project's `tsconfig.json` enables
`strict: true` plus the additional safety flags listed in *Tooling*. No
opt-outs.

**Why.** Strict mode catches an entire class of runtime errors at compile
time. Half-strict is unsupportable.

## TS-VERSION-002 — ECMAScript ES2022 minimum

**Severity:** error
**Since:** v0.1.0
**Linter:** tsc target

**Decision.** Target ES2022. Use top-level `await`, `Object.hasOwn`,
`Array.at()`, and error `cause` freely.

## TS-VERSION-003 — React 18+

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Frontend projects use React 18 or later. Use concurrent
features (Suspense, `useTransition`, `useDeferredValue`) where
appropriate.

## TS-VERSION-004 — Node.js 20 LTS+

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Backend services and CLI tooling target Node.js 20 LTS or
later.

## TS-VERSION-005 — ESM only; no CommonJS in new code

**Severity:** error
**Since:** v0.1.0
**Linter:** ESLint, tsc `verbatimModuleSyntax`

**Decision.** All new modules use `import`/`export`. No `require()`, no
`module.exports`.

**Exception.** Existing CommonJS files migrated incrementally.

### Imports
