#!/usr/bin/env python3
"""Public design check: documents exist and are edited; not full ODCS validation."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
failed=[]
for name in ['docs/PRD.md','contracts/product-research.odcs.yaml','docs/STTM.csv']:
    text=(root/name).read_text()
    if 'AUTHOR:' in text or len(text.strip().splitlines())<3:
        failed.append(name)
if failed:
    print('Complete and review the design artifacts: '+', '.join(failed))
    raise SystemExit(1)
print('Design artifacts edited. Instructor reviews meaning and validates the pinned ODCS schema separately.')
