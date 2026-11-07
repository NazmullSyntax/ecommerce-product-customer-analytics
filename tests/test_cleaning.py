import pandas as pd

from ecommerce_analytics.cleaning import clean_table
from ecommerce_analytics.transformation import order_line_revenue


def test_clean_table_trims_deduplicates_and_drops_missing_customer():
    source = pd.DataFrame(
        {"customer_id": ["c1", "c1", None], "name": [" Alice ", " Alice ", " Bob "]}
    )

    result = clean_table(source, {"missing_customer_id": "drop"})

    assert result.to_dict("records") == [{"customer_id": "c1", "name": "Alice"}]


def test_order_line_revenue_calculates_price_times_quantity():
    result = order_line_revenue(pd.DataFrame({"price": [4.5], "quantity": [2]}))

    assert result["line_revenue"].tolist() == [9.0]
