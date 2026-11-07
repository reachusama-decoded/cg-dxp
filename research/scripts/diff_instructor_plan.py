#!/usr/bin/env python3
"""Compare the current reference/instructor-plan.md with the Cohort 7 PDF version
(extracts/cohort7/instructor-plan-pdf.txt) paragraph by paragraph and print the
paragraphs that only exist in one of them. Run with: python3 -I research/scripts/diff_instructor_plan.py"""
import difflib, pathlib, re, sys
root = pathlib.Path(__file__).resolve().parent.parent.parent
md = (root / "reference/instructor-plan.md").read_text(encoding="utf8")
pdf = (root / "research/extracts/cohort7/instructor-plan-pdf.txt").read_text(encoding="utf8")
def paras(text):
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)           # drop md links
    text = re.sub(r"\+44 \(0\)20 3583 0972.*", "", text)            # drop pdf footers
    text = re.sub(r"\n\d+\s*$", "", text, flags=re.M)
    text = re.sub(r"[*`|#>-]", " ", text)
    out = []
    for p in re.split(r"\n\s*\n", text):
        p = " ".join(p.split()).lower()
        if len(p) > 60: out.append(p)
    return out
a, b = paras(md), paras(pdf)
def sim(p, pool): return max((difflib.SequenceMatcher(None, p, q).ratio() for q in pool), default=0)
print("## Paragraphs in the current instructor-plan.md with no close match in the Cohort 7 PDF\n")
for p in a:
    if sim(p, b) < 0.8: print("-", p[:400], "\n")
print("\n## Paragraphs in the Cohort 7 PDF with no close match in the current instructor-plan.md\n")
for p in b:
    if sim(p, a) < 0.8: print("-", p[:400], "\n")
