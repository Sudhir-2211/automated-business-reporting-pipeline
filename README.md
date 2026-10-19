# Automated Business Reporting Pipeline

An automated data extraction, transformation, and executive reporting pipeline built with **Python**, **Pandas**, and **SQL**.

---

## Features

- **Multi-Table Relational ETL**: Analytical SQL extraction across transactional tables (`orders`, `order_items`, `products`, `customers`).
- **Financial & Operational KPIs**: Automated calculation of Net/Gross Revenue, Cost of Goods Sold (COGS), Gross Profit Margins, Average Order Value (AOV), and unit sales.
- **Dimensional Breakdowns**: Segment performance aggregations by Product Category and Geographic Region.
- **Statistical Anomaly Detection**: Outlier identification using Z-score deviations on daily revenue trajectories to catch unforeseen drops or demand spikes.
- **Multi-Format Delivery**: Generates standalone, styled HTML executive reports and structured JSON data digests.
- **Synthetic Enterprise Dataset**: Includes automated synthetic data generation with customizable time horizons and simulated financial anomalies.

---

## Project Structure

```text
automated-business-reporting/
├── data/
│   └── business_warehouse.db # SQLite relational data warehouse
├── src/
│   ├── data_generator.py     # Synthetic transaction & client seeder
│   ├── pipeline.py           # Core ETL and anomaly calculation engine
│   └── report_generator.py   # Formatted HTML & JSON report builder
├── tests/
│   ├── test_pipeline.py      # Unit tests for SQL queries and metric math
│   └── test_report_generator.py # Report rendering verification
├── main.py                   # Command-line interface entrypoint
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10+

### 2. Installation

```bash
cd automated-business-reporting
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

python -m pip install -r requirements.txt
```

### 3. Run the Pipeline

Execute the reporting pipeline via CLI:

```bash
python main.py --db-path data/business_warehouse.db --output-dir reports
```

*Note: If `data/business_warehouse.db` is missing, the script will automatically seed a synthetic enterprise dataset for demonstration.*

Outputs generated:
- `reports/business_performance_report.html` — Styled executive dashboard report.
- `reports/business_performance_report.json` — Machine-readable metrics payload.

---

## Automated Tests

Run the test suite using `pytest`:

```bash
python -m pytest tests -v
```

Tests cover:
- Analytical SQL joins and column validation
- KPI aggregations and division-by-zero protection on empty inputs
- Category and regional groupby transformations
- Z-score anomaly detector logic
- HTML template rendering and JSON payload validity

---

## Security Considerations

1. **SQL Injection**: All analytical queries are parameterized; avoid raw string formatting when extending query parameters.
2. **Access Control**: Generated executive reports contain confidential financial data and should be restricted to authenticated company personnel.
3. **Database Credentials**: When upgrading from SQLite to PostgreSQL/Snowflake, store connection strings exclusively in environment variables.

---

## Known Limitations

- **Currency Conversion**: Assumes single consolidated currency reporting (USD); does not perform dynamic multi-currency FX revaluation.
- **Tax Calculation**: Computes pre-tax net revenues; state and regional sales tax rules are outside the current pipeline scope.
