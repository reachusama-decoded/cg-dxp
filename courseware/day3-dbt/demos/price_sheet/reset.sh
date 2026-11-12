#!/usr/bin/env bash
# Back to the starting point of the Day 3 "dbt from zero" section: only the two raw CSVs in seeds/.
# The anchor notebook's cells then write every other file, one step at a time.
set -euo pipefail
cd "$(dirname "$0")"
for item in dbt_project.yml profiles.yml models tests macros snapshots target logs warehouse .user.yml; do
  if [ -e "$item" ]; then rm -r "$item"; fi
done
mkdir -p models/staging models/intermediate models/marts tests/generic macros snapshots warehouse
echo "price_sheet/ is back to its starting point:"
find . -type f -not -name ".gitignore" | sort
