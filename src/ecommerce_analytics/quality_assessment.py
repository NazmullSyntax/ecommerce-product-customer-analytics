"""
Data Quality Assessment Engine Module
-------------------------------------
Performs deep structural data quality diagnostics, including missing value profiling,
timestamp sequence validation, price/freight range sanity checks, and category lookup auditing.
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from ecommerce_analytics.config import ConfigManager
from ecommerce_analytics.data_loader import DataLoader


class DataQualityAssessor:
    """Automates comprehensive quality audits across all dataset tables."""

    def __init__(self, loader: DataLoader = None) -> None:
        self.loader = loader or DataLoader()
        self.datasets: Dict[str, pd.DataFrame] = self.loader.load_all_datasets()

    def get_missing_values_report(self) -> pd.DataFrame:
        """Generates a detailed inventory of missing values per dataset and column."""
        missing_records = []
        for dataset_name, df in self.datasets.items():
            null_counts = df.isnull().sum()
            null_percentages = (null_counts / len(df)) * 100

            for col in df.columns:
                if null_counts[col] > 0:
                    missing_records.append({
                        "dataset": dataset_name,
                        "column": col,
                        "missing_count": null_counts[col],
                        "missing_percentage": round(null_percentages[col], 2),
                        "data_type": str(df[col].dtype),
                        "total_rows": len(df)
                    })

        report_df = pd.DataFrame(missing_records)
        return report_df.sort_values(by="missing_percentage", ascending=False) if not report_df.empty else report_df

    def validate_order_timestamps(self) -> Dict[str, int]:
        """Checks for timestamp logical order anomalies in olist_orders_dataset."""
        orders_df = self.datasets["orders"].copy()
        
        # Convert date columns to datetime objects
        date_cols = [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]
        for col in date_cols:
            orders_df[col] = pd.to_datetime(orders_df[col])

        # Anomaly 1: Delivered to customer before purchase
        delivered_before_purchase = (
            orders_df["order_delivered_customer_date"] < orders_df["order_purchase_timestamp"]
        ).sum()

        # Anomaly 2: Delivered to customer before carrier pickup
        delivered_before_carrier = (
            orders_df["order_delivered_customer_date"] < orders_df["order_delivered_carrier_date"]
        ).sum()

        # Anomaly 3: Approved before purchase timestamp
        approved_before_purchase = (
            orders_df["order_approved_at"] < orders_df["order_purchase_timestamp"]
        ).sum()

        # Anomaly 4: Late deliveries count (Delivered after estimated date)
        delivered_late = (
            orders_df["order_delivered_customer_date"] > orders_df["order_estimated_delivery_date"]
        ).sum()

        return {
            "delivered_before_purchase": int(delivered_before_purchase),
            "delivered_before_carrier": int(delivered_before_carrier),
            "approved_before_purchase": int(approved_before_purchase),
            "delivered_after_estimated_date": int(delivered_late)
        }

    def inspect_financial_anomalies(self) -> Dict[str, float]:
        """Detects zero/negative values or extreme statistical outliers in financial fields."""
        items_df = self.datasets["order_items"]
        payments_df = self.datasets["order_payments"]

        return {
            "zero_or_negative_price_count": int((items_df["price"] <= 0).sum()),
            "negative_freight_count": int((items_df["freight_value"] < 0).sum()),
            "zero_freight_count": int((items_df["freight_value"] == 0).sum()),
            "min_item_price": float(items_df["price"].min()),
            "max_item_price": float(items_df["price"].max()),
            "max_freight_value": float(items_df["freight_value"].max()),
            "zero_payment_value_count": int((payments_df["payment_value"] == 0).sum()),
            "min_payment_value": float(payments_df["payment_value"].min()),
            "max_payment_value": float(payments_df["payment_value"].max())
        }

    def inspect_unmapped_categories(self) -> Tuple[List[str], int]:
        """Identifies product categories present in products table but missing in translation table."""
        products_df = self.datasets["products"]
        translation_df = self.datasets["category_translation"]

        product_categories = set(products_df["product_category_name"].dropna().unique())
        translated_categories = set(translation_df["product_category_name"].unique())

        unmapped = list(product_categories - translated_categories)
        return unmapped, len(unmapped)


if __name__ == "__main__":
    assessor = DataQualityAssessor()
    print("--- MISSING VALUE AUDIT ---")
    print(assessor.get_missing_values_report().to_string(index=False))
    
    print("\n--- TIMESTAMP INTEGRITY CHECK ---")
    for key, val in assessor.validate_order_timestamps().items():
        print(f"  * {key}: {val:,}")

    print("\n--- FINANCIAL ANOMALY AUDIT ---")
    for key, val in assessor.inspect_financial_anomalies().items():
        print(f"  * {key}: {val}")

    unmapped_cats, count = assessor.inspect_unmapped_categories()
    print(f"\n--- UNMAPPED PRODUCT CATEGORIES ({count}) ---")
    print(f"  Categories missing translation: {unmapped_cats}")