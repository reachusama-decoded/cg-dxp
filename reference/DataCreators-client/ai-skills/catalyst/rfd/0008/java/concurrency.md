# JV-CONCURRENCY: Concurrency

java.util.concurrent and thread-safety rules.

## JV-CONCURRENCY-001 — `synchronized` on public methods only when documented thread-safe

**Severity:** warning
**Since:** v0.1.0
**Linter:** SpotBugs

**Decision.** Don't add `synchronized` to a public method unless the
class is explicitly documented as thread-safe.

## JV-CONCURRENCY-002 — Prefer `java.util.concurrent`

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `ConcurrentHashMap`, `AtomicReference`, `ReentrantLock`,
`ExecutorService` rather than hand-rolled synchronization.

**Why.** Effective Java Items 78-84.

## JV-CONCURRENCY-003 — Always shut down `ExecutorService`

**Severity:** error
**Since:** v0.1.0
**Linter:** SpotBugs

**Decision.** `ExecutorService` instances are shut down in a
try-finally or try-with-resources (Java 19+ implements `AutoCloseable`).

## JV-CONCURRENCY-004 — Never `Thread.stop`, `suspend`, or `resume`

**Severity:** error
**Since:** v0.1.0
**Linter:** SpotBugs

**Decision.** These methods are deprecated and unsafe.

## JV-CONCURRENCY-005 — `volatile` or `AtomicBoolean` for shared flags

**Severity:** error
**Since:** v0.1.0
**Linter:** SpotBugs

**Decision.** Flags shared between threads are `volatile` or wrapped in
`AtomicBoolean`. Plain `boolean` is not safe.

### Security
