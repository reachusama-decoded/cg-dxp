# PY-ERROR: Error Handling

Exception handling, propagation, and domain error types.

## PY-ERROR-001 — Never use bare `except:`

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `E722`, `B001`

**Decision.** Always catch a specific exception type. Bare `except:` is
banned.

**Why.** Bare except catches `KeyboardInterrupt` and `SystemExit`, which
breaks Ctrl-C and clean shutdown.

**Exception.** None.

**Example:**
```python
# Bad — bare except
try:
    df = spark.read.parquet(source_path)
except:
    pass

# Good — specific exception type
try:
    df = spark.read.parquet(source_path)
except AnalysisException as exc:
    logger.error("Failed to read source table at %s: %s", source_path, exc)
    raise
```

## PY-ERROR-002 — Never use `except Exception:` as a catch-all

**Severity:** warning
**Since:** v0.1.0
**Linter:** Ruff `BLE001`

**Decision.** Catching `Exception` is allowed only when re-raising or
logging at ERROR level. Never use it as a silent catch-all.

**Why.** `Exception` covers `KeyError`, `AttributeError`, `TypeError` —
bugs that should crash loudly during development.

**Exception.** Top-level handlers in long-running services where you must
log and continue. Even there, prefer narrower types.

## PY-ERROR-003 — Never swallow exceptions silently

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `BLE001`, `S110`

**Decision.** Every `except` block must do one of:
- Re-raise (`raise`)
- Raise a different exception with `from` (`raise X(...) from e`)
- Log at ERROR level (`logger.exception(...)`)

**Why.** Silently swallowed exceptions hide bugs and corrupt state.

**Exception.** None.

**Example:**
```python
try:
    write_delta(df, target_table)
except Exception:
    logger.exception("Failed to write to %s; aborting pipeline.", target_table)
    raise
```

## PY-ERROR-004 — Use `raise ... from e` for chaining

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `B904`

**Decision.** When raising a new exception inside an `except` block, use
`raise NewError(...) from e` to preserve the original traceback (PEP 3134).

**Why.** Chained tracebacks make root-cause analysis tractable.

**Exception.** Use `raise X from None` to deliberately suppress the cause
when the original exception is irrelevant to the caller.

## PY-ERROR-005 — Define domain exceptions with a base class

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Define a per-package base exception class and inherit from
it. Place exceptions in a dedicated `exceptions.py`.

**Why.** Callers can catch the base class to handle any error from your
package without coupling to specific subtypes.

**Example:**
```python
# exceptions.py — define a base and specific subtypes for the pipeline package
class PipelineError(Exception):
    """Base exception for all pipeline errors."""

class IngestionError(PipelineError):
    """Raised when a source ingestion step fails."""


# usage — raise a specific subtype
def run_ingestion(source_path: str) -> DataFrame:
    """Load raw records from the source path into a Spark DataFrame."""
    try:
        return spark.read.parquet(source_path)
    except AnalysisException as exc:
        raise IngestionError(f"Cannot read source at {source_path}") from exc


# caller — catch the base class to handle any pipeline error uniformly
try:
    run_ingestion(source_path)
except PipelineError:
    logger.exception("Pipeline step failed; halting DAG run.")
    raise
```

## PY-ERROR-006 — Prefer multiple specific excepts over one broad except

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When recovery differs by exception type, write multiple
narrow `except` blocks rather than one broad one with `isinstance` checks.

**Why.** Type-driven dispatch is clearer than runtime type checks.

## PY-ERROR-007 — Prefer context managers over try/finally for resources

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `SIM117`

**Decision.** For any resource with cleanup (files, connections, locks),
use a `with` statement. Reserve `try/finally` for cases where no context
manager exists.

**Why.** Context managers make cleanup impossible to forget. PEP 343.

**Example:**
```python
# Bad — manual cleanup via try/finally is verbose and easy to get wrong
conn = pyodbc.connect(dremio_dsn)
cur = conn.cursor()
try:
    cur.execute("SELECT * FROM lakehouse.sales.orders LIMIT 100")
finally:
    cur.close()
    conn.close()

# Good — context managers guarantee cleanup even on exceptions
with pyodbc.connect(dremio_dsn) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM lakehouse.sales.orders LIMIT 100")
```

### Idioms
