# Java Coding Standards

## Governing Authority

These standards are derived from and comply with:

- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
- [Effective Java, 3rd Edition](https://www.oreilly.com/library/view/effective-java/9780134686097/) (Joshua Bloch)
- [OpenJDK 21 API Documentation](https://openjdk.org/projects/jdk/21/)
- [Azul Zulu OpenJDK Documentation](https://docs.azul.com/core/)
- [SEI CERT Oracle Coding Standard for Java](https://wiki.sei.cmu.edu/confluence/display/java/SEI+CERT+Oracle+Coding+Standard+for+Java)
- [OWASP Java Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Java_Security_Cheat_Sheet.html)
- [Apache Spark Java API Documentation](https://spark.apache.org/docs/latest/api/java/)

Where this document is silent, the Google Java Style Guide applies.

## JDK Distribution

Capital Group standardizes on **Azul Zulu OpenJDK** for all Java workloads —
local development, CI builds, and production runtimes. Do not use Oracle
JDK (commercial license required for production), Amazon Corretto, Eclipse
Temurin, or any other distribution without an explicit RFD.

```kotlin
// build.gradle.kts — pin the toolchain to Azul Zulu
java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
        vendor = JvmVendorSpec.AZUL
    }
}
```

Gradle's toolchain auto-provisioning will fetch Azul Zulu from the
[Azul download API](https://api.azul.com/zulu/) when not present.

## Rule Format

Same shape as the rest of RFD 0008:

```
### JV-{CATEGORY}-{NNN} — one-line directive

**Severity:** error | warning | advisory
**Since:** v0.1.0
**Linter:** Checkstyle / SpotBugs / google-java-format / advisory

**Decision.** What to do.
**Why.** Rationale.
**Exception.** When the rule does not apply, or "None."
**Examples.** ✓ good / ✗ bad code.
```

Categories: `VERSION`, `IMPORT`, `NAMING`, `TYPE`, `NULL`, `ERROR`, `IDIOM`,
`LOG`, `DOC`, `TEST`, `IMMUTABILITY`, `CONCURRENCY`, `SECURITY`, `SPARK`.

## Tooling

### Build Tool

Gradle with Kotlin DSL is the primary build tool for new projects. Maven is
supported for existing projects.

```kotlin
// build.gradle.kts
plugins {
    java
    id("com.diffplug.spotless") version "7.0.2"
    id("checkstyle")
    id("com.github.spotbugs") version "6.0.26"
    id("jacoco")
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
        vendor = JvmVendorSpec.AZUL
    }
}
```

### Formatter: Spotless / google-java-format

```kotlin
spotless {
    java {
        googleJavaFormat("1.24.0")
        removeUnusedImports()
        trimTrailingWhitespace()
        endWithNewline()
    }
}
```

Run `./gradlew spotlessApply` to format. CI runs `spotlessCheck` and fails on
deviation.

### Linter: Checkstyle (Google checks)

```kotlin
checkstyle {
    toolVersion = "10.17.0"
    configFile = file("config/checkstyle/google_checks.xml")
    isIgnoreFailures = false
    maxWarnings = 0
}
```

### Static Analysis: SpotBugs + findsecbugs

```kotlin
spotbugs {
    effort = com.github.spotbugs.snom.Effort.MAX
    reportLevel = com.github.spotbugs.snom.Confidence.MEDIUM
}

dependencies {
    spotbugsPlugins("com.h3xstream.findsecbugs:findsecbugs-plugin:1.13.0")
}
```

### Build Order

Every build runs in order: `spotlessCheck` → `checkstyleMain` → `compileJava`
→ `test` → `spotbugsMain` → `jacocoTestCoverageVerification`. A failure at any
stage halts the build.

---

## Rule index

Rules are split by category. Each category file has the rules in numeric order.

- [`concurrency.md`](concurrency.md) — **Concurrency** (5 rules). java.util.concurrent and thread-safety rules.
- [`doc.md`](doc.md) — **Documentation** (6 rules). Javadoc requirements and package-info.java.
- [`error.md`](error.md) — **Error Handling** (8 rules). Exception handling, try-with-resources, exception chaining.
- [`idiom.md`](idiom.md) — **Idioms** (4 rules). Streams, method references, immutable collectors.
- [`immutability.md`](immutability.md) — **Immutability** (5 rules). Defensive copies, final, and unmodifiable factories.
- [`import.md`](import.md) — **Imports** (3 rules). Group order and wildcard policy per Google Java Style.
- [`log.md`](log.md) — **Logging** (4 rules). SLF4J usage and structured logging.
- [`naming.md`](naming.md) — **Naming** (8 rules). Identifier casing, banned suffixes, test naming.
- [`null.md`](null.md) — **Null and Optional** (7 rules). Optional usage, null discipline, requireNonNull at API boundaries.
- [`security.md`](security.md) — **Security** (6 rules). PreparedStatement, secrets, deserialization, OWASP scan.
- [`spark.md`](spark.md) — **Spark** (7 rules). Spark-on-JVM patterns: DataFrame chains, UDFs, serialization, encoders.
- [`test.md`](test.md) — **Testing** (7 rules). JUnit 5, AssertJ, Mockito, JaCoCo coverage.
- [`type.md`](type.md) — **Types** (5 rules). Records, sealed classes, switch expressions, text blocks, var.
- [`version.md`](version.md) — **Version** (4 rules). Java version policy and Azul Zulu OpenJDK selection.
