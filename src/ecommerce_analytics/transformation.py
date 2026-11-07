"""Common ecommerce table transformations."""

import pandas as pd

from .validation import require_columns


def order_line_revenue(
    order_items: pd.DataFrame,
    price_column: str = "price",
    quantity_column: str = "quantity",
) -> pd.DataFrame:
    """Return a copy of order items with a calculated line_revenue column."""
    require_columns(order_items, [price_column, quantity_column], "order_items")
    result = order_items.copy()
    result["line_revenue"] = (
        pd.to_numeric(result[price_column], errors="coerce")
        * pd.to_numeric(result[quantity_column], errors="coerce")
    )
    return result
