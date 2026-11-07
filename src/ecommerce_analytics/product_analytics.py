"""
Product & Operational Logistics Analytics Module
------------------------------------------------
Computes Pareto 80/20 product category distributions, freight friction ratios,
carrier delivery performance matrices, and product review correlations.
"""

from pathlib import Path
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from ecommerce_analytics.config import ConfigManager
from ecommerce_analytics.db_engine import DatabaseEngine


class ProductAnalytics:
    """Executes product category diagnostics and operational logistics analysis."""

    def __init__(self, db_engine: DatabaseEngine = None) -> None:
        self.db = db_engine or DatabaseEngine()

    def get_pareto_category_analysis(self) -> pd.DataFrame:
        """Executes Pareto (80/20) cumulative revenue share analysis across product categories."""
        query = """
            SELECT 
                p.product_category_name_english AS category_name,
                COUNT(oi.order_item_id) AS total_items_sold,
                COUNT(DISTINCT oi.order_id) AS total_orders,
                SUM(oi.price) AS category_revenue,
                AVG(oi.price) AS avg_item_price
            FROM fact_order_items oi
            JOIN dim_products p ON oi.product_id = p.product_id
            JOIN fact_orders o ON oi.order_id = o.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY p.product_category_name_english
            ORDER BY category_revenue DESC;
        """
        df = self.db.execute_query(query)

        # Calculate Cumulative Revenue and Share %
        total_platform_revenue = df["category_revenue"].sum()
        df["cumulative_revenue"] = df["category_revenue"].cumsum()
        df["revenue_share_pct"] = (df["category_revenue"] / total_platform_revenue) * 100
        df["cumulative_share_pct"] = (df["cumulative_revenue"] / total_platform_revenue) * 100

        # Assign Pareto Classification
        df["pareto_class"] = np.where(
            df["cumulative_share_pct"] <= 80.0,
            "Core Category (Top 80% Revenue)",
            "Tail Category (Bottom 20% Revenue)"
        )
        return df

    def get_freight_friction_analysis(self) -> pd.DataFrame:
        """Evaluates relationship between item weight, shipping cost, and price per category."""
        query = """
            SELECT 
                p.product_category_name_english AS category_name,
                COUNT(oi.order_item_id) AS items_sold,
                AVG(oi.price) AS avg_price_brl,
                AVG(oi.freight_value) AS avg_freight_brl,
                AVG(p.product_weight_g) AS avg_weight_g
            FROM fact_order_items oi
            JOIN dim_products p ON oi.product_id = p.product_id
            JOIN fact_orders o ON oi.order_id = o.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY p.product_category_name_english
            HAVING COUNT(oi.order_item_id) >= 200
            ORDER BY avg_freight_brl DESC;
        """
        df = self.db.execute_query(query)
        df["freight_to_price_ratio_pct"] = (df["avg_freight_brl"] / df["avg_price_brl"]) * 100
        df["freight_to_price_ratio_pct"] = df["freight_to_price_ratio_pct"].round(2)
        return df

    def get_logistics_performance_matrix(self) -> pd.DataFrame:
        """Aggregates delivery duration, delay rates, and freight costs by destination state."""
        query = """
            SELECT 
                c.customer_state,
                COUNT(DISTINCT o.order_id) AS total_delivered_orders,
                AVG(o.actual_delivery_days) AS avg_actual_delivery_days,
                AVG(o.estimated_delivery_days) AS avg_estimated_delivery_days,
                AVG(o.delivery_delay_days) AS avg_delay_days,
                SUM(o.is_late_delivery) AS total_late_orders,
                AVG(oi.freight_value) AS avg_freight_cost
            FROM fact_orders o
            JOIN dim_customers c ON o.customer_id = c.customer_id
            JOIN fact_order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_state
            ORDER BY total_delivered_orders DESC;
        """
        df = self.db.execute_query(query)
        df["late_delivery_rate_pct"] = (df["total_late_orders"] / df["total_delivered_orders"]) * 100
        df["late_delivery_rate_pct"] = df["late_delivery_rate_pct"].round(2)
        return df

    def get_review_score_correlations(self) -> pd.DataFrame:
        """Analyzes average review scores grouped by delivery delay buckets."""
        query = """
            SELECT 
                o.order_id,
                o.delivery_delay_days,
                o.is_late_delivery,
                r.review_score
            FROM fact_orders o
            JOIN fact_order_reviews r ON o.order_id = r.order_id
            WHERE o.order_status = 'delivered';
        """
        df = self.db.execute_query(query)

        # Categorize Delivery Speed Window
        def categorize_delay(days):
            if days > 5:
                return "Severe Delay (>5 Days Late)"
            elif days > 0:
                return "Minor Delay (1-5 Days Late)"
            elif days >= -3:
                return "On-Time (0-3 Days Early)"
            else:
                return "Super Early (>3 Days Early)"

        df["delay_bucket"] = df["delivery_delay_days"].apply(categorize_delay)

        summary = (
            df.groupby("delay_bucket")
            .agg(
                order_count=("order_id", "count"),
                avg_review_score=("review_score", "mean"),
                pct_one_star=("review_score", lambda x: (x == 1).mean() * 100),
                pct_five_star=("review_score", lambda x: (x == 5).mean() * 100)
            )
            .reset_index()
        )
        return summary.sort_values(by="avg_review_score", ascending=False)


if __name__ == "__main__":
    product_engine = ProductAnalytics()
    
    print("--- PARETO 80/20 CATEGORY DISTRIBUTION ---")
    pareto_df = product_engine.get_pareto_category_analysis()
    core_count = len(pareto_df[pareto_df["pareto_class"].str.contains("Core")])
    tail_count = len(pareto_df[pareto_df["pareto_class"].str.contains("Tail")])
    print(f"Core Categories (Drive 80% Revenue): {core_count}")
    print(f"Tail Categories (Drive 20% Revenue): {tail_count}")

    print("\n--- TOP FREIGHT FRICTION CATEGORIES ---")
    friction_df = product_engine.get_freight_friction_analysis()
    print(friction_df[["category_name", "avg_price_brl", "avg_freight_brl", "freight_to_price_ratio_pct"]].head(5).to_string(index=False))