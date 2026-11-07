#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

databricks current-user me
cd "$repo_root/data_products/atlas_elt"
python "$repo_root/dbt_wrapper.py" debug --connection --project-dir . --profiles-dir dbt_profiles --target local
# Capstone models start as `select 1 as placeholder`; skip those and their dependents until authored.
stubs="$(find datasets -name '*.sql' -exec grep -lx 'select 1 as placeholder' {} + 2>/dev/null | xargs -r -n1 basename | sed 's/\.sql$/+/' | tr '\n' ' ')"
exclude=()
if [[ -n "$stubs" ]]; then
  echo "Skipping $(wc -w <<<"$stubs") capstone placeholder model(s) and their dependents"
  exclude=(--exclude "$stubs")
fi
python "$repo_root/dbt_wrapper.py" build --project-dir . --profiles-dir dbt_profiles --target local "${exclude[@]}"
echo "Databricks verification: PASS"
