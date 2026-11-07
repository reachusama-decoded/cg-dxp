#!/usr/bin/env python3
"""Assigned Portfolio/Atlas routing; offline evidence cannot certify execution."""
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
V2 = ROOT / 'challenges/v2'
RUNTIME = V2 / 'runtime/portfolio'


def files(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()
            and not set(p.relative_to(root).parts) & {'target', 'logs', '__pycache__', '.git', '.venv'}
            and p.name not in {'.env', '.user.yml'}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'reset', 'verify', 'verify-starter', 'verify-solution'])
    parser.add_argument('tool', choices=['dbt', 'airflow', 'capstone'])
    parser.add_argument('phase', choices=['phase-one-certified', 'phase-two-proficient'])
    parser.add_argument('--workspace', type=pathlib.Path)
    parser.add_argument('--mode', choices=['offline', 'live'], default='offline')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    starter = V2 / args.tool / args.phase / 'starter'
    source = starter
    if args.action == 'verify-solution':
        source = ROOT / 'challenges/v2-solutions' / args.tool / args.phase / 'solution'
    if args.action in ['prepare', 'reset']:
        dest = (args.workspace or ROOT / '.local/challenges-v2' / args.tool / args.phase).resolve()
        if dest.exists():
            parser.error('Workspace exists; choose a new --workspace. Reset preserves existing attempts.')
        if args.dry_run:
            print(json.dumps({'copy': str(source), 'destination': str(dest), 'runtime': str(RUNTIME)}))
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, dest)
        shutil.copytree(RUNTIME, dest / 'runtime', ignore=shutil.ignore_patterns('__pycache__'))
        (dest / 'v2-attempt.json').write_text(json.dumps({'tool': args.tool, 'phase': args.phase,
            'starter_sha256': files(source), 'completion': False}, indent=2) + '\n')
        print(dest)
        return
    if args.action == 'verify':
        if not args.workspace:
            parser.error('verify requires --workspace; instructor answers use verify-solution')
        source = args.workspace.resolve()
    elif args.workspace:
        source = args.workspace.resolve()
    if not source.is_dir():
        parser.error('Missing source workspace')
    if args.dry_run:
        print(json.dumps({'source': str(source), 'mode': args.mode, 'action': args.action,
                          'boundary': 'Astro/Databricks' if args.tool == 'airflow' else 'Databricks',
                          'writes': 'fresh temporary copy; owned warehouse only in explicit live mode'}))
        return
    before = files(source)
    evidence = ROOT / '.local/v2-evidence'
    evidence.mkdir(parents=True, exist_ok=True)
    report = {'tool': args.tool, 'phase': args.phase, 'action': args.action, 'mode': args.mode,
              'source_sha256': before, 'completion': False,
              'runtime_sha256': files(RUNTIME), 'status': 'pending', 'observations': []}
    code = 0
    with tempfile.TemporaryDirectory(prefix='assigned-v2-') as temp:
        workspace = pathlib.Path(temp) / 'attempt'
        shutil.copytree(source, workspace, ignore=shutil.ignore_patterns('target', 'logs', '__pycache__', '.venv', 'runtime'))
        shutil.copytree(RUNTIME, workspace / 'runtime', ignore=shutil.ignore_patterns('__pycache__'))
        result = subprocess.run([sys.executable, str(workspace / 'runtime/lab.py'), 'static', str(workspace)], text=True, capture_output=True)
        unfinished = result.returncode == 1 and 'Untouched/incomplete' in result.stderr
        if args.action == 'verify-starter':
            if unfinished:
                report['status'] = 'baseline-pass'
                report['observations'].append('Declared untouched starter is rejected as completed work')
            else:
                report['status'] = 'fail'
                report['observations'].append('Starter did not demonstrate its declared unfinished state')
                code = 1
        elif result.returncode:
            report['status'] = 'fail'
            report['observations'].append(result.stderr.strip())
            code = 1
        elif args.mode == 'offline':
            report['status'] = 'supporting-only'
            report['observations'].append('Static authoring/profile checks pass; connected completion pending')
            code = 77 if args.action == 'verify' else 0
        elif args.tool == 'airflow':
            scheduled = workspace / 'scheduled-evidence.json'
            if not scheduled.exists():
                report['status'] = 'blocked'
                report['observations'].append('Use mise run challenge:v2:airflow-evidence with three fresh scheduled runs, then verify the owned stage; syntax cannot certify workers')
                code = 77
            else:
                earlier = json.loads(scheduled.read_text())
                command = [sys.executable, str(workspace / 'runtime/check-scheduled.py'), str(workspace), '--after', earlier['session_started_at']]
                for label in ['success', 'failure', 'repair']:
                    command += ['--' + label, earlier['runs'][label]['run']['dag_run_id']]
                checked = subprocess.run(command, text=True, capture_output=True)
                report['status'] = 'pass' if checked.returncode == 0 else 'blocked' if checked.returncode == 77 else 'fail'
                report['completion'] = checked.returncode == 0
                report['observations'] += [checked.stdout.strip(), checked.stderr.strip()]
                code = checked.returncode
        else:
            case = 'atlas' if args.tool == 'capstone' else 'portfolio'
            result = subprocess.run([sys.executable, str(workspace / 'runtime/lab.py'), 'run', str(workspace), '--case', case], text=True, capture_output=True)
            report['status'] = 'pass' if result.returncode == 0 else 'fail'
            report['completion'] = result.returncode == 0
            report['observations'].append(result.stdout.strip())
            report['observations'].append(result.stderr.strip())
            code = result.returncode
            if result.returncode == 0:
                from v2_assigned_behaviour import verify as verify_behaviour
                try:
                    report['behaviour'] = verify_behaviour(workspace, args.tool, args.phase)
                except Exception as error:
                    report['status'] = 'fail'
                    report['completion'] = False
                    report['observations'].append('Required live behavioral drill failed: ' + str(error))
                    code = 1
            for name in ['evidence.json', 'execution-start.json']:
                if (workspace / name).exists():
                    report[name] = json.loads((workspace / name).read_text())
    assert files(source) == before, 'Verification modified source files'
    report['cleanup'] = 'temporary copy removed; source bytes unchanged'
    output = evidence / f'{args.tool}-{args.phase}-{args.action}-{time.time_ns()}.json'
    output.write_text(json.dumps(report, indent=2, default=str) + '\n')
    print(json.dumps({'status': report['status'], 'completion': report['completion'], 'report': str(output), 'observations': report['observations']}, indent=2))
    sys.exit(code)


if __name__ == '__main__':
    main()
