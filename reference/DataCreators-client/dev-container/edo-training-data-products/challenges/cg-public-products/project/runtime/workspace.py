"""Check the learner's working product and assigned target before running tools.

The instructor supplies .capstone-workspace.json in each working product. It
contains locations/identifiers only, never credentials. Templates have no assignment.
"""
import json
import os
import re
from pathlib import Path


def check_workspace(root, environ=None, cwd=None):
    """Return safe diagnostic fields; reject wrong folders or target variables."""
    env = os.environ if environ is None else environ
    root = Path(root).resolve()
    current = Path.cwd().resolve() if cwd is None else Path(cwd).resolve()
    client_value = env.get('CG_CLIENT_ROOT') or env.get('CLIENT_ROOT')
    product_value = env.get('CG_PRODUCT_ROOT')
    if not client_value or not product_value:
        raise ValueError('Set CG_CLIENT_ROOT to the training repo root and CG_PRODUCT_ROOT to your assigned data_products product. See README: Your working folder.')
    client = Path(client_value).resolve()
    if not (client / 'data_products').is_dir() or not (client / '.mise.toml').is_file():
        raise ValueError('CG_CLIENT_ROOT must be the training repo root containing .mise.toml and data_products/.')
    product = Path(product_value).resolve()
    if root != product or current != product:
        raise ValueError(f'Wrong working folder. Run this product\'s commands from {product}; current folder is {current} and script belongs to {root}.')
    # Resolve symlinks before testing ownership; a link to a challenge is not a product.
    if product.parent != (client / 'data_products').resolve():
        raise ValueError('Work in your own product directly under data_products/. challenges/ contains templates, not your working product.')
    assignment_path = product / '.capstone-workspace.json'
    if not assignment_path.is_file():
        raise ValueError('Missing instructor-supplied .capstone-workspace.json. Ask for the assignment for this product; do not guess a schema or copy another learner\'s assignment.')
    assignment = json.loads(assignment_path.read_text())
    required = {'product_name': product.name, 'catalog': 'DBT_CATALOG', 'schema': 'DBT_SCHEMA', 'relation_prefix': 'DC_RELATION_PREFIX'}
    for field, variable in required.items():
        expected = assignment.get(field)
        if not isinstance(expected, str) or not expected or 'REPLACE' in expected.upper():
            raise ValueError(f'Incomplete workspace assignment: {field}. The instructor must supply the assigned value.')
        actual = product.name if field == 'product_name' else env.get(variable)
        if expected != actual:
            raise ValueError(f'Workspace target mismatch for {field}: assigned {expected}, received {actual or "<unset>"}. Restore the assigned settings before running dbt.')
    prefix = assignment['relation_prefix']
    if not re.fullmatch('[a-z][a-z0-9_]{2,55}', prefix):
        raise ValueError('Assigned relation prefix is invalid.')
    if not (product / 'dbt_project.yml').is_file() or not (product / 'profiles.yml').is_file():
        raise ValueError('This folder does not contain the CG dbt project and profile.')
    return {'product_root': str(product), 'client_root': str(client),
            'project_file': str(product / 'dbt_project.yml'), 'profile_file': str(product / 'profiles.yml'),
            'target': 'training', 'catalog': assignment['catalog'], 'schema': assignment['schema'],
            'relation_prefix': prefix}
