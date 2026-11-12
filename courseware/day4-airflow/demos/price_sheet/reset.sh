#!/usr/bin/env bash
# Back to the starting point of Day 4's bitemporal section: Day 3's finished price sheet (the files in start/)
# and the seeds. The anchor notebook's cells then write the history model and the macro, one step at a time.
set -euo pipefail
cd "$(dirname "$0")"
for item in dbt_project.yml profiles.yml models tests macros target logs warehouse .user.yml; do
  if [ -e "$item" ]; then rm -r "$item"; fi
done
cp -R start/. .
mkdir -p models/history warehouse
echo "price_sheet/ is Day 3's finished project again:"
find . -type f -not -path "./start/*" -not -name ".gitignore" -not -name "reset.sh" | sort
