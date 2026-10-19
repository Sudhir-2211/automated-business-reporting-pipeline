import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
import pandas as pd


class ReportGenerator:
    @staticmethod
    def generate_html_report(
        kpis: Dict[str, Any],
        category_df: pd.DataFrame,
        regional_df: pd.DataFrame,
        anomalies: List[Dict[str, Any]],
        output_filepath: str,
    ) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)

        categories_html = ""
        for _, row in category_df.iterrows():
            categories_html += f"""
            <tr>
                <td style="font-weight: 600;">{row['category']}</td>
                <td>${row['net_revenue']:,.2f}</td>
                <td>${row['profit']:,.2f}</td>
                <td><span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #10b981;">{row['margin_pct']}%</span></td>
                <td>{int(row['units_sold']):,}</td>
            </tr>
            """

        regional_html = ""
        for _, row in regional_df.iterrows():
            regional_html += f"""
            <tr>
                <td style="font-weight: 600;">{row['region']}</td>
                <td>${row['net_revenue']:,.2f}</td>
                <td>${row['profit']:,.2f}</td>
                <td>{int(row['order_count']):,}</td>
            </tr>
            """

        anomalies_html = ""
        if anomalies:
            for a in anomalies:
                color = "#ef4444" if a["type"] == "REVENUE_DIP" else "#3b82f6"
                anomalies_html += f"""
                <li style="margin-bottom: 0.5rem;">
                    <strong>{a['date']}</strong>: <span style="color: {color}; font-weight: 600;">{a['type']}</span>
                    (Revenue: ${a['revenue']:,.2f}, Z-score: {a['z_score']})
                </li>
                """
        else:
            anomalies_html = "<li>No statistical anomalies detected in current reporting window.</li>"

        report_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Executive Business Performance Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background-color: #f8fafc;
            color: #0f172a;
            margin: 0;
            padding: 2rem;
        }}
        .report-card {{
            max-width: 1000px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            padding: 2.5rem;
        }}
        .report-header {{
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .report-header h1 {{
            font-size: 1.85rem;
            margin: 0;
            color: #1e293b;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2.5rem;
        }}
        .kpi-box {{
            background: #f1f5f9;
            padding: 1.25rem;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }}
        .kpi-label {{
            font-size: 0.75rem;
            text-transform: uppercase;
            font-weight: 700;
            color: #64748b;
        }}
        .kpi-value {{
            font-size: 1.6rem;
            font-weight: 700;
            color: #0f172a;
            margin-top: 0.35rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 2rem;
        }}
        th, td {{
            text-align: left;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #e2e8f0;
            font-size: 0.9rem;
        }}
        th {{
            background-color: #f8fafc;
            color: #475569;
            font-weight: 600;
        }}
        .badge {{
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .anomaly-card {{
            background: #fffbeb;
            border: 1px solid #fde68a;
            padding: 1.25rem;
            border-radius: 8px;
            margin-top: 2rem;
        }}
    </style>
</head>
<body>
    <div class="report-card">
        <div class="report-header">
            <div>
                <h1>Executive Business Performance Report</h1>
                <p style="color: #64748b; font-size: 0.85rem; margin-top: 0.35rem;">Generated on: {report_timestamp}</p>
            </div>
            <div style="font-weight: 700; color: #3b82f6; font-size: 1.1rem;">Q3/Q4 Analytics</div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-box">
                <div class="kpi-label">Total Net Revenue</div>
                <div class="kpi-value">${kpis['total_net_revenue']:,.2f}</div>
            </div>
            <div class="kpi-box" style="border-left-color: #10b981;">
                <div class="kpi-label">Gross Profit</div>
                <div class="kpi-value">${kpis['total_profit']:,.2f}</div>
            </div>
            <div class="kpi-box" style="border-left-color: #8b5cf6;">
                <div class="kpi-label">Profit Margin</div>
                <div class="kpi-value">{kpis['gross_margin_pct']}%</div>
            </div>
            <div class="kpi-box" style="border-left-color: #f59e0b;">
                <div class="kpi-label">Avg Order Value (AOV)</div>
                <div class="kpi-value">${kpis['average_order_value']:,.2f}</div>
            </div>
        </div>

        <h2>Category Financial Performance</h2>
        <table>
            <thead>
                <tr>
                    <th>Product Category</th>
                    <th>Net Revenue</th>
                    <th>Gross Profit</th>
                    <th>Margin</th>
                    <th>Units Sold</th>
                </tr>
            </thead>
            <tbody>
                {categories_html}
            </tbody>
        </table>

        <h2>Regional Distribution</h2>
        <table>
            <thead>
                <tr>
                    <th>Region</th>
                    <th>Net Revenue</th>
                    <th>Gross Profit</th>
                    <th>Completed Orders</th>
                </tr>
            </thead>
            <tbody>
                {regional_html}
            </tbody>
        </table>

        <div class="anomaly-card">
            <h3 style="margin-top: 0; color: #92400e;">Automated Statistical Anomaly Watch</h3>
            <ul style="padding-left: 1.25rem; color: #78350f; font-size: 0.9rem;">
                {anomalies_html}
            </ul>
        </div>
    </div>
</body>
</html>
"""
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Also write JSON metrics export alongside HTML
        json_path = output_filepath.replace(".html", ".json")
        export_payload = {
            "generated_at": report_timestamp,
            "kpis": kpis,
            "anomalies": anomalies,
            "categories": category_df.to_dict(orient="records"),
            "regions": regional_df.to_dict(orient="records"),
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(export_payload, f, indent=2)

        return output_filepath
