"""Factory entry point. Loads only after both configurations name this product."""
# Airflow only parses files that mention both "airflow" and "dag"; this line keeps the factory file visible.
import sys
from pathlib import Path

# Every CG product ships runtime/ and include/ packages; load only this product's copies.
ROOT = Path(__file__).resolve().parents[1]
for _name in [n for n in sys.modules if n.split('.')[0] in ('runtime', 'include')]:
    if not str(getattr(sys.modules[_name], '__file__', None) or '').startswith(str(ROOT) + '/'):
        del sys.modules[_name]
sys.path.insert(0, str(ROOT))

import json
from runtime.product import owned_prefix

configs = json.loads((ROOT / 'include' / 'blueprint-configs.json').read_text())
# Placeholder IDs keep this file inert until you name both DAGs for your product.
if all(c['dag_id'].startswith(ROOT.name + '__') for c in configs):
    from include.blueprint import build_blueprint
    if len({c['dag_id'] for c in configs}) != len(configs) or len({c['relation_prefix'] for c in configs}) != len(configs):
        raise ValueError('Blueprint configs require distinct DAG IDs and owned prefixes')
    for cfg in configs:
        owned_prefix(cfg['relation_prefix'])
        dag = build_blueprint(cfg)
        globals()[dag.dag_id] = dag
