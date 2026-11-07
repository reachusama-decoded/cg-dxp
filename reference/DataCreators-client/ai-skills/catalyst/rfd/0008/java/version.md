# JV-VERSION: Version

Java version policy and Azul Zulu OpenJDK selection.

## JV-VERSION-001 — New projects use Azul Zulu OpenJDK 21 LTS

**Severity:** error
**Since:** v0.1.0
**Linter:** Gradle toolchain enforcement (`vendor = JvmVendorSpec.AZUL`)

**Decision.** New projects target Java 21 on the Azul Zulu OpenJDK
distribution. Use sealed classes, records, text blocks, switch
expressions, pattern matching, virtual threads, and sequenced collections
where appropriate.

**Why.** 21 is the current LTS. Earlier features (records, sealed, switch
expressions) materially reduce boilerplate and bugs. Azul Zulu is the
CG-standard OpenJDK distribution — Oracle JDK requires a commercial
license for production use.

## JV-VERSION-002 — Java 17 acceptable; must target 21 on next major

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Existing Java 17 projects may stay on 17 but must target 21 on
their next major update.

## JV-VERSION-003 — Java 11 must move to 17, then 21

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Java 11 projects must target Java 17 within the next quarter
and Java 21 on the following major update.

## JV-VERSION-004 — No Java 8 idioms

**Severity:** error
**Since:** v0.1.0
**Linter:** Checkstyle, SpotBugs

**Decision.** No `Date`/`Calendar` (use `java.time`). No raw types. No
anonymous inner classes where a lambda suffices. No `Vector`, `Hashtable`,
or `Stack`.

**Why.** These are legacy APIs with known bugs and replacements that are
strictly better.

### Imports
