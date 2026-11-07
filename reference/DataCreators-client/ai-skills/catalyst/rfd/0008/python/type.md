# PY-TYPE: Types

Type annotations, modern syntax, and structural typing.

## PY-TYPE-001 — All public function signatures must be annotated

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `ANN`

**Decision.** Every public function and method declares parameter types and
return type.

**Why.** Type annotations are documentation that the type checker can
verify. They prevent a class of bugs and make refactoring safe.

**Exception.** None for public functions. Tests are exempt.

## PY-TYPE-002 — All class attributes must be annotated

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `ANN`, pyright

**Decision.** Annotate every class attribute, either at class level or
through `__init__` parameter annotations (preferred via `@dataclass`).

**Why.** Same as PY-TYPE-001. Without annotations, pyright cannot infer
attribute types reliably.

**Exception.** None.

## PY-TYPE-003 — Annotate non-trivial private functions

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Private functions should be annotated unless the types are
trivially obvious from a one-line body.

**Why.** Private code drifts; today's "obvious" body is tomorrow's bug
source. The cost of an annotation is small.

**Exception.** Trivial one-liners with self-evident types.

## PY-TYPE-004 — Modern type syntax (PEP 585, PEP 604)

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `UP006`, `UP007`, `UP035`

**Decision.** Use built-in generic syntax: `list[str]` not `List[str]`,
`dict[str, int]` not `Dict[str, int]`, `str | None` not `Optional[str]`,
`X | Y` not `Union[X, Y]`.

**Why.** PEP 585 / PEP 604 are the canonical syntax in 3.10+.
`typing.List`, `typing.Dict`, `typing.Optional` are legacy aliases.

**Exception.** None for new code. Stub files (`.pyi`) targeting older
Python versions may use `typing` aliases.

## PY-TYPE-005 — No `Any` without justification

**Severity:** warning
**Since:** v0.1.0
**Linter:** Ruff `ANN401`

**Decision.** `Any` defeats the type checker. Every use of `Any` must have
an inline comment explaining why a more specific type is impossible.

**Why.** `Any` propagates through code and silently disables checks. If you
must use it, the why should be visible.

**Exception.** Type-erased deserialization at API boundaries.

## PY-TYPE-006 — Return type reflects all possibilities

**Severity:** error
**Since:** v0.1.0
**Linter:** pyright

**Decision.** If a function can return `None`, its return type is
`X | None`. If it can return multiple types, the return type is a union.

**Why.** A return annotation that hides `None` lets `None` propagate to
callers as a runtime `AttributeError`.

**Exception.** None.

## PY-TYPE-007 — Use `TypeAlias` for complex types

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When a type expression repeats or grows beyond ~50 chars,
define a `TypeAlias`.

**Why.** Names give shape to types and make signatures readable.

**Exception.** None.

## PY-TYPE-008 — Use `Protocol` for structural typing

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When you need duck typing with type-checker support, define a
`Protocol` (PEP 544) instead of an abstract base class.

**Why.** Protocols are structural — they don't require explicit
inheritance, which keeps the type system aligned with how Python actually
works.

**Exception.** When you need shared implementation, use an ABC instead.

**Example:**
```python
from typing import Protocol

# BatchSource is the structural contract (the port). load_orders depends
# only on that contract, not on a concrete backend. SparkSource and
# DremioSource are interchangeable adapters that implement the same
# read(table) shape, so either class can be passed to load_orders without
# changing pipeline logic.


class BatchSource(Protocol):
    """Protocol for batch sources that can read a table into a DataFrame."""

    def read(self, table: str) -> "DataFrame":
        ...


def load_orders(source: BatchSource) -> "DataFrame":
    """Load the orders table using any source implementing BatchSource."""
    return source.read("orders")


class SparkSource:
    """Batch source implementation backed by Spark tables."""

    def read(self, table: str) -> "DataFrame":
        return spark.table(table)


class DremioSource:
    """Batch source implementation backed by Dremio."""

    def read(self, table: str) -> "DataFrame":
        return dremio.read_table(table)
```

### Docstrings
