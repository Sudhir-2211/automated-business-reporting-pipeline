import os
import pytest
import sqlite3
import pandas as pd
from src.data_generator import generate_synthetic_business_db
from src.pipeline import BusinessReportingPipeline


@pytest.fixture(scope="module")
def test_db(tmp_path_factory):
    db_file = str(tmp_path_factory.mktemp("data") / "test_business.db")
    generate_synthetic_business_db(db_file)
    return db_file


def test_extract_order_dataset(test_db):
    pipeline = BusinessReportingPipeline(test_db)
    df = pipeline.extract_order_dataset()
    assert not df.empty
    assert "net_revenue" in df.columns
    assert "profit" in df.columns
    assert "region" in df.columns
    assert "category" in df.columns


def test_compute_summary_kpis(test_db):
    pipeline = BusinessReportingPipeline(test_db)
    df = pipeline.extract_order_dataset()
    kpis = pipeline.compute_summary_kpis(df)

    assert kpis["total_orders"] > 0
    assert kpis["total_net_revenue"] > 0
    assert kpis["total_profit"] > 0
    assert 0 < kpis["gross_margin_pct"] <= 100
    assert kpis["average_order_value"] > 0


def test_empty_dataset_kpi_safety():
    pipeline = BusinessReportingPipeline(":memory:")
    empty_df = pd.DataFrame()
    kpis = pipeline.compute_summary_kpis(empty_df)
    assert kpis["total_orders"] == 0
    assert kpis["total_net_revenue"] == 0.0


def test_category_and_regional_breakdown(test_db):
    pipeline = BusinessReportingPipeline(test_db)
    df = pipeline.extract_order_dataset()

    cat_df = pipeline.compute_category_breakdown(df)
    assert not cat_df.empty
    assert "category" in cat_df.columns
    assert "margin_pct" in cat_df.columns

    reg_df = pipeline.compute_regional_breakdown(df)
    assert not reg_df.empty
    assert "region" in reg_df.columns
    assert "order_count" in reg_df.columns


def test_detect_daily_anomalies(test_db):
    pipeline = BusinessReportingPipeline(test_db)
    df = pipeline.extract_order_dataset()
    anomalies = pipeline.detect_daily_anomalies(df, z_threshold=1.8)
    assert isinstance(anomalies, list)
