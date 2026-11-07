# PY-IDIOM: Idioms

Idiomatic patterns: iteration, formatting, paths, context managers, logging, datetimes.

## PY-IDIOM-001 — Use `sys.exit` or `SystemExit`, never `os._exit`, `quit`, or `exit`

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `PLW1510`, `B0`

**Decision.** Terminate scripts with `sys.exit(code)` or `raise
SystemExit(message)`. Never `os._exit()`, `quit()`, or `exit()`.

**Why.** `os._exit` skips cleanup (atexit, finally, context managers).
`quit`/`exit` are REPL helpers, not for scripts.

**Exception.** `os._exit` is correct in a forked child after `os.fork()`.

## PY-IDIOM-002 — Use `enumerate` instead of `range(len(...))`

**Severity:** warning
**Since:** v0.1.0
**Linter:** Ruff `PIE808`, `SIM110`

**Decision.** Iterate with `enumerate(items)` when you need the index.

**Why.** Pythonic and faster than `range(len(items))` indexing.

## PY-IDIOM-003 — Iterate directly; don't index when you don't need the index

**Severity:** warning
**Since:** v0.1.0
**Linter:** Ruff `SIM`

**Decision.** Loop over the collection directly when you don't need the
index.

**Why.** Clearer and avoids off-by-one bugs.

## PY-IDIOM-004 — `zip(..., strict=True)` for parallel iteration

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `B905`

**Decision.** When iterating multiple sequences, use `zip(a, b,
strict=True)`. Available in Python 3.10+.

**Why.** Without `strict=True`, `zip` silently truncates to the shortest
sequence, hiding length mismatches.

**Exception.** When mismatched lengths are intentional (rare), use
`itertools.zip_longest` and document why.

## PY-IDIOM-005 — Comprehensions for transforms; for-loops for side effects

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `C4`

**Decision.** Use comprehensions to build new collections. Use for-loops
when the body has side effects (logging, mutation, I/O).

**Why.** A comprehension that exists only for side effects allocates a
list that is immediately discarded. It also reads as if it produces
something.

## PY-IDIOM-006 — Use `itertools` for complex iteration

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Reach for `itertools` (`groupby`, `chain`, `islice`,
`takewhile`, etc.) before writing nested loops with index bookkeeping.

**Why.** Standard, lazy, well-tested.

## PY-IDIOM-007 — f-strings for runtime string construction

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `UP032`

**Decision.** Use f-strings (PEP 498) to construct strings at runtime.

**Why.** Faster than `.format()`, clearer than `%`-formatting, and the
canonical Python 3.6+ style.

**Exception.** See PY-IDIOM-008 (template-and-data separation),
PY-IDIOM-015 (logging), and SQL queries (PY-SECURITY-002).

## PY-IDIOM-008 — `.format()` only when template and data are separate

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `.format()` only when the template is defined separately
from the data — for example, a template loaded from configuration.

**Why.** f-strings can't reference deferred templates. `.format()` can.

## PY-IDIOM-009 — Never `%`-format new code

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `UP031`

**Decision.** Don't use `%`-formatting (`"hello %s" % name`) in new code.

**Why.** Legacy syntax. f-strings are clearer and faster.

**Exception.** Logging (PY-IDIOM-015) — the logger does its own lazy
`%`-formatting.

## PY-IDIOM-010 — `pathlib` only; never string concatenation or `os.path`

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `PTH`

**Decision.** Build paths with `pathlib.Path`. Never concatenate strings
or use `os.path.join`.

**Why.** PEP 428. `pathlib` is OS-portable, type-aware, and provides
high-level operations.

## PY-IDIOM-011 — Always use context managers for resources

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `SIM115`

**Decision.** Files, connections, locks, and any resource with cleanup
must be acquired in a `with` block.

**Why.** Cleanup-on-error is impossible to forget when the resource is
held in a context manager. PEP 343.

## PY-IDIOM-012 — Use `dataclasses` for structured data

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `@dataclass` (PEP 557) for plain structured data. Reach
for pydantic when you need validation; reach for `attrs` only with strong
reason.

**Why.** Built-in, zero dependency, type-aware.

## PY-IDIOM-013 — `frozen=True` for immutable value objects

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Mark dataclasses `frozen=True` when instances should not be
mutated after construction.

**Why.** Catches accidental mutation; makes instances hashable.

