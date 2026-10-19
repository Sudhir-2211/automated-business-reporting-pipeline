import os
import argparse
from src.data_generator import generate_synthetic_business_db
from src.pipeline import BusinessReportingPipeline
from src.report_generator import ReportGenerator


def run_pipeline(db_path: str = "data/business_warehouse.db", output_dir: str = "reports"):
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Generating synthetic business database...")
        generate_synthetic_business_db(db_path)

    print(f"Extracting analytical dataset from {db_path}...")
    pipeline = BusinessReportingPipeline(db_path)
    df = pipeline.extract_order_dataset()
    print(f"Extracted {len(df)} itemized transaction records.")

    print("Computing executive KPIs and segment breakdowns...")
    kpis = pipeline.compute_summary_kpis(df)
    category_df = pipeline.compute_category_breakdown(df)
    regional_df = pipeline.compute_regional_breakdown(df)
    anomalies = pipeline.detect_daily_anomalies(df)

    output_html = os.path.join(output_dir, "business_performance_report.html")
    print(f"Generating formatted executive HTML report at {output_html}...")
    ReportGenerator.generate_html_report(kpis, category_df, regional_df, anomalies, output_html)

    print("\n--- Pipeline Execution Summary ---")
    print(f"Total Net Revenue:   ${kpis['total_net_revenue']:,.2f}")
    print(f"Gross Profit:        ${kpis['total_profit']:,.2f}")
    print(f"Gross Margin:        {kpis['gross_margin_pct']}%")
    print(f"Average Order Value: ${kpis['average_order_value']:,.2f}")
    print(f"Anomalies Detected:  {len(anomalies)}")
    print(f"Report Location:     {os.path.abspath(output_html)}")
    print(f"JSON Digest:         {os.path.abspath(output_html.replace('.html', '.json'))}")
    print("----------------------------------\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Business Reporting Pipeline")
    parser.add_argument("--db-path", default="data/business_warehouse.db", help="Path to SQLite database")
    parser.add_argument("--output-dir", default="reports", help="Directory for generated reports")
    args = parser.parse_args()

    run_pipeline(args.db_path, args.output_dir)
