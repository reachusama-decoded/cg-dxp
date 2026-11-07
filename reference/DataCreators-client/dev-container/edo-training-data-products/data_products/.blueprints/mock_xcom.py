import importlib.util
from pathlib import Path

from airflow.operators.python import PythonOperator
from blueprint import BaseModel, Blueprint

_SRC_DIR = Path(__file__).parent / "src"


def _load_generate_mock_xcom():
    spec = importlib.util.spec_from_file_location(
        "mock_xcom_generator", _SRC_DIR / "mock_xcom_generator.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate_mock_xcom


class MockXcomConfig(BaseModel):
    domain: str
    model:  str


class MockXcom(Blueprint[MockXcomConfig]):
    def render(self, config: MockXcomConfig) -> PythonOperator:
        return PythonOperator(
            task_id=self.step_id,
            python_callable=_load_generate_mock_xcom(),
            op_kwargs={"domain": config.domain, "model": config.model},
        )
