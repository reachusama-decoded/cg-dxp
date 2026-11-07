# JV-DOC: Documentation

Javadoc requirements and package-info.java.

## JV-DOC-001 — Javadoc on all public types

**Severity:** error
**Since:** v0.1.0
**Linter:** Checkstyle `MissingJavadocType`

**Decision.** All public classes, interfaces, enums, and records have
class-level Javadoc.

## JV-DOC-002 — Javadoc on all public and protected methods

**Severity:** error
**Since:** v0.1.0
**Linter:** Checkstyle `MissingJavadocMethod`

**Decision.** All public and protected methods have Javadoc.

## JV-DOC-003 — `@param`, `@return`, `@throws` for every parameter, non-void return, declared exception

**Severity:** error
**Since:** v0.1.0
**Linter:** Checkstyle

**Decision.** Document every parameter, every non-void return, and every
declared `throws` clause.

**Examples.**
```java
/**
 * Profiles a table's columns for data quality assessment.
 *
 * <p>Connects to the specified catalog and runs statistical profiling on
 * each column. For tables exceeding {@code sampleSize} rows, profiling
 * runs against a random sample to keep query time under 30 seconds.
 *
 * @param catalog    the Unity Catalog name (e.g., "investments_dev")
 * @param schema     the schema within the catalog
 * @param table      the table name to profile
 * @param sampleSize maximum rows to sample; use -1 for full scan
 * @return a {@link TableProfile} containing column-level statistics
 * @throws IllegalArgumentException if any argument is null or blank
 * @throws SchemaNotFoundException  if the specified schema does not exist
 * @throws DataProfilingException   if the profiling query times out
 */
public TableProfile profile(String catalog, String schema, String table, int sampleSize) {
    // ...
}
```

## JV-DOC-004 — First sentence is a third-person summary

**Severity:** warning
**Since:** v0.1.0
**Linter:** Checkstyle

**Decision.** First Javadoc sentence is third-person declarative
("Returns the column statistics") not imperative ("Return the column
statistics").

## JV-DOC-005 — No `@author` tags

**Severity:** error
**Since:** v0.1.0
**Linter:** Checkstyle

**Decision.** Don't write `@author` tags. Version control records
authorship.

## JV-DOC-006 — `package-info.java` for every package

**Severity:** warning
**Since:** v0.1.0
**Linter:** Checkstyle

**Decision.** Every package has a `package-info.java` summarizing its
purpose.

**Examples.**
```java
/**
 * Core profiling logic for table and column-level data quality assessment.
 *
 * <p>This package contains the profiling engine, statistical calculators,
 * and result data types. It does not contain I/O — database access is
 * injected via the {@link com.catalyst.profiler.datasource.DataSource}
 * interface.
 */
package com.catalyst.profiler.core;
```

### Immutability
