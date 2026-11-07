#!/usr/bin/env python3
"""Create a learner's owned CG capstone product from the challenge template.

  prepare NAME [--catalog C --schema S --prefix P]   copy the template once
  diff NAME                                          list template files that differ

NAME must be cg_public_products_<owner-or-pair>. Existing products are never
overwritten; template updates reach new products only.
"""
import argparse
import fnmatch
import json
import os
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = Path('challenges/cg-public-products/project')
NAME = re.compile(r'cg_public_products_[a-z0-9][a-z0-9_]{1,39}')
IDENTIFIER = re.compile(r'[a-z][a-z0-9_]{1,62}')
PREFIX = re.compile(r'[a-z][a-z0-9_]{2,55}')
SKIP_DIRECTORIES = {'.git', '.local', '.venv', '.verification-venv', 'venv', 'target', 'logs',
                    '__pycache__', '.pytest_cache', 'dbt_packages', 'evidence'}
SKIP_FILES = ('.env', '.user.yml', '*.pyc', '*.duckdb*', '.DS_Store', '.capstone-workspace.json')


def template_files(template):
    files = {}
    for directory, names, entries in os.walk(template):
        names[:] = sorted(n for n in names if n not in SKIP_DIRECTORIES)
        for name in sorted(entries):
            if any(fnmatch.fnmatch(name, pattern) for pattern in SKIP_FILES):
                continue
            path = Path(directory) / name
            if path.is_symlink():
                raise SystemExit('Template may not contain symlinks: ' + str(path))
            files[path.relative_to(template).as_posix()] = path
    return files


def product_path(client, name):
    if not NAME.fullmatch(name):
        raise SystemExit('Product name must look like cg_public_products_<owner>, '
                         'using lowercase letters, digits and underscores.')
    return client / 'data_products' / name


def assignment(client, name, catalog, schema, prefix):
    values = [catalog, schema, prefix]
    if not any(values):
        return None
    if not all(values):
        raise SystemExit('Give --catalog, --schema and --prefix together, or none of them.')
    for label, value, pattern in [('catalog', catalog, IDENTIFIER), ('schema', schema, IDENTIFIER),
                                  ('prefix', prefix, PREFIX)]:
        if not pattern.fullmatch(value):
            raise SystemExit(f'Invalid {label}: {value}')
    for other in sorted((client / 'data_products').glob('cg_public_products_*/.capstone-workspace.json')):
        existing = json.loads(other.read_text())
        if existing.get('relation_prefix') == prefix and other.parent.name != name:
            raise SystemExit(f'Prefix {prefix} is already assigned to {other.parent.name}; '
                             'each product needs its own prefix.')
    return {'product_name': name, 'catalog': catalog, 'schema': schema, 'relation_prefix': prefix}


def prepare(client, name, catalog=None, schema=None, prefix=None):
    template = client / TEMPLATE
    destination = product_path(client, name)
    files = template_files(template)
    if 'dbt_project.yml' not in files:
        raise SystemExit('Missing CG challenge template: ' + str(template))
    if destination.exists() or destination.is_symlink():
        raise SystemExit(f'{destination} already exists. Keep working there; '
                         'nothing was copied or overwritten.')
    record = assignment(client, name, catalog, schema, prefix)
    staging = destination.with_name('.' + name + '.preparing')
    if staging.exists():
        shutil.rmtree(staging)
    try:
        for rel, source in files.items():
            target = staging / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            shutil.copymode(source, target)
        if record:
            (staging / '.capstone-workspace.json').write_text(json.dumps(record, indent=2) + '\n')
        staging.rename(destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination, len(files), record


def diff(client, name):
    destination = product_path(client, name)
    if not destination.is_dir():
        raise SystemExit(f'No product at {destination}')
    changed = []
    for rel, source in template_files(client / TEMPLATE).items():
        target = destination / rel
        if not target.is_file():
            changed.append(('missing', rel))
        elif target.read_bytes() != source.read_bytes():
            changed.append(('differs', rel))
    return changed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--client-root', type=Path, default=ROOT, help=argparse.SUPPRESS)
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('prepare', help='copy the template into data_products/NAME once')
    create.add_argument('name')
    create.add_argument('--catalog')
    create.add_argument('--schema')
    create.add_argument('--prefix', help='assigned relation prefix (DC_RELATION_PREFIX)')
    compare = commands.add_parser('diff', help='list template files that differ from the product')
    compare.add_argument('name')
    args = parser.parse_args(argv)
    client = args.client_root.resolve()
    if args.command == 'prepare':
        destination, count, record = prepare(client, args.name, args.catalog, args.schema, args.prefix)
        print(f'Created {destination} from {TEMPLATE} ({count} files).')
        if not record:
            print('No .capstone-workspace.json written: add the instructor-assigned catalog, schema and prefix.')
        print('Next: follow "Your working folder" in its README.md.')
    else:
        changed = diff(client, args.name)
        for state, rel in changed:
            print(f'{state}\t{rel}')
        print(f'{len(changed)} template file(s) differ; nothing was changed.', file=sys.stderr)


if __name__ == '__main__':
    main()
