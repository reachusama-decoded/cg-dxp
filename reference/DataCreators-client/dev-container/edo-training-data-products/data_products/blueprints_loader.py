import os
from pathlib import Path

from airflow.sdk import BaseOperatorLink
from airflow.models.taskinstancekey import TaskInstanceKey
from blueprint import build_all
from blueprint.registry import BlueprintRegistry

_default_config_root = (
    os.getenv("AIRFLOW__CORE__DAGS_FOLDER")
    or os.getenv("DAGS_FOLDER")
    or str(Path(__file__).parent)
)
CONFIG_ROOT_DIR = Path(os.getenv("CONFIG_ROOT_DIR", _default_config_root))

GITHUB_REPO_URL = "https://github.com/cg-open-itg/edo-training-data-products"
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "develop")
DEFAULT_POLICY_TAGS = [
    os.getenv("AIRFLOW_DEFAULT_USAGE_ID_TAG", "usage-id:AA00002933"),
    os.getenv("AIRFLOW_DEFAULT_COST_CENTER_TAG", "cost-center:52415"),
]


def merge_tags_with_defaults(existing_tags: list[str]) -> list[str]:
    defaults_by_key: dict[str, str] = {}
    passthrough_defaults: list[str] = []
    for tag in DEFAULT_POLICY_TAGS:
        if ":" in tag:
            key, value = tag.split(":", 1)
            defaults_by_key[key] = value
        else:
            passthrough_defaults.append(tag)

    merged_by_key = defaults_by_key.copy()
    passthrough = []
    for tag in existing_tags:
        if ":" in tag:
            key, value = tag.split(":", 1)
            merged_by_key[key] = value
        else:
            passthrough.append(tag)

    merged = [f"{key}:{value}" for key, value in merged_by_key.items()]
    merged.extend(passthrough_defaults)
    merged.extend(passthrough)
    return merged


class DatasetGitHubLink(BaseOperatorLink):
    name = "Dataset in GitHub"

    def get_link(self, operator, *, ti_key: TaskInstanceKey):
        dag_id = ti_key.dag_id
        # Find the DAG config file that produced this DAG to derive the dataset path
        for pattern in ("**/airflow/*.dag.yml", "**/airflow/*.dag.yaml"):
            for config_file in CONFIG_ROOT_DIR.rglob(pattern):
                try:
                    import yaml
                    with config_file.open() as f:
                        cfg = yaml.safe_load(f)
                    if cfg and cfg.get("dag_id") == dag_id:
                        # dataset path is 2 levels up from the airflow/ dir
                        dataset_path = config_file.parent.parent
                        relative = dataset_path.relative_to(CONFIG_ROOT_DIR)
                        return f"{GITHUB_REPO_URL}/tree/{GITHUB_BRANCH}/data_products/{relative}"
                except Exception:
                    continue
        return f"{GITHUB_REPO_URL}/tree/{GITHUB_BRANCH}/data_products"

# Tell the blueprint registry where to find the blueprint python files
blueprint_dir = CONFIG_ROOT_DIR / ".blueprints"
os.environ["BLUEPRINT_TEMPLATE_PATH"] = str(blueprint_dir)

registry = BlueprintRegistry(template_dirs=[blueprint_dir])

BLUEPRINT_TAG = "blueprint_factory"

# Load .dag.yml files
before_keys = set(globals())
build_all(
    search_path=str(CONFIG_ROOT_DIR),
    pattern="**/airflow/*.dag.yml",
    register_globals=globals(),
    bp_registry=registry
)

# Load .dag.yaml files
build_all(
    search_path=str(CONFIG_ROOT_DIR),
    pattern="**/airflow/*.dag.yaml",
    register_globals=globals(),
    bp_registry=registry
)

# Tag all blueprint-generated DAGs and add GitHub link
_github_link = DatasetGitHubLink()
for key in set(globals()) - before_keys:
    dag_obj = globals().get(key)
    if dag_obj is not None and hasattr(dag_obj, "tags"):
        tags = merge_tags_with_defaults(list(dag_obj.tags or []))
        if BLUEPRINT_TAG not in tags:
            tags.append(BLUEPRINT_TAG)
        dag_obj.tags = tags
        # Add GitHub link to all tasks in the DAG
        for task in getattr(dag_obj, "tasks", []):
            links = list(getattr(task, "operator_extra_links", []))
            if not any(isinstance(l, DatasetGitHubLink) for l in links):
                links.append(_github_link)
                task.operator_extra_links = tuple(links)
