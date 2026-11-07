# Containerization Standards

## Governing Authority

These standards are derived from and comply with:

- [Open Container Initiative Image Specification](https://github.com/opencontainers/image-spec)
- [Docker Best Practices](https://docs.docker.com/build/building/best-practices/)
- [Development Containers Specification](https://containers.dev/implementors/spec/)
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- RFD 0003 (repository layout) and the platform repo-vending process

These rules apply to the container images the platform builds across data-product
and service repositories \u2014 both the reproducible development containers it vends
into every repo and the production runtime images those repos ship: container
images, container orchestration files, development-container metadata, setup
scripts, and the
task-runner wiring (mise / poe) that bootstraps the workspace. The objective is a
container build that is structurally identical across repositories and
parameterized by a small set of variables, so the result is the same regardless
of host OS, build architecture, editor, or which repo it was built from.

Where this document is silent, OCI/Docker container guidance, the Development
Containers Specification, and the Google Shell Style Guide apply.

## Rule Format

Same shape as the rest of RFD 0008:

```
### CONT-{CATEGORY}-{NNN} — one-line directive

**Severity:** error | warning | advisory
**Since:** v0.1.0
**Linter:** advisory / shellcheck / CI

**Decision.** What to do.
**Why.** Rationale.
**Exception.** When the rule does not apply, or "None."
**Examples.** good / bad config.
```

Categories: `BASE`, `PATH`, `ENV`, `SETUP`, `PORT`.

## Current Platform Posture

Three decisions worth surfacing up front because they shape several rules below:

1. **Nothing is keyed to a user, home, or host path.** The workspace is derived
   from the container at runtime, the virtual environment is workspace-relative,
   and the interpreter setting is image-stable. A path that embeds a literal
   repo name, a `/home/<user>/` prefix, or a host absolute path is the most
   common cause of a broken vended container. See `CONT-PATH-001`.
2. **Scripts are the unit of vending, not inline shell.** Setup logic lives in
   committed container setup scripts that can be re-vended and updated
   centrally. Task-runner tasks only ever call those scripts. Inlining logic
   into a `.mise.toml` / `pyproject.toml` task is how downstream repos drift
   from canonical. See `CONT-SETUP-001`.
3. **Parameterize, do not fork.** Per-repo differences live in `.env` /
   environment metadata, never in divergent script logic. See `CONT-ENV-003`.
4. **Source everything from internal mirrors.** Public PyPI, Docker Hub, npm,
   conda, and Maven are blocked on the CG network. Every base image, package
   install, and build-time download routes through the internal registry /
   Nexus mirror. An example that pulls from a public host is the most common
   reason a copied Dockerfile fails to build. See `CONT-BASE-004`.

---

## Rule index

Rules are split by category. Each category file has the rules in numeric order.

- [`base.md`](base.md) — **Base Image, User, and Script Hygiene** (4 rules). Industry-common foundations: pin base image and tool versions, run as non-root, strict-mode and quoted shell scripts, source images and packages from internal mirrors.
- [`path.md`](path.md) — **Paths and Interpreter** (3 rules). Workspace, venv, and interpreter paths: no host/home hardcoding, single source of truth, runtime-derived workspace.
- [`env.md`](env.md) — **Environment** (3 rules). Persisting normalized env for all shells, quote normalization, parameterization via `.env` / container environment metadata.
- [`setup.md`](setup.md) — **Setup Tasks and Scripts** (3 rules). Scripts as the unit of vending, idempotent guarded tasks, no emojis in container output.
- [`portability.md`](portability.md) — **Portability** (3 rules). OS-agnostic host-path detection, one-time vs per-start lifecycle separation, architecture-agnostic builds.
