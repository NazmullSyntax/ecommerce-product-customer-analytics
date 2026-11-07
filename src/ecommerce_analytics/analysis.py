"""
Exploratory Data Analysis Engine Module
---------------------------------------
Computes business aggregations for revenue trends, category leaderboards,
geographic sales distribution, and shipping delay correlations.
"""

from pathlib import Path
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from ecommerce_analytics.config import ConfigManager


class EDAAnalyzer:
    """Calculates statistical summaries and analytical aggregations from processed data."""

    def __init__(self, config: ConfigManager = None) -> None:
        self.config = config or ConfigManager()
        self.processed_path = self.config.get_path("processed_data")
        self.master_df = self._load_master_data()

    def _load_master_data(self) -> pd.DataFrame:
        """Loads master_order_items dataset from processed storage."""
        parquet_file = self.processed_path / "master_order_items.parquet"
        csv_file = self.processed_path / "master_order_items.csv"

        if parquet_file.exists():
            return pd.read_parquet(parquet_file)
        elif csv_file.exists():
            return pd.read_csv(csv_file)
        else:
            raise FileNotFoundError("Processed master_order_items dataset not found. Run Day 4 transformation first.")

    def get_monthly_revenue_trend(self) -> pd.DataFrame:
        """Calculates monthly Gross Merchandise Value (GMV) and unique order volume for delivered orders."""
        delivered = self.master_df[self.master_df["order_status"] == "delivered"].copy()
        
        monthly = (
            delivered.groupby("purchase_year_month")
            .agg(
                total_revenue=("price", "sum"),
                total_freight=("freight_value", "sum"),
                total_orders=("order_id", "nunique"),
                unique_customers=("customer_unique_id", "nunique")
            )
            .reset_index()
        )
        
        monthly["average_order_value"] = monthly["total_revenue"] / monthly["total_orders"]
        return monthly.sort_values(by="purchase_year_month")

    def get_top_categories_by_revenue(self, top_n: int = 10) -> pd.DataFrame:
        """Returns top N revenue-generating product categories for delivered orders."""
        delivered = self.master_df[self.master_df["order_status"] == "delivered"]
        
        category_summary = (
            delivered.groupby("product_category_name_english")
            .agg(
                total_revenue=("price", "sum"),
                items_sold=("order_item_id", "count"),
                avg_item_price=("price", "mean")
            )
            .reset_index()
            .sort_values(by="total_revenue", ascending=False)
            .head(top_n)
        )
        return category_summary

    def get_sales_by_state(self, top_n: int = 10) -> pd.DataFrame:
        """Aggregates revenue, order volume, and average freight cost by customer state."""
        delivered = self.master_df[self.master_df["order_status"] == "delivered"]
        
        state_summary = (
            delivered.groupby("customer_state")
            .agg(
                total_revenue=("price", "sum"),
                total_orders=("order_id", "nunique"),
                avg_freight_value=("freight_value", "mean")
            )
            .reset_index()
            .sort_values(by="total_revenue", ascending=False)
            .head(top_n)
        )
        return state_summary

    def get_delivery_vs_review_score(self) -> pd.DataFrame:
        """Evaluates relationship between delivery delay categories and customer review scores."""
        # Load reviews table
        reviews_file = self.processed_path / "fact_order_reviews.parquet"
        reviews_df = pd.read_parquet(reviews_file) if reviews_file.exists() else pd.read_csv(self.processed_path / "fact_order_reviews.csv")

        # Load orders table
        orders_file = self.processed_path / "fact_orders.parquet"
        orders_df = pd.read_parquet(orders_file) if orders_file.exists() else pd.read_csv(self.processed_path / "fact_orders.csv")

        merged = orders_df.merge(reviews_df, on="order_id", how="inner")
        delivered = merged[merged["order_status"] == "delivered"].copy()

        # Categorize delivery timeliness
        def classify_delivery(row):
            if row["delivery_delay_days"] > 0:
                return "Late Delivery (>0 days late)"
            elif row["delivery_delay_days"] >= -3:
                return "On-Time (0-3 days early)"
            else:
                return "Early Delivery (>3 days early)"

        delivered["delivery_category"] = delivered.apply(classify_delivery, axis=1)

        review_summary = (
            delivered.groupby("delivery_category")
            .agg(
                average_review_score=("review_score", "mean"),
                total_reviews=("review_id", "count"),
                one_star_percentage=("review_score", lambda x: round((x == 1).mean() * 100, 2)),
                five_star_percentage=("review_score", lambda x: round((x == 5).mean() * 100, 2))
            )
            .reset_index()
        )
        return review_summary


if __name__ == "__main__":
    analyzer = EDAAnalyzer()
    print("--- MONTHLY REVENUE SAMPLE ---")
    print(analyzer.get_monthly_revenue_trend().head(3).to_string(index=False))

    print("\n--- TOP 5 CATEGORIES BY REVENUE ---")
    print(analyzer.get_top_categories_by_revenue(5).to_string(index=False))