# CONT-PORT: Portability

Making the same container behave identically across host operating systems and
across the container lifecycle.

## CONT-PORT-001 — OS-agnostic host-path detection

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory + shellcheck

**Decision.** When a script needs the host path of the workspace (for example to
wire a sibling bind mount), detect it at runtime via `docker inspect` of the
container's mounts and normalize the result — convert backslashes to forward
slashes and trim a trailing slash. Do not hardcode an absolute host path in a
compose `.env`.

**Why.** Compose `.env` files do not expand `$HOME` or `~`, so a hardcoded host
path only works on the machine it was written for and silently produces an
empty or wrong mount elsewhere. Windows hosts return backslash paths from
`docker inspect` that break compose parsing unless normalized. Runtime detection
plus normalization is the only approach that is correct on macOS, Linux, and
Windows hosts simultaneously.

**Exception.** None.

**Examples.**
```sh
# ✓ — detect from the container, normalize for cross-OS compose compatibility
HOST_PATH=$(docker inspect -f \
  '{{ range .Mounts }}{{ if eq .Destination "'"$WORKSPACE_DEST"'" }}{{ .Source }}{{ end }}{{ end }}' \
  "$(hostname)")
HOST_PATH=$(printf '%s' "$HOST_PATH" | sed 's#\\#/#g')   # backslashes -> forward slashes
HOST_PATH=${HOST_PATH%/}                                  # trim trailing slash
```

## CONT-PORT-002 — Separate one-time setup from per-start work

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Idempotent, expensive bootstrap (trusting the task runner,
installing tools, creating the venv, normalizing env) belongs in
`postCreateCommand`. Lightweight work that must happen on every container start
(syncing dependencies, refreshing a branch-derived variable) belongs in
`postStartCommand`. Each command stays idempotent.

**Why.** `postCreateCommand` runs once at build; `postStartCommand` runs on every
start. Putting per-start work in `postCreate` means it never refreshes; putting
heavy bootstrap in `postStart` slows every container start. Splitting them keeps
startup fast and the environment current.

**Exception.** None.

**Examples.**
```jsonc
// ✓ — heavy one-time bootstrap vs light per-start refresh
"postCreateCommand": "mise trust .mise.toml && mise install && mise run setup",
"postStartCommand": "uv sync --extra dbt --extra dev"
```

## CONT-PORT-003 — Build architecture-agnostically

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When a build downloads architecture-specific binaries, select the
architecture at build time from the platform — Docker's `TARGETARCH` / `TARGETOS`
build args or `uname -m` — and map it to the vendor's asset naming. Never
hardcode a single architecture (for example always fetching the `amd64` asset).

**Why.** The same image is built on Apple Silicon laptops (arm64) and on amd64
CI and production hosts. A hardcoded-architecture download produces an image that
either fails to build or silently ships the wrong-architecture binary on one of
those platforms. Deriving the architecture keeps a single Dockerfile correct on
every build host.

**Exception.** Images intentionally restricted to a single architecture,
documented as such.

**Examples.**
```dockerfile
# ✗ — hardcoded architecture; breaks on arm64 build hosts
RUN curl -fsSL https://example.com/tool-linux-amd64 -o /usr/local/bin/tool

# ✓ — production runtime image: resolve arch from the build platform, then map it
#     to the vendor's asset name. The binary comes from the internal mirror, not
#     the public vendor download host (see CONT-BASE-004)
ARG TARGETARCH
RUN case "${TARGETARCH}" in \
      amd64) arch=amd64 ;; \
      arm64) arch=arm64 ;; \
      *) echo "unsupported arch: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    curl -fsSL "https://cgrepo-aws.capgroup.com/repository/cgbinaries/rclone/v1.60.0/rclone-v1.60.0-linux-${arch}.zip" -o /tmp/rclone.zip
```
