import os
import json
import pandas as pd
from src.report_generator import ReportGenerator


def test_generate_html_and_json_report(tmp_path):
    output_html = str(tmp_path / "test_report.html")
    kpis = {
        "total_orders": 120,
        "total_gross_revenue": 50000.0,
        "total_net_revenue": 48000.0,
        "total_profit": 22000.0,
        "gross_margin_pct": 45.83,
        "average_order_value": 400.0,
        "total_units_sold": 450,
    }
    cat_df = pd.DataFrame([
        {"category": "Cloud Services", "net_revenue": 30000.0, "profit": 15000.0, "margin_pct": 50.0, "units_sold": 200},
    ])
    reg_df = pd.DataFrame([
        {"region": "North America", "net_revenue": 28000.0, "profit": 13000.0, "order_count": 70},
    ])
    anomalies = [
        {"date": "2026-09-15", "revenue": 1200.0, "z_score": -2.3, "type": "REVENUE_DIP"}
    ]

    result_path = ReportGenerator.generate_html_report(kpis, cat_df, reg_df, anomalies, output_html)
    assert os.path.exists(result_path)

    with open(result_path, "r", encoding="utf-8") as f:
        html = f.read()
        assert "Executive Business Performance Report" in html
        assert "$48,000.00" in html
        assert "REVENUE_DIP" in html

    json_path = output_html.replace(".html", ".json")
    assert os.path.exists(json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["kpis"]["total_orders"] == 120
