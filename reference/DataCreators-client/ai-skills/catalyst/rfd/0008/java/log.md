# JV-LOG: Logging

SLF4J usage and structured logging.

## JV-LOG-001 — SLF4J only

**Severity:** error
**Since:** v0.1.0
**Linter:** Checkstyle, SpotBugs

**Decision.** SLF4J is the only logging facade. Never `java.util.logging`,
`System.out.println()`, `System.err.println()`, or Log4j API directly.

**Why.** Single facade lets the deployment swap implementations without
code changes.

## JV-LOG-002 — Parameterized messages, not concatenation

**Severity:** error
**Since:** v0.1.0
**Linter:** SpotBugs `LO_LOGGER_LOST_EXCEPTION_STACK_TRACE`

**Decision.** Use `{}` placeholders. Never `+`-concatenate strings in log
calls.

**Why.** Concatenation runs even when the level is suppressed; `{}`
placeholders only format if the level is enabled.

**Examples.**
```java
// ✓
logger.debug("Processing {} rows from {}", rowCount, table);

// ✗
logger.debug("Processing " + rowCount + " rows from " + table);
```

## JV-LOG-003 — Logger declaration `private static final`

**Severity:** error
**Since:** v0.1.0
**Linter:** Checkstyle

**Decision.** Declare loggers as `private static final
Logger logger = LoggerFactory.getLogger(ClassName.class);`.

**Why.** One logger instance per class, immutable, not exposed as API.

## JV-LOG-004 — Exception as last argument in log calls

**Severity:** error
**Since:** v0.1.0
**Linter:** SpotBugs

**Decision.** When logging an exception, pass it as the last argument.
SLF4J appends the full stack trace automatically.

**Examples.**
```java
// ✓
logger.error("Failed to profile {}.{}", schema, table, e);

// ✗ — no stack trace
logger.error("Failed to profile {}.{}: {}", schema, table, e.getMessage());
```

### Testing
