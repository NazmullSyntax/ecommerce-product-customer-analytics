"""Reusable customer, product, and sales metrics."""

import pandas as pd

from .transformation import order_line_revenue
from .validation import require_columns


def monthly_sales(
    orders: pd.DataFrame,
    date_column: str = "order_date",
    revenue_column: str = "revenue",
) -> pd.DataFrame:
    """Aggregate revenue and order count by calendar month."""
    require_columns(orders, [date_column, revenue_column], "orders")
    result = orders[[date_column, revenue_column]].copy()
    result[date_column] = pd.to_datetime(result[date_column], errors="coerce")
    result[revenue_column] = pd.to_numeric(result[revenue_column], errors="coerce")
    result = result.dropna(subset=[date_column])
    result["month"] = result[date_column].dt.to_period("M").astype(str)
    return (
        result.groupby("month", as_index=False)
        .agg(revenue=(revenue_column, "sum"), order_count=(date_column, "size"))
        .sort_values("month")
        .reset_index(drop=True)
    )


def customer_metrics(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    customer_column: str = "customer_id",
    revenue_column: str = "revenue",
) -> pd.DataFrame:
    """Calculate order count and revenue per customer, joined to customer attributes."""
    require_columns(orders, [customer_column, revenue_column], "orders")
    require_columns(customers, [customer_column], "customers")
    order_values = orders[[customer_column, revenue_column]].copy()
    order_values[revenue_column] = pd.to_numeric(order_values[revenue_column], errors="coerce")
    metrics = order_values.groupby(customer_column, as_index=False).agg(
        order_count=(revenue_column, "size"), revenue=(revenue_column, "sum")
    )
    return customers.merge(metrics, on=customer_column, how="left")


def product_metrics(
    order_items: pd.DataFrame,
    products: pd.DataFrame,
    product_column: str = "product_id",
) -> pd.DataFrame:
    """Calculate units and revenue per product, joined to product attributes."""
    require_columns(order_items, [product_column, "price", "quantity"], "order_items")
    require_columns(products, [product_column], "products")
    items = order_line_revenue(order_items)
    metrics = items.groupby(product_column, as_index=False).agg(
        units_sold=("quantity", "sum"), revenue=("line_revenue", "sum")
    )
    return products.merge(metrics, on=product_column, how="left")
