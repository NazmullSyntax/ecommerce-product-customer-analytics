"""
Customer Analytics & RFM Segmentation Engine Module
---------------------------------------------------
Calculates Recency, Frequency, Monetary (RFM) scores, segments customer cohorts,
and evaluates repeat purchase & retention dynamics.
"""

from pathlib import Path
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from ecommerce_analytics.config import ConfigManager
from ecommerce_analytics.db_engine import DatabaseEngine


class CustomerAnalytics:
    """Performs RFM scoring, customer segmentation, and cohort analysis."""

    def __init__(self, db_engine: DatabaseEngine = None) -> None:
        self.db = db_engine or DatabaseEngine()

    def get_rfm_scores(self) -> pd.DataFrame:
        """Calculates raw RFM values and assigns 1-5 quartile quantile scores per customer."""
        # Query customer order metrics directly from Neon DB / Local DB
        query = """
            SELECT 
                c.customer_unique_id,
                MAX(o.order_purchase_timestamp) AS last_purchase_date,
                COUNT(DISTINCT o.order_id) AS frequency,
                SUM(oi.price) AS monetary
            FROM fact_orders o
            JOIN fact_order_items oi ON o.order_id = oi.order_id
            JOIN dim_customers c ON o.customer_id = c.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id;
        """
        df = self.db.execute_query(query)
        df["last_purchase_date"] = pd.to_datetime(df["last_purchase_date"])

        # Define Snapshot Date as 1 day after the latest purchase date in dataset
        snapshot_date = df["last_purchase_date"].max() + pd.Timedelta(days=1)
        
        # Calculate Recency in Days
        df["recency"] = (snapshot_date - df["last_purchase_date"]).dt.days

        # RFM Quantile Scoring (1 to 5 scale)
        # Recency: Lower days = Higher Score (5 is best)
        df["r_score"] = pd.qcut(df["recency"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)

        # Frequency: Rank method used due to heavy concentration of single-time buyers
        df["f_score"] = pd.Series(
            np.where(df["frequency"] > 1, 5, 1), index=df.index
        ).astype(int)

        # Monetary: Higher spend = Higher Score (5 is best)
        df["m_score"] = pd.qcut(df["monetary"], q=5, labels=[1, 2, 3, 4, 5]).astype(int)

        # Combined RFM Score & String
        df["rfm_cell"] = df["r_score"].astype(str) + df["f_score"].astype(str) + df["m_score"].astype(str)
        df["rfm_score"] = df["r_score"] + df["f_score"] + df["m_score"]

        # Assign Business Customer Segments
        df["customer_segment"] = df.apply(self._assign_segment, axis=1)
        return df

    @staticmethod
    def _assign_segment(row: pd.Series) -> str:
        """Rule-based segmentation logic mapping RFM metrics to business categories."""
        r, f, m = row["r_score"], row["f_score"], row["m_score"]

        if r >= 4 and f == 5 and m >= 4:
            return "Champions (VIP)"
        elif r >= 3 and f == 5:
            return "Loyal Customers"
        elif r >= 4 and f == 1 and m >= 3:
            return "Promising / Recent Buyers"
        elif r >= 3 and f == 1 and m < 3:
            return "New / Casual Buyers"
        elif r == 2 and f == 5:
            return "At Risk (Need Attention)"
        elif r == 1 and f == 5:
            return "Cant Lose Them (High Spend Churned)"
        elif r <= 2 and f == 1 and m >= 4:
            return "Hibernating High Value"
        else:
            return "Lost / Inactive"

    def get_segment_summary(self, rfm_df: pd.DataFrame) -> pd.DataFrame:
        """Aggregates customer counts, average spend, and average recency by segment."""
        summary = (
            rfm_df.groupby("customer_segment")
            .agg(
                customer_count=("customer_unique_id", "count"),
                avg_recency_days=("recency", "mean"),
                avg_frequency=("frequency", "mean"),
                avg_monetary_spend=("monetary", "mean"),
                total_segment_revenue=("monetary", "sum")
            )
            .reset_index()
        )
        
        total_cust = summary["customer_count"].sum()
        summary["customer_percentage"] = round((summary["customer_count"] / total_cust) * 100, 2)
        return summary.sort_values(by="total_segment_revenue", ascending=False)

    def calculate_cohort_retention(self) -> pd.DataFrame:
        """Builds monthly cohort retention matrix tracking user activity over time."""
        query = """
            SELECT 
                c.customer_unique_id,
                o.order_id,
                o.order_purchase_timestamp
            FROM fact_orders o
            JOIN dim_customers c ON o.customer_id = c.customer_id
            WHERE o.order_status = 'delivered';
        """
        df = self.db.execute_query(query)
        df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])

        # Determine Cohort Month (First purchase month per customer)
        df["order_month"] = df["order_purchase_timestamp"].dt.to_period("M")
        df["cohort_month"] = df.groupby("customer_unique_id")["order_purchase_timestamp"].transform("min").dt.to_period("M")

        # Cohort Index (Months elapsed since first order)
        df["cohort_index"] = (df["order_month"].dt.year - df["cohort_month"].dt.year) * 12 + (df["order_month"].dt.month - df["cohort_month"].dt.month)

        # Pivot Cohort Retention Matrix
        cohort_data = (
            df.groupby(["cohort_month", "cohort_index"])["customer_unique_id"]
            .nunique()
            .reset_index()
        )
        
        cohort_pivot = cohort_data.pivot(index="cohort_month", columns="cohort_index", values="customer_unique_id")
        
        # Calculate Percentage Retention Matrix
        cohort_size = cohort_pivot.iloc[:, 0]
        retention_matrix = cohort_pivot.divide(cohort_size, axis=0) * 100
        return retention_matrix.round(2)


if __name__ == "__main__":
    analytics = CustomerAnalytics()
    print("--- RUNNING RFM CUSTOMER SEGMENTATION ---")
    rfm_df = analytics.get_rfm_scores()
    print(f"Total Customers Scored: {len(rfm_df):,}")

    summary_df = analytics.get_segment_summary(rfm_df)
    print("\n--- SEGMENT SUMMARY REPORT ---")
    print(summary_df.to_string(index=False))