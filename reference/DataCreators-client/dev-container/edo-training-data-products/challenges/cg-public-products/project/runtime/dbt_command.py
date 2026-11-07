#!/usr/bin/env python3
"""Run learner dbt commands against explicit, checked product/profile paths.

Refuses the challenge template, a wrong cwd or a mismatched assigned schema/prefix.
The private assessor uses separate owned verification targets and does not call this.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime.workspace import check_workspace


def main(arguments):
    details = check_workspace(ROOT)
    if not arguments or arguments[0] not in {'seed', 'build', 'run', 'test', 'compile', 'show', 'debug', 'parse', 'ls'}:
        raise ValueError('Use seed, build, run, test, compile, show, debug, parse or ls.')
    # Destination flags are owned here so a remembered v1 flag cannot redirect work.
    for arg in arguments:
        if arg.split('=', 1)[0] in {'--project-dir', '--profiles-dir', '--target', '--target-path', '-t'} or (arg.startswith('-t') and not arg.startswith('--')):
            raise ValueError('Project/profile/target flags are supplied by this helper; remove your override.')
    executable = shutil.which(os.environ.get('CG_DBT_EXECUTABLE', 'dbt'))
    if not executable:
        raise ValueError('The prepared dbt executable is missing. Use the course devcontainer and its tool setup.')
    version = subprocess.run([executable, '--version'], capture_output=True, text=True)
    if version.returncode or 'databricks' not in (version.stdout + version.stderr).lower():
        raise ValueError('The selected dbt executable has no Databricks adapter. Restore the course dbt environment.')
    print(json.dumps(details, indent=2), flush=True)
    location = ['--project-dir', str(ROOT), '--profiles-dir', str(ROOT), '--target', 'training']
    if arguments[0] in {'seed', 'build', 'run', 'test'}:
        # Compile with the same phase variables before writes. Ignore selection here:
        # every enabled output must remain within this product's assigned namespace.
        variables = []
        for index, arg in enumerate(arguments):
            if arg == '--vars':
                if index + 1 >= len(arguments):
                    raise ValueError('--vars needs a value.')
                variables += [arg, arguments[index + 1]]
            elif arg.startswith('--vars='):
                variables.append(arg)
        compiled = subprocess.run([executable, 'compile', *variables, *location], cwd=ROOT)
        if compiled.returncode:
            return compiled.returncode
        manifest = json.loads((ROOT / 'target/manifest.json').read_text())
        for node in manifest['nodes'].values():
            config = node.get('config', {})
            kind = node.get('resource_type')
            writes = kind in {'model', 'seed', 'snapshot'} or kind == 'test' and config.get('store_failures')
            if writes and config.get('enabled', True):
                if node.get('database') != details['catalog'] or node.get('schema') != details['schema'] or not str(node.get('alias', '')).startswith(details['relation_prefix'] + '_'):
                    raise ValueError('Compiled output escapes the assigned catalog/schema/prefix: ' + node.get('unique_id', node.get('name', 'unknown node')))
    command = [executable, *arguments, *location]
    return subprocess.run(command, cwd=ROOT).returncode


if __name__ == '__main__':
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print('dbt command blocked: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
