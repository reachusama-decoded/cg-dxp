"""CG capstone preparation copies the template once into an owned product."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('cg_prepare', ROOT / 'scripts/cg-prepare.py')
cg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cg)


@pytest.fixture
def client(tmp_path):
    template = tmp_path / cg.TEMPLATE
    (template / 'docs').mkdir(parents=True)
    (template / 'dbt_project.yml').write_text('name: cg\n')
    (template / 'docs/EVIDENCE.md').write_text('evidence\n')
    (template / '.env').write_text('DBT_ACCESS_TOKEN=secret\n')
    (template / '.local').mkdir()
    (template / '.local/run.json').write_text('{}\n')
    (tmp_path / 'data_products').mkdir()
    return tmp_path


def test_prepare_copies_template_without_secrets_or_state(client):
    product, count, record = cg.prepare(client, 'cg_public_products_alex', 'training_dev', 'training_alex', 'cg_alex')
    assert product == client / 'data_products/cg_public_products_alex'
    assert count == 2 and (product / 'docs/EVIDENCE.md').is_file()
    assert not (product / '.env').exists() and not (product / '.local').exists()
    assert json.loads((product / '.capstone-workspace.json').read_text()) == record == {
        'product_name': 'cg_public_products_alex', 'catalog': 'training_dev',
        'schema': 'training_alex', 'relation_prefix': 'cg_alex'}


def test_prepare_never_overwrites_existing_work(client):
    product, _, _ = cg.prepare(client, 'cg_public_products_alex')
    (product / 'dbt_project.yml').write_text('name: learner_edit\n')
    with pytest.raises(SystemExit, match='already exists'):
        cg.prepare(client, 'cg_public_products_alex')
    assert (product / 'dbt_project.yml').read_text() == 'name: learner_edit\n'
    assert cg.diff(client, 'cg_public_products_alex') == [('differs', 'dbt_project.yml')]


@pytest.mark.parametrize('name', ['alex', 'cg_public_products_', 'cg_public_products_Alex',
                                  'cg_public_products_../x', 'portfolio_analytics'])
def test_prepare_rejects_names_outside_the_cg_namespace(client, name):
    with pytest.raises(SystemExit):
        cg.prepare(client, name)
    assert sorted(p.name for p in (client / 'data_products').iterdir()) == []


def test_prepare_rejects_partial_invalid_or_shared_assignments(client):
    with pytest.raises(SystemExit, match='together'):
        cg.prepare(client, 'cg_public_products_alex', 'training_dev')
    with pytest.raises(SystemExit, match='Invalid prefix'):
        cg.prepare(client, 'cg_public_products_alex', 'training_dev', 'training_alex', 'REPLACE_ME')
    cg.prepare(client, 'cg_public_products_alex', 'training_dev', 'training_alex', 'cg_alex')
    with pytest.raises(SystemExit, match='already assigned'):
        cg.prepare(client, 'cg_public_products_sam', 'training_dev', 'training_sam', 'cg_alex')
    assert not (client / 'data_products/cg_public_products_sam').exists()


def test_real_template_is_ready_for_the_shared_astro_runtime():
    template = ROOT / cg.TEMPLATE
    assert (template / 'README.md').is_file() and (template / 'dbt_project.yml').is_file()
    # Airflow 3 reads .airflowignore as glob patterns: only dags/*.py may be parsed.
    assert (template / '.airflowignore').read_text().splitlines()[1:] == ['*', '!dags/', '!dags/*.py']
    # A regular include package would shadow other products' namespace include/ on the shared path.
    assert not (template / 'include/__init__.py').exists()
    assert not (template / 'orchestration').exists() and not (template / '.mise.toml').exists()
    assert 'data_products/cg_public_products_*/' in (ROOT / '.gitignore').read_text().splitlines()
