"""Supplied deterministic hashing, atomic file writes and generated-seed schema."""
import csv
import hashlib
import json
import os
from pathlib import Path
HISTORY_FIELDS=['row_uid','product_id','metric','value','business_valid_from','business_valid_to','system_valid_from','system_valid_to']

def digest(value):
    # Canonical JSON prevents dictionary order from changing an event identity.
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def atomic_json(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    os.replace(temporary,path)

def ensure_generated_seed(root):
    # Git ignores generated state, so recreate the empty schema after a fresh clone.
    path=Path(root)/'.local/generated/cg_training_history.csv'
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        with path.open('w',newline='') as f:
            csv.writer(f).writerow(HISTORY_FIELDS)
    return path

def write_history(root, history):
    path=ensure_generated_seed(root)
    temporary=path.with_suffix('.tmp')
    with temporary.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=HISTORY_FIELDS)
        writer.writeheader();writer.writerows(history)
    os.replace(temporary,path)
    return path
