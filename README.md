# Ecommerce Product & Customer Analytics

A starter workspace for understanding ecommerce data, assessing data quality,
cleaning raw extracts, and analyzing sales, customers, and products.

## Project layout

- `data/raw/` — original CSV inputs (ignored by Git)
- `data/interim/` — validated/cleaned intermediate CSVs (ignored by Git)
- `data/processed/` — analysis-ready outputs (ignored by Git)
- `notebooks/` — guided exploration and analysis workflow
- `src/ecommerce_analytics/` — reusable Python functions
- `sql/` — starter schema, quality checks, and analysis queries
- `dashboard/` — location for a Power BI report and exported screenshots
- `reports/` — business findings and final report templates

## Setup

Use Python 3.10 or newer:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

In VS Code, select the `.venv` interpreter and open this project folder.

## Add data

Place CSV files in `data/raw/`. The default expected filenames are
`customers.csv`, `products.csv`, `orders.csv`, and `order_items.csv`; edit
`config/config.yaml` if your files have other names. Tables are optional at load
time, but each notebook or metric needs the relevant tables and columns:

- `orders`: `order_id`, `customer_id`, `order_date`, `revenue` (sales analysis)
- `customers`: `customer_id` (customer analysis)
- `products`: `product_id` (product analysis)
- `order_items`: `product_id`, `price`, `quantity` (product analysis)

Adapt column names and metric definitions to your source system before drawing
business conclusions. The SQL examples assume a relational schema in
`sql/database_schema.sql`; date truncation syntax may need adjustment for your
database engine.

Raw input files are never modified. The cleaning notebook saves clean table
copies in `data/interim/`.

## Run

Open notebooks in order in VS Code or Jupyter. Run automated tests from the
project root:

```powershell
python -m pytest
```

Build the Power BI report in Power BI Desktop and save it as
`dashboard/ecommerce_dashboard.pbix`. Export the four report screenshots to
`dashboard/screenshots/`. These are output assets, so they are excluded from
version control by default.
