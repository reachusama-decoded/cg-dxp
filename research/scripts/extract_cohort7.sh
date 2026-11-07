#!/usr/bin/env bash
# Regenerates plain-text extracts of the Cohort 7 PDFs and the Day 1 agenda docx
# into extracts/cohort7/. Needs poppler (pdftotext) and python3.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="$ROOT/reference/DCP Cohort 7 (Oct _26)"
OUT="$ROOT/research/extracts/cohort7"
mkdir -p "$OUT"
squeeze() { sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' | cat -s; }
pdf() { pdftotext -layout "$1" - | squeeze > "$OUT/$2"; }
pdf "$SRC/Day 1  - Monday/Day 1 AI notes.pdf"               d1-ai-notes.txt
pdf "$SRC/Day 1  - Monday/Day 1 transcript.pdf"             d1-transcript.txt
pdf "$SRC/Day 2 - Tuesday/Day 2 AI notes - with agenda.pdf" d2-ai-notes.txt
pdf "$SRC/Day 2 - Tuesday/Day 2 transcript.pdf"             d2-transcript.txt
pdf "$SRC/Day 3 - Wednesday/Day 3 AI notes.pdf"             d3-ai-notes.txt
pdf "$SRC/Day 3 - Wednesday/Day 3 agenda.pdf"               d3-agenda.txt
pdf "$SRC/Day 3 - Wednesday/Day 3 transcript.pdf"           d3-transcript.txt
pdf "$SRC/Day 4 - Thursday/Day 4 AI notes with agenda.pdf"  d4-ai-notes.txt
pdf "$SRC/Day 4 - Thursday/Day 4 transcript.pdf"            d4-transcript.txt
pdf "$SRC/Day 5 - Friday/Day 5 AI notes with agenda.pdf"    d5-ai-notes.txt
pdf "$SRC/Day 5 - Friday/Day 5 transcript.pdf"              d5-transcript.txt
pdf "$SRC/Day 5 - Friday/Capstone Team Presentations.pdf"   d5-capstone-presentations.txt
pdf "$SRC/DataCreators-instructor-plan.pdf"                 instructor-plan-pdf.txt
pdf "$SRC/DataCreators-SlideDeck.pdf"                       slidedeck.txt
pdftotext "$SRC/DataCreators-v4-3.pdf" "$OUT/learner-book-v4-3.txt"
# Day 1 agenda (docx): strip the XML down to paragraphs
TMP="$(mktemp -d)"; unzip -o -q "$SRC/Day 1  - Monday/Day 1 agenda.docx" -d "$TMP"
python3 -I - "$TMP/word/document.xml" "$OUT/d1-agenda.txt" <<'PY'
import re, sys
x = open(sys.argv[1], encoding="utf8").read()
x = re.sub(r"</w:p>", "\n", x); x = re.sub(r"<w:tab/>", "\t", x); x = re.sub(r"<[^>]+>", "", x)
open(sys.argv[2], "w").write(x.replace("&amp;", "&"))
PY
rm -rf "$TMP"
echo "Extracts written to $OUT"
