#!/usr/bin/env bash
# Build an isolated review candidate; never promote/overwrite the accepted v4 release.
set -euo pipefail
CLIENT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CAPITAL="$(cd "$CLIENT/../../.." && pwd)"
V4="$CAPITAL/DataCreators-v4"
CANDIDATE="$V4/candidates/challenges-v2"
BUILDER="${CWBUILDER_ROOT:-$(git -C "$CLIENT" rev-parse --show-toplevel)/../ts-courseware/Platform/CwBuilder}"
export PATH="$V4/build/node_modules/.bin:$PATH"
python3 "$CLIENT/scripts/sync-v2-course.py" --check
mkdir -p "$CANDIDATE/reviews/qualifying-text" "$CANDIDATE/render/images"
python3 "$V4/scripts/count-learner-words.py" "$CANDIDATE/learner" "$CANDIDATE/reviews/qualifying-text" --require-minimum
python3 - "$CANDIDATE" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]);files=sorted((p/'learner').glob('[0-9][0-9]-*.md'));assert len(files)==13
(p/'render/course.md').write_text('\n\n'.join(f.read_text() for f in files))
PY
# Project-local chapter-link mapping includes the new full challenge appendix.
cp "$CANDIDATE/build/pdf/book-links.lua" "$CANDIDATE/render/book-links.lua"
python3 - "$CANDIDATE/render/book-links.lua" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]);t=p.read_text().replace('local chapters = {',"local chapters = {\n  ['13-appendix-h-challenges-v2.md'] = 'appendix-h',")
p.write_text(t)
PY
ARGS=("--lua-filter=$CLIENT/scripts/v2-presentation.lua")
for name in strip-notes engage extra callouts admonitions expert worked-example try-your-own scenario predict; do ARGS+=("--lua-filter=$BUILDER/filters/$name.lua"); done
ARGS+=("--lua-filter=$CANDIDATE/build/pdf/debrief.lua" "--lua-filter=$CANDIDATE/build/pdf/provenance.lua")
for name in themed-sections multicol-overview mermaid check-images table-style breakable-inline-code; do ARGS+=("--lua-filter=$BUILDER/filters/$name.lua"); done
ARGS+=("--lua-filter=$CANDIDATE/render/book-links.lua")
pandoc "$CANDIDATE/render/course.md" -o "$CANDIDATE/DataCreators-challenges-v2.pdf" --pdf-engine=xelatex \
 --metadata-file="$BUILDER/themes/decoded/prose-base.yaml" --metadata-file="$CANDIDATE/build/pdf/visual-style.yaml" \
 --include-in-header="$BUILDER/themes/decoded/prose-header.tex" --include-in-header="$CANDIDATE/build/pdf/debrief-header.tex" --include-in-header="$CANDIDATE/build/pdf/five-day-visual-header.tex" \
 "${ARGS[@]}" -M notes-mode=say -M remove-hrs=true -M "mermaid-output-dir=$CANDIDATE/render/images" -M "mermaid-theme-config=$BUILDER/themes/decoded/mermaid-theme.json" \
 -V 'title=Data Creators Programme 2026' -V 'subtitle=Challenge pack v2 — full course review candidate' -V 'author=Skills Lab' -V date=2026-10-05 --toc -V toc-depth=2 \
 --resource-path="$CANDIDATE/learner:$CANDIDATE/render:$BUILDER/themes/decoded" > "$CANDIDATE/render/build.log" 2>&1
pdftotext -layout "$CANDIDATE/DataCreators-challenges-v2.pdf" "$CANDIDATE/render/course.txt"
python3 "$CLIENT/scripts/review-v2-course.py"
