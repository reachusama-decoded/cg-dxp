#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HERE"
while [[ ! -f "$ROOT/.mise.toml" || ! -f "$ROOT/dbt_wrapper.py" ]]; do
  [[ "$ROOT" != / ]] || { echo 'Project root not found' >&2; exit 2; }
  ROOT="$(dirname "$ROOT")"
done
exec "${V2_PYTHON:-python3}" "$ROOT/scripts/challenge-v2.py" verify-solution docker phase-two-proficient "$@"
