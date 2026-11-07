#!/usr/bin/env python3
"""Show the product, profile and assigned warehouse target; never print credentials."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime.workspace import check_workspace

if __name__ == '__main__':
    try:
        print(json.dumps(check_workspace(ROOT), indent=2))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print('Workspace check failed: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
