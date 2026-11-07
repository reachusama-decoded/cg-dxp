# RS-CARGO: Cargo

Cargo.toml conventions and workspace inheritance.

## RS-CARGO-001 — Workspace inheritance for shared settings

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Edition, version, license, repository, rust-version, and
lints are defined in the workspace `Cargo.toml` and inherited by member
crates.

**Examples.**
```toml
# Workspace Cargo.toml
[workspace.package]
edition = "2021"
rust-version = "1.78"
license = "MIT"
repository = "https://github.com/org/catalyst"

# Member crate
[package]
name = "catalog-client"
version = "0.1.0"
edition.workspace = true
rust-version.workspace = true
license.workspace = true

[lints]
workspace = true
```

## RS-CARGO-002 — Default features `= []`

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Library crates set `default = []`. Don't enable heavy
features (`tokio/full`, `serde/derive`) by default.

**Why.** Forces consumers to opt in. Keeps binary size and compile time
under control.

## RS-CARGO-003 — Version requirements: stable major or minor

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `"1"` or `"1.2"` for stable crates. Use exact versions
(`"=1.2.3"`) only when a known regression exists in newer versions, and
document why.

### Performance
