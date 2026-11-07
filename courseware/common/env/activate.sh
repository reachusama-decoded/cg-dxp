# Source this file in each demo terminal:  source courseware/common/env/activate.sh
export CG_DXP_VENV="${CG_DXP_VENV:-$HOME/.venvs/cg-dxp}"
export PATH="$CG_DXP_VENV/bin:$HOME/.local/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH"
export DBT_SEND_ANONYMOUS_USAGE_STATS=false
export ASTRO_TELEMETRY=false
alias dbtv='dbt --version'
echo "cg-dxp demo env: $(dbt --version 2>/dev/null | grep installed | tr -d ' ') | duckdb $(python -c 'import duckdb;print(duckdb.__version__)' 2>/dev/null) | $(docker --version 2>/dev/null) | astro $(astro version 2>/dev/null | head -1 | awk '{print $NF}')"
