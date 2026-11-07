#!/usr/bin/env bash
# Public wrapper: execute the same Python checker from this working product's directory.
# No separate shell acceptance logic or implicit tool installation.
set -euo pipefail
cd "$(dirname "$0")"
exec python3 verify-starter.py "$@"
