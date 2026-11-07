"""
Data Loading Engine Module
--------------------------
Handles loading CSV datasets safely with explicit verification checks.
"""

import pandas as pd
from typing import Dict
from ecommerce_analytics.config import ConfigManager

class DataLoader:
    """Loads and validates input datasets from storage."""

    def __init__(self, config: ConfigManager = None) -> None:
        self.config = config or ConfigManager()
        self.raw_data_path = self.config.get_path("raw_data")

    def load_single_csv(self, filename: str) -> pd.DataFrame:
        """Loads a single raw CSV dataset into a pandas DataFrame."""
        file_path = self.raw_data_path / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file missing: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            raise IOError(f"Error reading dataset file {filename}: {str(e)}")

    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Loads all Olist e-commerce datasets into a key-value dictionary."""
        files = {
            "customers": "olist_customers_dataset.csv",
            "orders": "olist_orders_dataset.csv",
            "order_items": "olist_order_items_dataset.csv",
            "order_payments": "olist_order_payments_dataset.csv",
            "order_reviews": "olist_order_reviews_dataset.csv",
            "products": "olist_products_dataset.csv",
            "sellers": "olist_sellers_dataset.csv",
            "category_translation": "product_category_name_translation.csv"
        }
        
        loaded_data = {}
        for key, fname in files.items():
            path = self.raw_data_path / fname
            if path.exists():
                loaded_data[key] = pd.read_csv(path)
                print(f"Loaded {key}: {loaded_data[key].shape[0]} rows, {loaded_data[key].shape[1]} columns.")
            else:
                print(f"Warning: File {fname} not found in {self.raw_data_path}.")
                
        return loaded_data

if __name__ == "__main__":
    loader = DataLoader()
    print("DataLoader instantiated successfully.")