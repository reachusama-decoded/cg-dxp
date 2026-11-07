"""Metadata differences must not weaken the merged local/connected money check."""
import importlib.util

import pytest

from tests.challenges.conftest import repo_root


@pytest.mark.parametrize("connected", [False, True])
@pytest.mark.parametrize("column_type,accepted", [("decimal(18, 2)", True), ("DECIMAL", False), ("DECIMAL(18,3)", False), ("DOUBLE", False)])
def test_exposure_checks_precision_in_the_selected_schema(tmp_path, monkeypatch, connected, column_type, accepted):
    spec = importlib.util.spec_from_file_location("merged_verifier", repo_root() / "scripts/challenge-v2.py")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    verifier.CONNECTED = {"schema": "assigned_training"} if connected else None
    seeds = tmp_path / "seeds"
    seeds.mkdir()
    (seeds / "funds.csv").write_text("fund_id,fund_name\nA,Alpha\n")
    (seeds / "holdings.csv").write_text("fund_id,instrument_id,market_value\nA,i1,10.00\n")
    def observed(workspace, sql):
        if sql.startswith("select fund_id,holdings"):
            return [["A", 1, "10.00"]]
        if sql.startswith("select fund_id,instrument_id"):
            return [["A", "i1", "10.00"]]
        expected_column = "full_data_type" if connected else "data_type"
        expected_schema = "assigned_training" if connected else "main"
        assert sql.startswith(f"select {expected_column} ")
        assert f"table_schema='{expected_schema}'" in sql
        return [[column_type]]
    monkeypatch.setattr(verifier, "query", observed)
    if accepted:
        assert verifier.exposure(tmp_path) == [["A", 1, "10.00"]]
    else:
        with pytest.raises(AssertionError, match="Money contract"):
            verifier.exposure(tmp_path)
