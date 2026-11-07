#!/usr/bin/env python3
"""Session 2 suite: verifier baseline + starter/solution journeys, offline and live. Writes suite.tsv."""
import json, os, shutil, subprocess, sys, time
from pathlib import Path
ROOT = Path('/workspaces/edo-training-data-products')
RUN = ROOT / '.local/live/20261005T141153Z'
J = RUN / 'journeys'
EV = ROOT / '.local/v2-evidence'
LOGS = RUN / 'suite-logs'; LOGS.mkdir(exist_ok=True)
OUT = RUN / sys.argv[1] if len(sys.argv) > 1 else RUN / 'suite.tsv'
only = set(sys.argv[2:])
phases = [l.split() for l in subprocess.run(['python3', 'scripts/challenge-v2.py', 'list'], cwd=ROOT, text=True, capture_output=True).stdout.splitlines()]
phases = [(t, p) for t, p, o in phases if o == 'offered' and (not only or t in only)]
env = {**os.environ, 'V2_DB_SCHEMA': 'training_conmhab'}
if not OUT.exists():
    OUT.write_text('journey\ttool\tphase\taction\tmode\texit\tresult\tseconds\tevidence\tnote\n')

def one(journey, tool, phase, action, mode, ws=None):
    cmd = ['mise', 'exec', '--', 'python3', 'scripts/challenge-v2.py', action, tool, phase, '--mode', mode]
    if ws: cmd += ['--workspace', str(ws)]
    before = set(EV.glob('*.json')); t = time.monotonic()
    log = LOGS / f'{journey}-{tool}-{phase}-{action}-{mode}.log'
    with log.open('w') as f:
        code = subprocess.run(cmd, cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=3600).returncode
    new = sorted(set(EV.glob('*.json')) - before)
    result, note, ev = 'no-report', '', ''
    if new:
        r = json.loads(new[-1].read_text()); result = r['result']; ev = new[-1].name
        o = r['observations']; note = (o.get('reason') or o.get('error') or '')[:200].replace('\t', ' ').replace('\n', ' ')
    row = [journey, tool, phase, action, mode, str(code), result, str(round(time.monotonic() - t)), ev, note]
    with OUT.open('a') as f: f.write('\t'.join(row) + '\n')
    print('\t'.join(row[:8]), flush=True)

for tool, phase in phases:
    key = f'{tool}-{phase}'
    for mode in ['offline', 'live']:
        one('baseline', tool, phase, 'verify-starter', mode)
        one('baseline', tool, phase, 'verify-solution', mode)
        one('starter', tool, phase, 'verify', mode, J / 'starter' / key)
    sol = J / 'solution' / key
    if not (sol / '.solution-applied').exists():
        shutil.copytree(ROOT / 'challenges/v2-solutions' / tool / phase / 'solution', sol, dirs_exist_ok=True)
        (sol / '.solution-applied').write_text('shipped solution copied over the prepared starter\n')
    for mode in ['offline', 'live']:
        one('solution', tool, phase, 'verify', mode, sol)
print('SUITE-DONE', flush=True)
