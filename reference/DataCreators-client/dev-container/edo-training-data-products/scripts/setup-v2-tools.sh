#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
command -v uv >/dev/null || { echo 'Install uv in the prepared client environment first' >&2; exit 77; }
# uv ignores /etc/pip.conf; public PyPI refuses some sdists here, so use the image's index.
if [[ -z "${UV_DEFAULT_INDEX:-}" ]] && command -v pip >/dev/null; then
  UV_DEFAULT_INDEX="$(pip config --global get global.index-url 2>/dev/null || true)"
  [[ -n "$UV_DEFAULT_INDEX" ]] && export UV_DEFAULT_INDEX
fi
if ! uv python find 3.11 >/dev/null 2>&1 && ! uv python install 3.11; then
  # Some proxies cut off uv's download mid-stream; curl can resume it, then uv installs from a local mirror.
  url="$(uv python list 3.11 --only-downloads --output-format json | python3 -c 'import json,sys; print(next(x["url"] for x in json.load(sys.stdin) if x["implementation"]=="cpython" and x["variant"]=="default"))')"
  rel="$(python3 -c 'import sys,urllib.parse; print(urllib.parse.unquote(sys.argv[1].split("/releases/download/",1)[1]))' "$url")"
  mirror="$ROOT/.local/python-mirror"
  mkdir -p "$mirror/$(dirname "$rel")"
  url="https://github.com/astral-sh/python-build-standalone/releases/download/${url#*/releases/download/}"
  echo "uv download failed; fetching $url with curl"
  rm -f "$mirror/$rel"
  curl -fsSL --retry 5 --retry-all-errors -C - -o "$mirror/$rel" "$url"
  UV_PYTHON_INSTALL_MIRROR="file://$mirror" uv python install 3.11
fi
# --clear: after a container rebuild the venvs survive on the bind mount but their uv Python doesn't.
uv venv --clear .local/v2-tools --python 3.11
uv pip install --python .local/v2-tools/bin/python -r scripts/v2-tools-requirements.txt
uv venv --clear .local/v2-airflow --python 3.11
uv pip install --python .local/v2-airflow/bin/python apache-airflow==3.1.0 apache-airflow-providers-standard confluent-kafka --constraint https://raw.githubusercontent.com/apache/airflow/constraints-3.1.0/constraints-3.11.txt
echo 'Use .local/v2-tools/bin/dbt for dbt; .local/v2-airflow/bin/python for Airflow/bridge.'
