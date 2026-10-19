import sqlite3
from typing import Dict, Any, List
import pandas as pd
import numpy as np


class BusinessReportingPipeline:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def extract_order_dataset(self) -> pd.DataFrame:
        """Executes analytical SQL join across orders, items, products, and customers."""
        conn = sqlite3.connect(self.db_path)
        query = """
        SELECT 
            o.order_id,
            o.order_date,
            o.status,
            c.customer_id,
            c.name AS customer_name,
            c.region,
            c.segment,
            p.product_id,
            p.name AS product_name,
            p.category,
            p.unit_price,
            p.unit_cost,
            oi.quantity,
            oi.discount,
            (oi.quantity * p.unit_price) AS gross_revenue,
            (oi.quantity * p.unit_price * (1.0 - oi.discount)) AS net_revenue,
            (oi.quantity * p.unit_cost) AS total_cost
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.status != 'REFUNDED';
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            df["order_date"] = pd.to_datetime(df["order_date"])
            df["profit"] = df["net_revenue"] - df["total_cost"]
        return df

    def compute_summary_kpis(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {
                "total_orders": 0,
                "total_gross_revenue": 0.0,
                "total_net_revenue": 0.0,
                "total_profit": 0.0,
                "gross_margin_pct": 0.0,
                "average_order_value": 0.0,
                "total_units_sold": 0,
            }

        unique_orders = df["order_id"].nunique()
        gross_rev = df["gross_revenue"].sum()
        net_rev = df["net_revenue"].sum()
        total_cost = df["total_cost"].sum()
        profit = net_rev - total_cost
        margin_pct = (profit / net_rev * 100) if net_rev > 0 else 0.0
        aov = (net_rev / unique_orders) if unique_orders > 0 else 0.0

        return {
            "total_orders": int(unique_orders),
            "total_gross_revenue": round(float(gross_rev), 2),
            "total_net_revenue": round(float(net_rev), 2),
            "total_profit": round(float(profit), 2),
            "gross_margin_pct": round(float(margin_pct), 2),
            "average_order_value": round(float(aov), 2),
            "total_units_sold": int(df["quantity"].sum()),
        }

    def compute_category_breakdown(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["category", "net_revenue", "profit", "margin_pct", "units_sold"])

        grouped = df.groupby("category").agg({
            "net_revenue": "sum",
            "profit": "sum",
            "quantity": "sum",
        }).reset_index().rename(columns={"quantity": "units_sold"})

        grouped["margin_pct"] = (grouped["profit"] / grouped["net_revenue"] * 100).round(2)
        grouped["net_revenue"] = grouped["net_revenue"].round(2)
        grouped["profit"] = grouped["profit"].round(2)
        return grouped.sort_values(by="net_revenue", ascending=False)

    def compute_regional_breakdown(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["region", "net_revenue", "order_count", "profit"])

        grouped = df.groupby("region").agg({
            "net_revenue": "sum",
            "profit": "sum",
            "order_id": "nunique",
        }).reset_index().rename(columns={"order_id": "order_count"})

        grouped["net_revenue"] = grouped["net_revenue"].round(2)
        grouped["profit"] = grouped["profit"].round(2)
        return grouped.sort_values(by="net_revenue", ascending=False)

    def detect_daily_anomalies(self, df: pd.DataFrame, z_threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Identifies days with statistically anomalous revenue based on Z-score."""
        if df.empty:
            return []

        daily = df.groupby(df["order_date"].dt.date)["net_revenue"].sum().reset_index()
        if len(daily) < 5:
            return []

        mean_rev = daily["net_revenue"].mean()
        std_rev = daily["net_revenue"].std()

        if std_rev == 0 or np.isnan(std_rev):
            return []

        daily["z_score"] = (daily["net_revenue"] - mean_rev) / std_rev

        anomalies = []
        for _, row in daily[daily["z_score"].abs() >= z_threshold].iterrows():
            anomalies.append({
                "date": str(row["order_date"]),
                "revenue": round(float(row["net_revenue"]), 2),
                "z_score": round(float(row["z_score"]), 2),
                "type": "REVENUE_SPIKE" if row["z_score"] > 0 else "REVENUE_DIP",
            })
        return anomalies
