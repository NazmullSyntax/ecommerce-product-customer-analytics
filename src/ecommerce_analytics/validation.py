"""Data profiling and schema validation."""

import pandas as pd


def profile_table(table: pd.DataFrame) -> pd.DataFrame:
    """Summarize dtype, missing count, missing rate, and distinct values by column."""
    return pd.DataFrame(
        {
            "dtype": table.dtypes.astype(str),
            "missing_count": table.isna().sum(),
            "missing_rate": table.isna().mean(),
            "distinct_count": table.nunique(dropna=True),
        }
    )


def require_columns(table: pd.DataFrame, columns: list[str], table_name: str = "table") -> None:
    """Raise a clear error if required columns are absent."""
    missing = sorted(set(columns) - set(table.columns))
    if missing:
        raise ValueError(f"{table_name} is missing required columns: {', '.join(missing)}")
