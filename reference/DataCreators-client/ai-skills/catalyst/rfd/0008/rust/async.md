# RS-ASYNC: Async

tokio runtime, structured concurrency, and async-safety rules.

## RS-ASYNC-001 — tokio is the async runtime

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** All async code targets tokio. No `async-std`, `smol`, or
mixed runtimes.

**Why.** A single runtime per workspace avoids cross-runtime
incompatibilities and simplifies dependency selection.

## RS-ASYNC-002 — `try_join!` for concurrent independent tasks

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When multiple awaitable values are independent, use
`tokio::try_join!` rather than awaiting them sequentially.

**Examples.**
```rust
use tokio::try_join;

let (tables, schemas, permissions) = try_join!(
    client.list_tables(),
    client.list_schemas(),
    client.list_permissions(),
)?;
```

## RS-ASYNC-003 — `select!` for racing or cancellation

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `tokio::select!` for racing futures (e.g., timeout vs
result, shutdown signal vs work).

**Examples.**
```rust
use tokio::select;

select! {
    result = client.fetch() => result.context("fetch failed"),
    _ = tokio::time::sleep(timeout) => {
        Err(anyhow::anyhow!("request timed out after {:?}", timeout))
    }
}
```

## RS-ASYNC-004 — Bound concurrency with `Semaphore`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When spawning N tasks against a finite resource (database,
HTTP server, filesystem), gate spawns through a `tokio::sync::Semaphore`.

**Why.** Unbounded `tokio::spawn` in a loop overwhelms downstream
services and OOM-kills the process.

**Examples.**
```rust
use tokio::sync::Semaphore;
use std::sync::Arc;

let semaphore = Arc::new(Semaphore::new(max_concurrent));
let mut handles = Vec::new();
for table in tables {
    let permit = semaphore.clone().acquire_owned().await?;
    handles.push(tokio::spawn(async move {
        let result = profile_table(&table).await;
        drop(permit);
        result
    }));
}
```

## RS-ASYNC-005 — Never block the runtime

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Don't call blocking I/O or CPU-bound code in an async
function. Use `tokio::fs`, `tokio::task::spawn_blocking`, or move work
to a dedicated thread pool.

**Why.** A blocked async task blocks the executor thread, starving
every other task on that runtime.

**Examples.**
```rust
// ✓
let data = tokio::fs::read_to_string("config.toml").await?;

// ✗
let data = std::fs::read_to_string("config.toml")?;  // blocks executor
```

## RS-ASYNC-006 — Never hold `std::sync::Mutex` across `.await`

**Severity:** error
**Since:** v0.1.0
**Linter:** Clippy `await_holding_lock`

**Decision.** Use `tokio::sync::Mutex` (or `parking_lot` with care) when
the lock guard must be held across an await point. Standard library
`Mutex` is not async-aware and deadlocks if a task is preempted while
holding it.

**Examples.**
```rust
// ✓
let guard = tokio_mutex.lock().await;
do_something().await;

// ✗
let guard = std_mutex.lock().unwrap();
do_something().await;  // DEADLOCK RISK
```

### Logging
