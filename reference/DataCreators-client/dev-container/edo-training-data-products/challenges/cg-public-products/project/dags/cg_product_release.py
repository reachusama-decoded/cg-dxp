"""AUTHOR phase 2: wire the release DAG using supplied runtime task interfaces.

Do not import unfinished phase-3 blueprint behavior until you enable its DAGs.
The neutral smoke DAG is supplied separately so environment checks work first.
Keep the import block below: Airflow shares one worker between all products.
Name the DAG dag_id('product_release'), add REQUIRED_TAGS to its tags and use an
owned prefix such as assignment()['relation_prefix'] + '_release' (all from
runtime.product).
"""
import sys
from pathlib import Path

# Every CG product ships runtime/ and include/ packages; load only this product's copies.
ROOT = Path(__file__).resolve().parents[1]
for _name in [n for n in sys.modules if n.split('.')[0] in ('runtime', 'include')]:
    if not str(getattr(sys.modules[_name], '__file__', None) or '').startswith(str(ROOT) + '/'):
        del sys.modules[_name]
sys.path.insert(0, str(ROOT))

# AUTHOR: define the single team release DAG and custom on_failure_callback.
