"""Conservative, configurable table cleaning."""

from collections.abc import Mapping

import pandas as pd


def clean_table(table: pd.DataFrame, options: Mapping[str, object] | None = None) -> pd.DataFrame:
    """Trim text, remove exact duplicates, and optionally drop missing entity IDs."""
    settings = options or {}
    cleaned = table.copy()
    if settings.get("trim_string_values", True):
        for column in cleaned.select_dtypes(include=["object", "string"]).columns:
            cleaned[column] = cleaned[column].str.strip()
    if settings.get("drop_exact_duplicates", True):
        cleaned = cleaned.drop_duplicates()

    for column, option in (
        ("customer_id", settings.get("missing_customer_id")),
        ("product_id", settings.get("missing_product_id")),
    ):
        if option == "drop" and column in cleaned.columns:
            cleaned = cleaned.dropna(subset=[column])
    return cleaned.reset_index(drop=True)
