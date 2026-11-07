"""
Data Quality & Relational Validation Module
-------------------------------------------
Automates structural schema inspections, key uniqueness checks,
and referential integrity validation across raw Olist datasets.
"""

from typing import Dict, List, Tuple
import pandas as pd
from ecommerce_analytics.config import ConfigManager
from ecommerce_analytics.data_loader import DataLoader


class DataValidator:
    """Validates schema structure, primary key uniqueness, and foreign key integrity."""

    def __init__(self, data_loader: DataLoader = None) -> None:
        self.loader = data_loader or DataLoader()
        self.datasets: Dict[str, pd.DataFrame] = self.loader.load_all_datasets()

    def inspect_dataset_shapes(self) -> pd.DataFrame:
        """Returns row counts, column counts, missing value counts, and memory footprint."""
        summary = []
        for name, df in self.datasets.items():
            summary.append({
                "dataset": name,
                "rows": df.shape[0],
                "columns": df.shape[1],
                "total_missing_cells": int(df.isnull().sum().sum()),
                "duplicate_rows": int(df.duplicated().sum()),
                "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
            })
        return pd.DataFrame(summary)

    def verify_primary_keys(self) -> pd.DataFrame:
        """Validates primary key candidate uniqueness across datasets."""
        pk_mapping = {
            "customers": ["customer_id"],
            "orders": ["order_id"],
            "order_items": ["order_id", "order_item_id"],
            "order_payments": ["order_id", "payment_sequential"],
            "order_reviews": ["review_id"],
            "products": ["product_id"],
            "sellers": ["seller_id"],
            "category_translation": ["product_category_name"]
        }

        results = []
        for dataset_name, pk_cols in pk_mapping.items():
            if dataset_name not in self.datasets:
                continue
            
            df = self.datasets[dataset_name]
            total_rows = len(df)
            unique_keys = len(df.drop_duplicates(subset=pk_cols))
            is_unique = total_rows == unique_keys
            null_keys = df[pk_cols].isnull().any().to_dict()

            results.append({
                "dataset": dataset_name,
                "primary_key": ", ".join(pk_cols),
                "total_rows": total_rows,
                "unique_key_count": unique_keys,
                "is_unique": is_unique,
                "has_null_in_pk": any(null_keys.values())
            })

        return pd.DataFrame(results)

    def check_referential_integrity(self) -> pd.DataFrame:
        """Verifies foreign key relationships between tables."""
        relationships = [
            ("orders", "customer_id", "customers", "customer_id"),
            ("order_items", "order_id", "orders", "order_id"),
            ("order_items", "product_id", "products", "product_id"),
            ("order_items", "seller_id", "sellers", "seller_id"),
            ("order_payments", "order_id", "orders", "order_id"),
            ("order_reviews", "order_id", "orders", "order_id"),
        ]

        results = []
        for child_df_name, child_fk, parent_df_name, parent_pk in relationships:
            if child_df_name not in self.datasets or parent_df_name not in self.datasets:
                continue

            child_df = self.datasets[child_df_name]
            parent_df = self.datasets[parent_df_name]

            child_keys = set(child_df[child_fk].dropna())
            parent_keys = set(parent_df[parent_pk].dropna())

            orphaned_keys = child_keys - parent_keys
            match_percentage = round((len(child_keys - orphaned_keys) / len(child_keys)) * 100, 2) if child_keys else 0.0

            results.append({
                "child_table": child_df_name,
                "foreign_key": child_fk,
                "parent_table": parent_df_name,
                "parent_key": parent_pk,
                "orphaned_keys_count": len(orphaned_keys),
                "match_percentage": match_percentage
            })

        return pd.DataFrame(results)


if __name__ == "__main__":
    validator = DataValidator()
    print("--- DATASET SUMMARY ---")
    print(validator.inspect_dataset_shapes().to_string(index=False))
    print("\n--- PRIMARY KEY INTEGRITY ---")
    print(validator.verify_primary_keys().to_string(index=False))
    print("\n--- REFERENTIAL INTEGRITY (FOREIGN KEYS) ---")
    print(validator.check_referential_integrity().to_string(index=False))