#!/usr/bin/env python3
"""Pin this product's code before a shared-Astro run; nothing is copied.

Airflow already reads this product folder through the data_products/ mount. The
pinned manifest lets each worker task refuse code that changed after staging,
and binds receipts to the exact bytes that ran. Finish active runs, then restage.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runtime.io_support import atomic_json, ensure_generated_seed
from runtime.product import ROOT, STAGED_MANIFEST, assignment, code_manifest


def stage(root):
    root = Path(root).resolve()
    if root.parent.name != 'data_products':
        raise ValueError('Stage your own product under data_products/, not ' + str(root))
    assignment(root)
    manifest = root / STAGED_MANIFEST.relative_to(ROOT)
    atomic_json(manifest, code_manifest(root))
    ensure_generated_seed(root)
    for name in ['evidence/runtime', '.local/events']:
        (root / name).mkdir(parents=True, exist_ok=True)
    return manifest


if __name__ == '__main__':
    try:
        print(stage(Path(__file__).resolve().parents[1]))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print('Staging refused: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
