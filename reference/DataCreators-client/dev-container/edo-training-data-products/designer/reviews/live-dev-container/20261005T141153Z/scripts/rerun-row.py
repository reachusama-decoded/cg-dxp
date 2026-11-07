#!/usr/bin/env python3
"""Re-run single suite rows (journey tool phase action mode [workspace]) and append them, marked as reruns."""
import json, os, subprocess, sys, time
from pathlib import Path
ROOT = Path('/workspaces/edo-training-data-products'); RUN = ROOT / '.local/live/20261005T141153Z'; EV = ROOT / '.local/v2-evidence'
journey, tool, phase, action, mode = sys.argv[1:6]; ws = sys.argv[6] if len(sys.argv) > 6 else None
cmd = ['mise', 'exec', '--', 'python3', 'scripts/challenge-v2.py', action, tool, phase, '--mode', mode] + (['--workspace', ws] if ws else [])
before = set(EV.glob('*.json')); t = time.monotonic(); log = RUN / 'suite-logs' / f'rerun-{journey}-{tool}-{phase}-{action}-{mode}.log'
with log.open('w') as f:
    code = subprocess.run(cmd, cwd=ROOT, env={**os.environ, 'V2_DB_SCHEMA': 'training_conmhab'}, stdout=f, stderr=subprocess.STDOUT).returncode
new = sorted(set(EV.glob('*.json')) - before); r = json.loads(new[-1].read_text()) if new else {'result': 'no-report', 'observations': {}}
o = r['observations']; note = 'rerun: ' + (o.get('reason') or o.get('error') or '')[:180].replace('\t', ' ').replace('\n', ' ')
row = [journey, tool, phase, action, mode, str(code), r['result'], str(round(time.monotonic() - t)), new[-1].name if new else '', note]
with (RUN / 'suite.tsv').open('a') as f: f.write('\t'.join(row) + '\n')
print('\t'.join(row))
