"""Supplied product identity for the shared Astro runtime; not assessed work.

Every CG product sits directly under data_products/ and is mounted into the
same Airflow workers. Paths, DAG IDs and owned prefixes come from this product's
folder and .capstone-workspace.json, never from container-wide settings.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE_DIRECTORIES = ['models', 'macros', 'tests', 'runtime', 'dags', 'include']
CODE_FILES = ['dbt_project.yml', 'profiles.yml']
STAGED_MANIFEST = ROOT / '.local/staged-code-manifest.json'
# The shared Airflow cluster policy rejects DAGs without these tag keys.
REQUIRED_TAGS = ['usage-id:AA00002933', 'cost-center:52415']


def assignment(root=ROOT):
    path = Path(root) / '.capstone-workspace.json'
    if not path.is_file():
        raise ValueError('Missing .capstone-workspace.json in ' + Path(root).name + '; ask for the assignment.')
    value = json.loads(path.read_text())
    if value.get('product_name') != Path(root).name:
        raise ValueError('Assignment belongs to ' + str(value.get('product_name')) + ', not ' + Path(root).name)
    if not re.fullmatch('[a-z][a-z0-9_]{2,55}', str(value.get('relation_prefix', ''))):
        raise ValueError('Assigned relation prefix is missing or invalid.')
    return value


def dag_id(suffix, root=ROOT):
    return Path(root).name + '__' + suffix


def owned_prefix(prefix, root=ROOT):
    owner = assignment(root)['relation_prefix']
    if prefix != owner and not prefix.startswith(owner + '_'):
        raise ValueError('Relation prefix ' + prefix + ' is outside this product\'s assigned prefix ' + owner)
    return prefix


def code_manifest(root=ROOT):
    root = Path(root)
    files = {}
    for name in CODE_DIRECTORIES:
        for path in sorted((root / name).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                files[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    for name in CODE_FILES:
        files[name] = hashlib.sha256((root / name).read_bytes()).hexdigest()
    return files
