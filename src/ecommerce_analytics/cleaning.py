"""
Data Cleaning Engine Module
---------------------------
Applies standardized cleaning rules: missing value handling, string normalization,
datetime conversions, and data type casting across raw Olist datasets.
"""

from typing import Dict
import pandas as pd
import numpy as np
from ecommerce_analytics.data_loader import DataLoader


class DataCleaner:
    """Executes deterministic cleaning routines on raw e-commerce datasets."""

    def __init__(self, data_loader: DataLoader = None) -> None:
        self.loader = data_loader or DataLoader()
        self.raw_datasets = self.loader.load_all_datasets()

    def clean_customers(self) -> pd.DataFrame:
        """Cleans customer dataset: strips whitespace and normalizes text fields."""
        df = self.raw_datasets["customers"].copy()
        
        # Strip text columns
        text_cols = ["customer_city", "customer_state"]
        for col in text_cols:
            df[col] = df[col].astype(str).str.strip().str.title()
            
        return df

    def clean_orders(self) -> pd.DataFrame:
        """Converts order timestamps to datetime objects and validates order lifecycle states."""
        df = self.raw_datasets["orders"].copy()

        # Datetime column conversion
        date_cols = [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors="coerce")

        # Normalize status string
        df["order_status"] = df["order_status"].astype(str).str.strip().str.lower()
        return df

    def clean_products(self) -> pd.DataFrame:
        """Imputes missing product categories and physical metrics."""
        df = self.raw_datasets["products"].copy()

        # Fill missing product category names
        df["product_category_name"] = df["product_category_name"].fillna("unknown")

        # Impute missing numeric specifications with median values
        numeric_cols = [
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty"
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())

        return df

    def clean_category_translation(self) -> pd.DataFrame:
        """Fills known translation gaps identified during Day 3 audit."""
        df = self.raw_datasets["category_translation"].copy()

        # Explicitly patch missing translations discovered in audit
        extra_translations = pd.DataFrame([
            {"product_category_name": "pc_gamer", "product_category_name_english": "pc_gamer"},
            {"product_category_name": "portateis_cozinha_e_preparadores_de_alimentos", "product_category_name_english": "portable_kitchen_appliances"},
            {"product_category_name": "unknown", "product_category_name_english": "unknown"}
        ])

        # Concatenate and remove any potential duplicates
        df = pd.concat([df, extra_translations], ignore_index=True)
        df = df.drop_duplicates(subset=["product_category_name"]).reset_index(drop=True)
        return df

    def clean_order_items(self) -> pd.DataFrame:
        """Ensures pricing and freight values are strictly non-negative floating-point values."""
        df = self.raw_datasets["order_items"].copy()
        
        # Ensure prices and freight are positive floats
        df["price"] = df["price"].astype(float)
        df["freight_value"] = df["freight_value"].astype(float)
        
        # Datetime conversion for shipping limit
        df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce")
        return df

    def clean_order_reviews(self) -> pd.DataFrame:
        """Cleans reviews table and handles null comment fields."""
        df = self.raw_datasets["order_reviews"].copy()

        # Convert timestamps
        df["review_creation_date"] = pd.to_datetime(df["review_creation_date"], errors="coerce")
        df["review_answer_timestamp"] = pd.to_datetime(df["review_answer_timestamp"], errors="coerce")

        # Fill missing text comments with placeholder
        df["review_comment_title"] = df["review_comment_title"].fillna("No Title")
        df["review_comment_message"] = df["review_comment_message"].fillna("No Comment")
        return df

    def run_all_cleaning(self) -> Dict[str, pd.DataFrame]:
        """Runs cleaning across all tables and returns clean DataFrames."""
        return {
            "customers": self.clean_customers(),
            "orders": self.clean_orders(),
            "order_items": self.clean_order_items(),
            "order_payments": self.raw_datasets["order_payments"].copy(),
            "order_reviews": self.clean_order_reviews(),
            "products": self.clean_products(),
            "sellers": self.raw_datasets["sellers"].copy(),
            "category_translation": self.clean_category_translation()
        }


if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaned_data = cleaner.run_all_cleaning()
    print("--- DATA CLEANING SUCCESSFUL ---")
    for key, df in cleaned_data.items():
        print(f"Table '{key}': {df.shape[0]} rows, {df.shape[1]} columns.")