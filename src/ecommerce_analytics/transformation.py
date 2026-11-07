"""
Data Transformation & Feature Engineering Module
------------------------------------------------
Enriches cleaned data with business features: delivery metrics, English category mappings,
customer order aggregations, and master analytical tables for SQL/Power BI ingestion.
"""

from pathlib import Path
from typing import Dict
import pandas as pd
import numpy as np
from ecommerce_analytics.config import ConfigManager
from ecommerce_analytics.cleaning import DataCleaner


class DataTransformer:
    """Transforms cleaned data into analytical datasets and feature-engineered tables."""

    def __init__(self, config: ConfigManager = None, cleaner: DataCleaner = None) -> None:
        self.config = config or ConfigManager()
        self.cleaner = cleaner or DataCleaner()
        self.cleaned_data: Dict[str, pd.DataFrame] = self.cleaner.run_all_cleaning()
        self.processed_path = self.config.get_path("processed_data")

    def transform_products_with_translation(self) -> pd.DataFrame:
        """Merges products table with English category translations."""
        products = self.cleaned_data["products"]
        translations = self.cleaned_data["category_translation"]

        merged_products = products.merge(
            translations,
            on="product_category_name",
            how="left"
        )

        # Fallback if any unmapped categories remain
        merged_products["product_category_name_english"] = merged_products["product_category_name_english"].fillna(
            merged_products["product_category_name"]
        )
        return merged_products

    def transform_order_features(self) -> pd.DataFrame:
        """Enriches orders with delivery duration, delay flags, and time dimensions."""
        orders = self.cleaned_data["orders"].copy()

        # Delivery Time in Days (Actual vs Estimated)
        orders["actual_delivery_days"] = (
            orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]
        ).dt.total_seconds() / (24 * 3600)

        orders["estimated_delivery_days"] = (
            orders["order_estimated_delivery_date"] - orders["order_purchase_timestamp"]
        ).dt.total_seconds() / (24 * 3600)

        # Shipping delay in days (Positive = Late, Negative = Early)
        orders["delivery_delay_days"] = (
            orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]
        ).dt.total_seconds() / (24 * 3600)

        # Late delivery boolean flag (1 if delivered after estimated date, else 0)
        orders["is_late_delivery"] = np.where(
            orders["delivery_delay_days"] > 0, 1, 0
        )

        # Time components for seasonality analysis
        orders["purchase_year"] = orders["order_purchase_timestamp"].dt.year
        orders["purchase_month"] = orders["order_purchase_timestamp"].dt.month
        orders["purchase_year_month"] = orders["order_purchase_timestamp"].dt.to_period("M").astype(str)
        orders["purchase_day_of_week"] = orders["order_purchase_timestamp"].dt.day_name()
        orders["purchase_hour"] = orders["order_purchase_timestamp"].dt.hour

        return orders

    def build_master_order_items(self) -> pd.DataFrame:
        """Denormalizes order items with product, customer, seller, and order metadata."""
        items = self.cleaned_data["order_items"].copy()
        orders = self.transform_order_features()
        customers = self.cleaned_data["customers"]
        products_translated = self.transform_products_with_translation()
        sellers = self.cleaned_data["sellers"]

        # Calculate item total spend
        items["item_total_value"] = items["price"] + items["freight_value"]

        # Master Merge
        master_df = items.merge(orders, on="order_id", how="inner")
        master_df = master_df.merge(customers, on="customer_id", how="left")
        master_df = master_df.merge(products_translated, on="product_id", how="left")
        master_df = master_df.merge(sellers, on="seller_id", how="left")

        return master_df

    def export_processed_datasets(self) -> None:
        """Exports all transformed datasets to parquet and CSV in data/processed/."""
        self.processed_path.mkdir(parents=True, exist_ok=True)
        
        # Prepare datasets
        datasets_to_export = {
            "dim_customers": self.cleaned_data["customers"],
            "dim_products": self.transform_products_with_translation(),
            "dim_sellers": self.cleaned_data["sellers"],
            "fact_orders": self.transform_order_features(),
            "fact_order_items": self.cleaned_data["order_items"],
            "fact_order_payments": self.cleaned_data["order_payments"],
            "fact_order_reviews": self.cleaned_data["order_reviews"],
            "master_order_items": self.build_master_order_items()
        }

        print("--- EXPORTING PROCESSED DATASETS ---")
        for name, df in datasets_to_export.items():
            csv_file = self.processed_path / f"{name}.csv"
            parquet_file = self.processed_path / f"{name}.parquet"

            df.to_csv(csv_file, index=False)
            df.to_parquet(parquet_file, index=False)
            print(f"Exported {name}: {len(df):,} rows -> {csv_file.name} & {parquet_file.name}")


if __name__ == "__main__":
    transformer = DataTransformer()
    transformer.export_processed_datasets()