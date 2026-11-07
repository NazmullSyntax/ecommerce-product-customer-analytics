"""Read and write tabular ecommerce data."""

from pathlib import Path
from typing import Mapping

import pandas as pd


def load_csv(path: str | Path, **read_csv_kwargs: object) -> pd.DataFrame:
    """Read one CSV file, raising the original filesystem or parser error on failure."""
    return pd.read_csv(path, **read_csv_kwargs)


def load_tables(config: Mapping[str, object]) -> dict[str, pd.DataFrame]:
    """Load configured CSV tables from the raw data directory."""
    raw_dir = Path(config["paths"]["raw"])  # type: ignore[index]
    filenames = config["files"]
    tables: dict[str, pd.DataFrame] = {}
    for name, filename in filenames.items():  # type: ignore[union-attr]
        path = raw_dir / filename
        if path.exists():
            tables[name] = load_csv(path)
    if not tables:
        raise FileNotFoundError(
            f"No configured CSV files found in {raw_dir}. Add source data or update config/config.yaml."
        )
    return tables


def save_tables(tables: Mapping[str, pd.DataFrame], output_dir: str | Path) -> None:
    """Save tables as CSV files, creating the destination directory when needed."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(destination / f"{name}.csv", index=False)
