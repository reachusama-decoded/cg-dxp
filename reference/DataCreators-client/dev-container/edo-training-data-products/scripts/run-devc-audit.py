#!/usr/bin/env python3
"""Run isolated supporting starter/reference checks; never implies connected acceptance."""
import argparse, csv, hashlib, json, os, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run-id', default=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    ap.add_argument('--tools', nargs='+')
    ap.add_argument('--refresh-matrix', action='store_true', help='Refresh task/status inventory from existing results; runs no tools')
    a = ap.parse_args()
    out = ROOT/'designer/reviews/live-dev-container'/a.run_id
    raw = ROOT/'.local/live-dev-audit'/a.run_id
    out.mkdir(parents=True, exist_ok=True); raw.mkdir(parents=True, exist_ok=True)
    m = json.loads((ROOT/'challenges/v2/manifest.json').read_text())
    records = json.loads((out/'verification-results.json').read_text()) if a.refresh_matrix else []
    for t in m['tools']:
        if a.refresh_matrix:break
        if a.tools and t['id'] not in a.tools: continue
        for p in t['phases']:
            if not p['offered']: continue
            for action in ['verify-starter', 'verify-solution']:
                cmd = [sys.executable, str(ROOT/'scripts/challenge-v2.py'), action, t['id'], p['id'], '--mode', 'offline']
                before = set((ROOT/'.local/v2-evidence').glob('*.json'))
                start = time.monotonic()
                proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                log = raw/f"{t['id']}-{p['id']}-{action}.log"; log.write_text(proc.stdout)
                new = set((ROOT/'.local/v2-evidence').glob('*.json'))-before
                candidates=[json.loads(file.read_text()) for file in new]
                candidates=[r for r in candidates if r['tool']==t['id'] and r['phase']==p['id'] and r['action']==action]
                report = candidates[0] if len(candidates)==1 else {'result':'fail', 'observations':{'error':'No unique matching evidence report'}}
                record = {'run_id':a.run_id, 'tool':t['id'], 'phase':p['id'], 'journey':action, 'route':'offline/supporting', 'exit_code':proc.returncode, 'duration_seconds':round(time.monotonic()-start,3), 'raw_log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(), 'report':report}
                records.append(record)
                print(t['id'], p['id'], action, report['result'], flush=True)
                (out/'verification-results.json').write_text(json.dumps(records,indent=2)+'\n')
    with (out/'task-matrix.csv').open('w') as f:
        w = csv.writer(f); w.writerow(['task_id','tool','phase','route','starter','solution','learner_reconstruction','negative','editorial'])
        for t in m['tools']:
            for p in t['phases']:
                for task in p['tasks']:
                    matches = [r for r in records if r['tool']==t['id'] and r['phase']==p['id']]
                    statuses={r['journey']:r['report']['result'] for r in matches}
                    local_route={'git':'local-git' if p['id']=='phase-one-certified' else 'local-simulated-collaboration','docker':'host-python-app/supporting-only','dbt':'local-duckdb','capstone':'local-duckdb','databricks-cli':'metadata-fixture/supporting-only','airflow':'local-airflow-import-or-dag-test','kafka':'event-fixture/supporting-only'}[t['id']]
                    w.writerow([task['id'],t['id'],p['id'],local_route,'phase-baseline: '+statuses.get('verify-starter','not-run'),'phase-reference: '+statuses.get('verify-solution','not-run'),'see explicit reconstruction ledger; otherwise not-run','phase-level observations only; task review pending','not-run'])
                    connected={'git':'authorized-github/reviewer','docker':'real-docker','dbt':'connected-databricks','capstone':'connected-databricks','databricks-cli':'actual-workspace-and-unity-catalog-metadata','airflow':'astro-scheduler-worker-api-ui','kafka':'broker-airflow-dbt-chain'}[t['id']]
                    if t['id']!='git' or p['id']!='phase-one-certified':
                        w.writerow([task['id'],t['id'],p['id'],connected,'blocked: missing runtime/assignment','blocked: missing runtime/assignment','not-run','not-run','not-run'])
    print(out)
if __name__=='__main__':main()
