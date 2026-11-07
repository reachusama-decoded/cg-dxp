#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v uv >/dev/null || { echo 'uv required for the isolated capture environment' >&2; exit 77; }
cd "$ROOT"
if [ ! -x .local/demo-capture/bin/python ]; then
  uv venv .local/demo-capture --python 3.11
fi
uv pip sync --python .local/demo-capture/bin/python instructor-demos/requirements.lock
.local/demo-capture/bin/python -m playwright install chromium
.local/demo-capture/bin/python scripts/instructor-demos.py validate
