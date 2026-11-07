"""
Neon PostgreSQL & Database Engine Module
-----------------------------------------
Connects to online Neon PostgreSQL cluster (or local fallback)
and automates table creation, dataset ingestion, and SQL query execution.
"""

import os
from pathlib import Path
from typing import Dict, Optional
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from ecommerce_analytics.config import ConfigManager

# Load environment variables from .env file
load_dotenv()


class DatabaseEngine:
    """Manages cloud PostgreSQL / local DB connections and automated CSV ingestion."""

    def __init__(self, config: ConfigManager = None) -> None:
        self.config = config or ConfigManager()
        self.processed_path = self.config.get_path("processed_data")
        self.db_url = os.getenv("DATABASE_URL")
        self.engine: Engine = self._create_db_engine()

    def _create_db_engine(self) -> Engine:
        """Instantiates SQLAlchemy connection engine for Neon PostgreSQL or SQLite fallback."""
        if self.db_url:
            # Fix legacy postgres:// protocol string if present
            url = self.db_url.replace("postgres://", "postgresql://")
            print("Connecting to Online Neon PostgreSQL Database...")
            return create_engine(url, pool_pre_ping=True)
        else:
            sqlite_path = self.processed_path / "ecommerce_analytics.db"
            print(f"DATABASE_URL not found in .env. Falling back to local SQLite: {sqlite_path}")
            return create_engine(f"sqlite:///{sqlite_path}")

    def load_processed_tables(self) -> None:
        """Ingests all processed CSV datasets directly into online database tables."""
        tables_to_load = {
            "dim_customers": "dim_customers.csv",
            "dim_products": "dim_products.csv",
            "dim_sellers": "dim_sellers.csv",
            "fact_orders": "fact_orders.csv",
            "fact_order_items": "fact_order_items.csv",
            "fact_order_payments": "fact_order_payments.csv",
            "fact_order_reviews": "fact_order_reviews.csv"
        }

        print("--- STARTING NEON DATABASE INGESTION ---")
        with self.engine.begin() as conn:
            for table_name, csv_name in tables_to_load.items():
                csv_path = self.processed_path / csv_name
                if not csv_path.exists():
                    raise FileNotFoundError(f"Missing processed CSV file: {csv_path}")

                df = pd.read_csv(csv_path)
                
                # Push dataframe to Neon PostgreSQL
                df.to_sql(
                    name=table_name,
                    con=conn,
                    if_exists="replace",
                    index=False,
                    chunksize=5000  # Optimized chunk size for network upload
                )
                print(f"Uploaded '{table_name}': {len(df):,} rows -> Neon Cloud DB.")

        print("All tables loaded successfully into Neon PostgreSQL!")

    def execute_query(self, query_string: str) -> pd.DataFrame:
        """Executes any raw SQL query and returns results as a Pandas DataFrame."""
        try:
            with self.engine.connect() as conn:
                return pd.read_sql_query(sql=text(query_string), con=conn)
        except Exception as e:
            raise RuntimeError(f"Database Query Error: {str(e)}")


if __name__ == "__main__":
    db = DatabaseEngine()
    db.load_processed_tables()

    # Verification Query on Neon PostgreSQL
    res = db.execute_query("SELECT COUNT(*) AS total_orders FROM fact_orders;")
    print(f"\nVerification Check: Total Orders in Neon DB = {res['total_orders'].iloc[0]:,}")