# E-Commerce Product & Customer Behavior Analytics

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon%20Cloud-blue)](https://neon.tech/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end Business Intelligence, SQL Data Engineering, and Customer Analytics solution analyzing over 100,000 commercial transactions from Brazilian E-Commerce platform **Olist**.

---

## Executive Summary

This project addresses key commercial, merchandising, and operational challenges faced by e-commerce marketplace executives:
* **Gross Merchandise Value (GMV):** R$ 13.22M generated across 96,478 delivered orders.
* **Customer Retention Challenge:** Only 3.00% repeat purchase rate, highlighting an acquisition-heavy business model.
* **Logistics Impact on Sentiment:** Delivery delays cause average review ratings to drop from **4.25 ⭐** (on-time) to **2.25 ⭐** (late), with 1-star negative ratings surging to 53.8%.
* **Pareto Revenue Drivers:** 18 out of 71 product categories account for 80% of total revenue.

---

## Interactive Dashboard Preview

| Executive Overview | Customer Behavior Analytics |
|---|---|
| *(Include Screenshot 01)* | *(Include Screenshot 03)* |

* **Live Web Dashboard:** [Streamlit Web App Link / Looker Studio Link](https://your-dashboard-link.app)

---

## Tech Stack & Tools

* **Data Analysis & ETL:** Python (`pandas`, `numpy`), VS Code, Jupyter Notebooks.
* **Data Visualization:** Matplotlib, Seaborn, Plotly Express.
* **Database & SQL Querying:** Neon Cloud PostgreSQL / SQLite, SQLAlchemy, ANSI SQL (CTEs, Window Functions, `NTILE`, `LAG`).
* **BI Dashboarding:** Streamlit Community Cloud / Power BI / Google Looker Studio.
* **Version Control:** Git, GitHub.

---

## Enterprise Repository Architecture

```text
ecommerce-product-customer-analytics/
├── config/                  # Path & business rules configuration
│   └── config.yaml
├── data/
│   ├── raw/                 # Original untouched Olist CSV files
│   ├── interim/             # Quality-audited intermediate files
│   └── processed/           # Cleaned, transformed CSV & Parquet files
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_quality_assessment.ipynb
│   ├── 03_data_cleaning.ipynb
│   ├── 04_exploratory_data_analysis.ipynb
│   ├── 05_customer_analytics.ipynb
│   └── 06_product_analytics.ipynb
├── src/
│   └── ecommerce_analytics/ # Modular Python Package
│       ├── config.py
│       ├── data_loader.py
│       ├── validation.py
│       ├── cleaning.py
│       ├── transformation.py
│       ├── quality_assessment.py
│       ├── analysis.py
│       ├── visualization.py
│       ├── db_engine.py
│       ├── customer_analytics.py
│       └── product_analytics.py
├── sql/                     # 25 Business SQL Queries
│   ├── database_schema.sql
│   ├── sales_analysis.sql
│   ├── product_analysis.sql
│   ├── customer_analysis.sql
│   └── advanced_queries.sql
├── dashboard/
│   └── app.py               # Interactive Streamlit Web Application
├── reports/                 # Strategic Insights & Business Reports
│   ├── figures/
│   ├── business_insights.md
│   └── final_report.md
├── requirements.txt
├── setup.py                 # Local editable package setup
├── .env.example
├── .gitignore
└── README.md