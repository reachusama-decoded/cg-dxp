#!/usr/bin/env bash
# One-time setup of the instructor demo environment on a Mac. Safe to re-run.
# Pins follow the learners' dev container (.devcontainer/requirements.txt): dbt-core 1.11.8,
# with dbt-duckdb 1.11.1 standing in for dbt-databricks 1.11.7. Python 3.13 as in the container.
set -euo pipefail
VENV="${CG_DXP_VENV:-$HOME/.venvs/cg-dxp}"
PY="${CG_DXP_PYTHON:-$(command -v python3.13 || command -v python3)}"
echo "Python: $PY ($("$PY" --version 2>&1))"
if [[ ! -x "$VENV/bin/python" ]]; then
  "$PY" -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install -q --upgrade pip
"$VENV/bin/python" -m pip install -q "dbt-core==1.11.8" "dbt-duckdb==1.11.1" "pyyaml>=6,<7" pytest ipykernel pandas "nbformat>=5" deltalake pyarrow "pyspark==3.5.7"
echo "dbt: $("$VENV/bin/dbt" --version 2>/dev/null | grep -E 'installed|duckdb' | tr '\n' ' ')"
# Astro CLI (same `astro dev` commands as the learners' dev container). Installed without sudo.
if ! command -v astro >/dev/null 2>&1 && [[ ! -x "$HOME/.local/bin/astro" ]]; then
  mkdir -p "$HOME/.local/bin"; T="$(mktemp -d)"
  URL=$(curl -s https://api.github.com/repos/astronomer/astro-cli/releases/latest | python3 -c "import sys,json; d=json.load(sys.stdin); print([a['browser_download_url'] for a in d['assets'] if a['name'].endswith('darwin_arm64.tar.gz')][0])")
  curl -sSL "$URL" -o "$T/astro.tar.gz" && tar -xzf "$T/astro.tar.gz" -C "$T" && mv "$T/astro" "$HOME/.local/bin/astro" && chmod +x "$HOME/.local/bin/astro"; rm -rf "$T"
fi
cat <<MSG

Done. In every terminal you use for the demos, run:

  source "$(cd "$(dirname "$0")" && pwd)/activate.sh"

That puts dbt, duckdb and astro on PATH and points docker at Docker Desktop.
MSG

# Register the kernel the anchor notebooks use
"$VENV/bin/python" -m ipykernel install --user --name cg-dxp --display-name "Python (cg-dxp)" >/dev/null
