# CartScope

## E-Commerce Intelligence & Analytics Platform

CartScope is a maintainable Python and Streamlit analytics application for exploring
the supplied India fashion e-commerce sales dataset. It provides consistent,
auditable KPIs and interactive views for sales, products, regions, fulfilment, and
data quality. CartScope is an independent analytics project and is not an official
Amazon product.

## Problem statement

E-commerce teams need one reliable view of revenue, orders, product demand,
geographic performance, cancellations, returns, and data quality. The original
analysis mixed record and order metrics and used non-portable notebook paths.
CartScope centralizes cleaning and calculations so the dashboard and notebook use the
same definitions.

## Features

- Executive, sales, regional, product, fulfilment, and data-explorer views.
- Date, month, category, state, status, fulfilment, and B2B/B2C filters.
- Plotly charts, responsive KPI cards, and filtered CSV export.
- CSV/XLSX upload with required-column and date validation.
- Reusable loading, cleaning, calculation, and analytics modules.
- Automated tests for cleaning, metrics, and filters.
- A portable EDA notebook with revenue sensitivity analysis.

## Technology stack

Python, Pandas, NumPy, Streamlit, Plotly, OpenPyXL, Jupyter, and Pytest.

## Architecture

`app.py` owns the UI and delegates data behavior to `utils/`. The source workbook is
kept in the repository root and copied to `data/sales_dataset.xlsx` as the application
default. The original README and PBIX are preserved as reference files.

```text
.
├── app.py
├── data/sales_dataset.xlsx
├── notebooks/CartScope_EDA.ipynb
├── utils/
│   ├── analytics.py
│   ├── calculations.py
│   ├── data_cleaning.py
│   ├── data_loader.py
│   └── validators.py
├── tests/test_cartscope.py
├── assets/dashboard_overview.png
└── powerbi/Amazon_dashboard_original.pbix
```

## Dataset

The supplied workbook contains 128,949 source records, 23 columns, and dates from
March 31 through June 29, 2022. It includes order IDs, dates, status, fulfilment,
category, SKU, size, quantity, amount, destination fields, and B2B information.
The original workbook is retained as `sales_dataset.xlsx`; the application copy is
`data/sales_dataset.xlsx`.

## Processing and analytical methodology

1. Validate required columns and parse dates.
2. Remove exact duplicate records. The supplied data becomes **128,943 records**.
3. Standardize category labels and state casing without inventing geography.
4. Impute missing Amount values using the median of non-cancelled, positive Amount
   values and add `Amount_Imputed`. Zero-amount non-cancelled rows remain zero.
5. Exclude cancelled records from revenue and units sold; report cancelled value
   separately.
6. Calculate AOV as revenue divided by unique non-cancelled orders.
7. Report both record-based and order-based cancellation rates.
8. Treat both `Shipped - Returned to Seller` and `Shipped - Returning to Seller` as
   returns. The return denominator is non-cancelled records.

For the supplied data, the verified baseline is 120,352 unique orders, ₹71,790,793.62
revenue, 110,970 units sold, and ₹695.93 AOV. These are baseline values before
interactive filters. March is a partial month and should not be compared to complete
months without qualification.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run the application

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit. Use the Data Explorer page to upload a CSV
or XLSX file with the required columns: `Order ID`, `Date`, `Status`, `Category`,
`Qty`, and `Amount`.

## Notebook and tests

Run the notebook with Jupyter from the project root:

```bash
jupyter notebook notebooks/CartScope_EDA.ipynb
pytest -q
```

## Screenshot

The supplied dashboard image is retained at
[`assets/dashboard_overview.png`](assets/dashboard_overview.png) as a historical
reference. It is not treated as evidence for the corrected CartScope metrics.
Browser verification captures of the current application are also retained:
[`gui_executive_overview.png`](assets/gui_executive_overview.png),
[`gui_sales_analytics.png`](assets/gui_sales_analytics.png),
[`gui_regional_analytics.png`](assets/gui_regional_analytics.png),
[`gui_product_analytics.png`](assets/gui_product_analytics.png),
[`gui_order_fulfilment.png`](assets/gui_order_fulfilment.png), and
[`gui_data_explorer.png`](assets/gui_data_explorer.png).

## Power BI integration

The original `Amazon_dashboard.pbix` is preserved, including its invalid 2-byte
placeholder state, and is not used by CartScope. A future manual recreation should
use the cleaned fields and definitions in this README: record and unique-order
counts must be separated, cancelled value must not enter revenue, AOV must use
unique non-cancelled orders, and return statuses must be explicitly grouped.

## Limitations and future scope

The source covers a limited date window, has incomplete shipping fields, and does
not support unsupported delivery-performance claims. Future work could add a
warehouse-backed data layer, configurable metric definitions, geographic mapping
only where validated, and a refreshed Power BI model.

## Author and contribution

This repository contains the CartScope implementation and its source dataset.
Contributions should preserve the shared cleaning and metric definitions, add tests
for behavior changes, and document any new assumptions.
