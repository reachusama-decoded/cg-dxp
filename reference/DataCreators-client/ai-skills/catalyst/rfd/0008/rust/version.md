# RS-VERSION: Version

Toolchain pinning and MSRV policy.

## RS-VERSION-001 — Pin the toolchain via `rust-toolchain.toml`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Every repository contains a `rust-toolchain.toml` at the
root that pins the exact stable version, components, and targets.

**Why.** Reproducible builds. A floating `stable` channel produces
different warnings, dependency resolution, and codegen across machines
and CI. Pinning eliminates "works on my machine."

**Exception.** None.

**Examples.**
```toml
# rust-toolchain.toml
[toolchain]
channel = "1.82.0"
components = ["rustfmt", "clippy", "rust-src"]
targets = ["x86_64-unknown-linux-gnu", "aarch64-apple-darwin"]
```

## RS-VERSION-002 — MSRV 1.78+, updated quarterly

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Minimum Supported Rust Version is 1.78. The MSRV bumps
quarterly across the workspace.

**Why.** Keeps the platform on a current toolchain without forcing
constant churn.

**Exception.** Crates published externally may pin a lower MSRV; document
in their `Cargo.toml`.

## RS-VERSION-003 — No nightly features in production code

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Production code uses stable Rust only. Nightly is permitted
in CI for `cargo fuzz` and `miri`, but not in shipped binaries or
libraries.

**Why.** Nightly features change without warning and pin you to a moving
target.

**Exception.** A nightly feature genuinely required must be approved via
RFD before adoption.

### Imports
