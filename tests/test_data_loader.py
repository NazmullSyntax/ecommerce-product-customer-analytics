import pandas as pd
import pytest

from ecommerce_analytics.data_loader import load_csv, load_tables, save_tables


def test_load_csv_reads_records(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text("id,value\n1,example\n", encoding="utf-8")

    result = load_csv(source)

    assert result.to_dict("records") == [{"id": 1, "value": "example"}]


def test_load_tables_ignores_missing_optional_files_and_errors_if_none_exist(tmp_path):
    config = {
        "paths": {"raw": str(tmp_path)},
        "files": {"customers": "customers.csv"},
    }

    with pytest.raises(FileNotFoundError, match="No configured CSV files"):
        load_tables(config)


def test_save_tables_creates_directory_and_writes_csv(tmp_path):
    output = tmp_path / "nested" / "processed"

    save_tables({"orders": pd.DataFrame({"order_id": ["o1"]})}, output)

    assert pd.read_csv(output / "orders.csv").iloc[0]["order_id"] == "o1"
