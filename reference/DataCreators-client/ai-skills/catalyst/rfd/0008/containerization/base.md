# CONT-BASE: Base Image, User, and Script Hygiene

Foundational, industry-common rules that apply to every containerized
development environment regardless of language or repo. Grounded in the Google
Shell Style Guide and standard container hardening practice.

## CONT-BASE-001 — Pin the base image and tool versions

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** The base image is pinned to a specific version tag (and, where the
registry supports it, also by digest). Every tool installed during the build or
managed by the task runner is pinned to an explicit version. Never use `latest`
or an unpinned floating tag.

**Why.** Reproducible, deterministic builds. An unpinned base image or tool means
two developers — or CI versus a laptop — silently get different environments,
producing "works on my machine" failures that cannot be reproduced. Pinning makes
the container deterministic and turns an upgrade into a reviewable, intentional
diff instead of a surprise.

**Exception.** An internal image MAY reference a sibling image by a mutable tag
(for example `FROM ${repo}myapp-base:latest` in the matching unit-test image)
only when both images are built and published atomically by the same pipeline
run, so the floating tag resolves deterministically within that build. Even
then an immutable build tag is preferred; a mutable tag pulled independently of
its build pipeline is a violation.

**Examples.**
```dockerfile
# ✗ — floating tag; the environment drifts under you (and pull from the internal
#     registry, never public Docker Hub, which is blocked — see CONT-BASE-004)
FROM cgregistry-aws.capgroup.com/capgroup.com/python:latest

# ✓ — pinned to a specific tag (digest pin is stronger still), sourced from the
#     internal hardened registry
FROM cgregistry-aws.capgroup.com/capgroup.com/python:3.12

# ✓ — production runtime image: registry parameterized via a build ARG, base
#     pinned to an explicit build tag, tools pinned to exact versions
#     (rclone v1.60.0, kubectl v1.33.0), never a floating download
ARG repo
FROM ${repo}pyspark-base:5.2.0-a2
RUN set -eux; \
    pip install --no-cache-dir \
      --index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/ \
      "setuptools==80.9.0"
```
```toml
# ✓ — task-runner tools pinned to exact versions (development container)
[tools]
python = "3.12.13"
uv = "0.11.2"
databricks-cli = "0.236.0"
```

## CONT-BASE-002 — Run the container as a non-root user

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** The container runs as a non-root user by default. In a development
container, `remoteUser` is set to a non-root account such as `vscode`; in a
plain Dockerfile, use `USER` for the runtime stage. Steps that genuinely need
elevation use `sudo` or a dedicated build stage for that specific command,
rather than running the whole interactive/runtime container as root.

**Why.** Least privilege. A root container means any compromised dependency or
setup script runs with full container privileges, and files it writes to mounted
volumes become root-owned on the host — a recurring source of permission pain.
A non-root default limits blast radius and keeps host file ownership sane.

**Exception.** Base images whose tooling genuinely requires root, documented in
the containerization README or template guidance. Prefer migrating to a non-root
image when feasible.

**Examples.**
```jsonc
// ✗ — full root for the whole session
"remoteUser": "root"

// ✓ — non-root default; elevate per-command via sudo when needed
"remoteUser": "vscode"
```
```dockerfile
# ✓ — production runtime image: run privileged build steps as root, then drop to
#     a non-root service account for the runtime stage. dnf resolves through the
#     hardened base image's pre-configured internal repos, never the public distro
#     mirrors, which are blocked on the CG network (see CONT-BASE-004)
USER root
RUN dnf install -y <build-only packages> && dnf clean all
# ... build and install ...
USER appuser:appuser
```
```dockerfile
# ✓ — isolate root-only build work in a dedicated builder stage, so the final
#     runtime image never needs root
FROM ${repo}spark-base:7.12.0 AS builder
USER root
RUN pip install --no-cache-dir \
      --index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/ \
      --target /deps -r requirements.txt

FROM ${repo}spark-base:7.12.0
COPY --from=builder /deps /usr/lib/python3/site-packages
USER appuser:appuser
```

## CONT-BASE-003 — Setup scripts use strict mode and quote all expansions

**Severity:** error
**Since:** v0.1.0
**Linter:** shellcheck

**Decision.** Every shell script enables strict mode at the top — `set -euo
pipefail` for bash, `set -eu` for POSIX `sh` — and quotes all variable and command
expansions. A command whose non-zero exit is expected guards locally
(`cmd || true`); strict mode is never disabled globally.

**Why.** Google Shell Style Guide. Without strict mode, a failed command midway
through setup is ignored and the container ends up half-provisioned while
reporting success. Unquoted expansions break on paths containing spaces and open
word-splitting and glob bugs. Strict mode plus quoting converts silent corruption
into a loud, debuggable failure at the point it happens.

**Exception.** None. A specific tolerated failure is guarded inline, not by
dropping strict mode.

**Examples.**
```sh
# ✗ — only -e; unquoted expansions; a failed cp is swallowed downstream
set -e
cp $SRC $DEST

# ✓ — strict mode plus quoted expansions
set -euo pipefail
cp "$SRC" "$DEST"
```

## CONT-BASE-004 — Source all base images and packages from internal mirrors

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Every `FROM`, package install, and build-time download resolves
through an internal mirror, never a public registry. Base images come from
`cgregistry-aws.capgroup.com/...` (the hardened Chainguard set, where one is
vended for the language); Python packages use `--index-url
https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/` (or a committed
`pip.conf` pointing at it); OS packages (`apt` / `dnf` / `yum`), npm, conda, and
Maven likewise resolve through their internal mirrors. No build step pulls
directly from Docker Hub, pypi.org, npmjs.com, or a public vendor download host.

**Why.** Public PyPI, Docker Hub, npm, conda, and Maven are blocked on the CG
corporate network. A `FROM python:3.12` or an unscoped `pip install` resolves
against a public host and fails with a connection timeout on every developer
laptop and CI runner, and a direct public download inside a build is exactly the
supply-chain path the registry policy blocks. Routing through the internal
mirrors is the only pattern that builds on the network and keeps provenance
auditable. Because this is a standards document, its canonical examples are
copied verbatim, so they must model the compliant source.

**Exception.** None on the corporate network. A documented, network-isolated
build that has its own vetted mirror substitutes that mirror's host.

**Examples.**
```dockerfile
# ✗ — public Docker Hub base + public PyPI install; both blocked on the CG network
FROM python:3.12
RUN pip install --no-cache-dir -r requirements.txt

# ✓ — internal registry base image + internal pip index
FROM cgregistry-aws.capgroup.com/capgroup.com/python:3.12
RUN pip install --no-cache-dir \
      --index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/ \
      -r requirements.txt
```
