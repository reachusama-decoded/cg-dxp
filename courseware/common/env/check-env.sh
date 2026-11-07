#!/usr/bin/env bash
# Pre-flight for the instructor laptop. Prints one line per check; nothing is changed.
source "$(cd "$(dirname "$0")" && pwd)/activate.sh" >/dev/null 2>&1 || true
ok() { printf '  [ok]   %s\n' "$*"; }; bad() { printf '  [FIX]  %s\n' "$*"; }
echo "Instructor environment check"
command -v dbt >/dev/null && ok "dbt $(dbt --version 2>/dev/null | grep installed | awk '{print $3}') with duckdb adapter" || bad "dbt not found: run setup-env.sh"
python -c 'import duckdb' 2>/dev/null && ok "duckdb python $(python -c 'import duckdb;print(duckdb.__version__)')" || bad "duckdb missing in the venv"
if docker info >/dev/null 2>&1; then ok "docker engine reachable ($(docker version --format '{{.Server.Version}}' 2>/dev/null))"; else bad "docker engine not running: open Docker Desktop and wait for the whale"; fi
docker image inspect python:3.11-slim >/dev/null 2>&1 && ok "image python:3.11-slim present (Day 2 Docker demo)" || bad "pull python:3.11-slim before Day 2 (docker pull python:3.11-slim)"
docker image inspect quay.io/astronomer/astro-runtime:3.1-17-base >/dev/null 2>&1 && ok "image astro-runtime:3.1-17-base present (Day 4 Airflow demo)" || bad "pull quay.io/astronomer/astro-runtime:3.1-17-base before Day 4"
command -v astro >/dev/null && ok "astro CLI $(astro version 2>/dev/null | head -1 | awk '{print $NF}')" || bad "astro CLI missing: run setup-env.sh"
[[ -f "$(dirname "$0")/../../day3-dbt/demos/portfolio_analytics/warehouse/training_dev.duckdb" ]] && ok "Day 3 warehouse built (run demo.sh to rebuild)" || bad "Day 3 warehouse not built yet: bash courseware/day3-dbt/demos/portfolio_analytics/demo.sh"