## PY-IDIOM-014 — `slots=True` for memory-sensitive dataclasses

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Add `slots=True` when a dataclass is instantiated in volume
(large lists, hot loops). Available 3.10+.

**Why.** ~40% memory savings, ~20% attribute access speedup. Costs:
no `__dict__`, no monkey-patching.

## PY-IDIOM-015 — Lazy logging with `%` formatting

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `G`, pylint `W1202`

**Decision.** Pass arguments to logging calls; never format with f-strings
or `.format()` in the call itself.

**Why.** The arguments are only formatted if the log level is enabled.
f-string formatting always runs, wasting CPU on suppressed log lines.

## PY-IDIOM-016 — Never `print()` in production code

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `T20`

**Decision.** Use `logger.info()` (or appropriate level), not `print()`,
in production code.

**Why.** `print()` has no level, no timestamp, no structure, and goes to
stdout regardless of logging configuration.

**Exception.** CLI tools that intentionally write to stdout for piping.
Tests are allowed via `per-file-ignores`.

## PY-IDIOM-017 — `logger.exception` to capture tracebacks

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Inside an `except` block, use `logger.exception(msg, ...)`
to log with the full traceback. Equivalent to `logger.error(...,
exc_info=True)`.

**Why.** Without `exc_info`, the log line tells you something failed but
not where.

## PY-IDIOM-018 — Always use timezone-aware datetimes

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `DTZ`

**Decision.** All datetime values are timezone-aware. Construct with
`datetime.now(tz=timezone.utc)` or with an explicit tzinfo. Parse with
`datetime.fromisoformat(...)` on tz-bearing strings.

**Why.** Naive datetimes silently break across timezones, DST, and
serialization boundaries.

## PY-IDIOM-019 — Never `datetime.now()` without `tz` and never `datetime.utcnow()`

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `DTZ001`, `DTZ003`

**Decision.** `datetime.now()` (no tz) returns a naive datetime in local
time. `datetime.utcnow()` returns a naive datetime despite the name. Both
are banned.

**Why.** Naive datetimes lose meaning the moment they cross a process or
timezone boundary.

## PY-IDIOM-020 — t-strings (template strings, Python 3.14+)

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use t-strings (PEP 701) for template-based string substitution
when the template and data are separated, starting in Python 3.14+. For
earlier versions, use `string.Template` or `.format()`. For most runtime
string construction, prefer f-strings (see PY-IDIOM-007).

**Why.** t-strings provide a native, readable syntax for deferred template
substitution, similar to JavaScript template literals.

**Exception.** Use `string.Template` or `.format()` for compatibility with
Python <3.14.

**Example (Python 3.14+):**
```python
name = "Alice"
day = "Monday"
msg = t"Hello, {name}! Today is {day}."
# result: 'Hello, Alice! Today is Monday.'
```

**Example (Python <3.14):**
```python
from string import Template

tmpl = Template("Hello, $name! Today is $day.")
msg = tmpl.substitute(name="Alice", day="Monday")
# result: 'Hello, Alice! Today is Monday.'
```

## PY-IDIOM-021 — Use `functools.lru_cache` for simple memoization

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `@functools.lru_cache` to memoize pure functions with
immutable arguments, especially for expensive computations or repeated
lookups.

**Why.** Built-in, thread-safe, and avoids manual cache boilerplate. Makes
code faster and clearer when repeated calls are common.

**Exception.** Do not use for functions with side effects or mutable
arguments.

**Example:**
```python
import functools

@functools.lru_cache(maxsize=128)
def get_exchange_rate(currency: str) -> float:
    # Simulate expensive API call
    ...

# First call computes, subsequent calls are cached
rate = get_exchange_rate("USD")
```

## PY-IDIOM-022 — Use `contextlib` utilities for advanced resource management

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `contextlib` utilities like `contextlib.suppress`,
`contextlib.ExitStack`, and `contextlib.contextmanager` for advanced context
management and error handling.

**Why.** These tools simplify complex resource cleanup, error suppression,
and custom context manager creation.

**Exception.** Use only when standard `with` blocks are insufficient or when
managing multiple resources dynamically.

**Example:**
```python
from contextlib import suppress, ExitStack

# Suppress specific exceptions
with suppress(FileNotFoundError):
    os.remove("/tmp/stale_file")

# Dynamically manage multiple context managers
with ExitStack() as stack:
    files = [stack.enter_context(open(f)) for f in file_list]
    # ... work with all files ...
```

### Testing
