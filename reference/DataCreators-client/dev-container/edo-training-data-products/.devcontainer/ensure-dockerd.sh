#!/usr/bin/env sh

set -eu

# Opt-out escape hatch (matches dpc-academy behavior).
[ -n "${DPC_SKIP_DOCKERD_HEAL:-}" ] && exit 0

# Fast path for interactive shells.
pgrep -x dockerd >/dev/null 2>&1 && exit 0

if docker info >/dev/null 2>&1; then
  exit 0
fi

echo "inner Docker daemon unhealthy; scheduling recovery" >&2

nohup /usr/local/bin/start-dockerd.sh --restart --no-wait >/var/log/dockerd-heal.log 2>&1 </dev/null &
exit 0
