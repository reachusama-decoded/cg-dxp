#!/usr/bin/env bash
# verify.sh — one-command gate for the docker-intro mini-lab.
#
# Builds the learner's starter image, runs it, and checks the expected portfolio
# summary. Set CHALLENGE_DOCKER_CONTEXT=solution to validate the retained solution.
#
# Preflight / client sign-off: missing Docker is SKIP, not PASS.
# Exit 2 on skip unless ALLOW_DOCKER_SKIP=1 (local non-sign-off only).
# When Airflow is in scope and local Astro/devcontainers are used, treat
# exit 2 as FAIL on the results template (same honesty bar as gate 3).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

IMAGE="portfolio-summary-verify"
EXPECTED=$'Portfolio summary\n6 holdings, total market value 12,011,626.50'
BUILD_CONTEXT="${CHALLENGE_DOCKER_CONTEXT:-starter}"

if [[ "$BUILD_CONTEXT" != /* ]]; then
  BUILD_CONTEXT="$SCRIPT_DIR/$BUILD_CONTEXT"
fi

if [[ ! -f "$BUILD_CONTEXT/Dockerfile" ]]; then
  echo "[FAIL] Dockerfile not found in build context: $BUILD_CONTEXT"
  exit 1
fi

_skip() {
  echo "$1"
  if [[ "${ALLOW_DOCKER_SKIP:-0}" == "1" ]]; then
    echo "[note] ALLOW_DOCKER_SKIP=1 set — recording skip without failing (not a preflight PASS)."
    exit 0
  fi
  echo "[FAIL] Docker not available; for client sign-off this is not a green gate when local containers/Airflow are in scope. Set ALLOW_DOCKER_SKIP=1 only for local non-sign-off runs."
  exit 2
}

# --- Is the docker command available at all? ---
if ! command -v docker >/dev/null 2>&1; then
  _skip "[skip] docker not on PATH — install Docker Desktop, or run this inside the course devcontainer."
fi

# --- Is the daemon reachable? ---
if ! docker info >/dev/null 2>&1; then
  _skip "[skip] docker is installed but the daemon is not running — start Docker Desktop and re-run."
fi

# --- Build the selected learner or solution context. ---
echo "[build] docker build -t $IMAGE $BUILD_CONTEXT"
if ! docker build -t "$IMAGE" "$BUILD_CONTEXT"; then
  echo "[FAIL] docker build failed — check the Dockerfile (FROM / WORKDIR / COPY / CMD)."
  exit 1
fi

# --- Run it and capture the output. ---
if ! OUTPUT="$(docker run --rm "$IMAGE" 2>&1)"; then
  echo "[FAIL] docker run failed:"
  echo "$OUTPUT"
  exit 1
fi

echo "----- container output -----"
echo "$OUTPUT"
echo "----------------------------"

if [[ "$OUTPUT" == "$EXPECTED" ]]; then
  echo "[PASS] image built and ran; output is correct."
  exit 0
else
  echo "[FAIL] expected exactly:"
  echo "$EXPECTED"
  exit 1
fi
