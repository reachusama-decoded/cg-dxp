# JV-NAMING: Naming

Identifier casing, banned suffixes, test naming.

## JV-NAMING-001 — Identifier casing per Google Java Style

**Severity:** error
**Since:** v0.1.0
**Linter:** Checkstyle

**Decision.** Use the conventions in this table:

| Item | Convention | Example |
|------|-----------|---------|
| Packages | `all.lowercase.no_underscores` | `com.catalyst.pipeline.lineage` |
| Classes | `UpperCamelCase` | `TableProfiler` |
| Interfaces | `UpperCamelCase` (no `I` prefix) | `DataSource` |
| Enums | `UpperCamelCase` | `PipelineStatus` |
| Enum constants | `SCREAMING_SNAKE_CASE` | `IN_PROGRESS` |
| Methods | `lowerCamelCase` | `fetchTableProfile` |
| Fields (instance) | `lowerCamelCase` | `rowCount` |
| Fields (static final) | `SCREAMING_SNAKE_CASE` | `MAX_BATCH_SIZE` |
| Local variables | `lowerCamelCase` | `columnStats` |
| Type parameters | `T` or `CamelCaseT` | `T`, `ResponseT` |

## JV-NAMING-002 — No `I` prefix on interfaces

**Severity:** error
**Since:** v0.1.0
**Linter:** Checkstyle

**Decision.** Java interfaces don't use `I` as a prefix.

**Why.** That convention is C#, not Java. The compiler distinguishes
interfaces from classes; the prefix adds noise.

**Examples.**
```java
// ✓
public interface DataSource { ... }

// ✗
public interface IDataSource { ... }
```

## JV-NAMING-003 — No `Impl` suffix as a default

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Don't name a class `DataSourceImpl`. Name what makes the
implementation distinct: `JdbcDataSource`, `MockDataSource`,
`InMemoryDataSource`.

**Why.** `Impl` carries no information. If there's only one implementation,
ask whether the interface is needed.

## JV-NAMING-004 — No Hungarian notation

**Severity:** error
**Since:** v0.1.0
**Linter:** Checkstyle

**Decision.** No type prefixes on identifiers (`strName`, `iCount`,
`bIsActive`).

**Why.** The type system carries the type information.

## JV-NAMING-005 — No single-character names except loop counters

**Severity:** warning
**Since:** v0.1.0
**Linter:** Checkstyle

**Decision.** Single-character names are allowed only for loop counters
(`i`, `j`, `k`) and lambda parameters where the type is obvious from
context.

## JV-NAMING-006 — No generic class names (`Manager`, `Helper`, `Util`, `Handler`)

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Avoid `Manager`, `Helper`, `Util`, `Handler` as class names
unless the class genuinely manages a lifecycle or handles events. If the
generic name fits, the class probably has no cohesive purpose.

**Why.** Generic suffixes hide the actual responsibility.

## JV-NAMING-007 — Test classes named `{ClassUnderTest}Test`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** A test for `TableProfiler` is named `TableProfilerTest`.

## JV-NAMING-008 — Test methods named `methodName_condition_expectedBehavior`

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Test method names use underscores to separate the method
under test, the precondition, and the expected outcome.

**Examples.**
```java
// ✓
@Test
void profile_validTable_returnsColumnStats() { ... }

@Test
void profile_missingTable_throwsSchemaNotFound() { ... }

// ✗
@Test
void test1() { ... }

@Test
void testProfile() { ... }
```

### Types
