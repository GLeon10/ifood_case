from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import ingestion
from .ab_test import (
    compute_ab_metrics,
    evaluate_coupon_viability,
    proportion_test_conversion,
    t_test_order_value,
)
from .feature_engineering import compute_customer_metrics
from .processing import prepare_fact_orders
from .segmentation import assign_rfm_segments, segment_ab_performance
from .visualization import (
    plot_conversion_rate_comparison,
    plot_gmv_per_user_comparison,
    plot_order_value_distribution,
    plot_rfm_distribution,
    plot_uplift_by_segment,
)


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
TABLES_DIR = BASE_DIR / "outputs" / "tables"

TABLES_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


ORDERS_URL = "https://data-architect-test-source.s3-sa-east-1.amazonaws.com/order.json.gz"
CONSUMER_URL = "https://data-architect-test-source.s3-sa-east-1.amazonaws.com/consumer.csv.gz"
RESTAURANT_URL = "https://data-architect-test_source.s3-sa-east-1.amazonaws.com/restaurant.csv.gz"
AB_TEST_URL = "https://data-architect-test-source.s3-sa-east-1.amazonaws.com/ab_test_ref.tar.gz"


def run_pipeline() -> None:
    """
    End-to-end pipeline that:
    - downloads and extracts raw data
    - builds fact_orders
    - computes customer metrics and segments
    - runs A/B test analysis and financial evaluation
    - saves key tables and charts
    """
    ingestion.ensure_raw_dir()

    # Download orders and AB test reference
    orders_gz = ingestion.download_file(ORDERS_URL, RAW_DIR / "order.json.gz")
    orders_path = ingestion.extract_gzip(orders_gz)

    ab_tar = ingestion.download_file(AB_TEST_URL, RAW_DIR / "ab_test_ref.tar.gz")
    ab_dir = ingestion.extract_tar(ab_tar)

    # Load AB reference – ignore hidden/metadata files like ._ab_test_ref.csv
    ab_files = [f for f in ab_dir.glob("*.csv") if not f.name.startswith("._")]
    if not ab_files:
        ab_files = [f for f in ab_dir.glob("*.tsv") if not f.name.startswith("._")]
    if not ab_files:
        raise FileNotFoundError("No valid AB reference CSV/TSV found in extracted archive.")

    # The reference file is text; default UTF-8 should work, but we can
    # fall back to latin1 if needed to avoid UnicodeDecodeError.
    try:
        ab_ref = pd.read_csv(ab_files[0])
    except UnicodeDecodeError:
        ab_ref = pd.read_csv(ab_files[0], encoding="latin1")

    # Stream orders and concatenate into a single DataFrame for processing.
    # For a truly massive dataset this could be further chunked, but for this
    # exercise we keep it simple while respecting streaming ingestion.
    order_chunks = list(ingestion.load_orders_json_streaming(orders_path, chunksize=200_000))
    orders_df = pd.concat(order_chunks, ignore_index=True)

    fact_orders = prepare_fact_orders(orders_df, ab_assignments=ab_ref)
    # Use CSV to avoid extra parquet dependencies (pyarrow/fastparquet)
    fact_orders.to_csv(PROCESSED_DIR / "fact_orders.csv", index=False)

    # Customer metrics and segmentation
    customer_metrics = compute_customer_metrics(fact_orders)
    segmented_customers = assign_rfm_segments(customer_metrics)

    customer_metrics.to_csv(PROCESSED_DIR / "customer_metrics.csv", index=False)
    segmented_customers.to_csv(PROCESSED_DIR / "segmented_customers.csv", index=False)

    # A/B metrics and tests
    ab_metrics = compute_ab_metrics(fact_orders)
    ttest_res = t_test_order_value(fact_orders)
    prop_res = proportion_test_conversion(fact_orders)
    finance = evaluate_coupon_viability(ab_metrics)

    ab_metrics.to_csv(TABLES_DIR / "ab_metrics.csv", index=False)

    summary = {
        "t_test_p_value": ttest_res.p_value,
        "t_test_ci_low": ttest_res.ci_low,
        "t_test_ci_high": ttest_res.ci_high,
        "t_test_significant": ttest_res.significant,
        "prop_test_p_value": prop_res.p_value,
        "prop_test_ci_low": prop_res.ci_low,
        "prop_test_ci_high": prop_res.ci_high,
        "prop_test_significant": prop_res.significant,
        **finance,
    }
    pd.DataFrame([summary]).to_csv(TABLES_DIR / "summary.csv", index=False)

    # Segment analysis
    segment_metrics = segment_ab_performance(fact_orders, segmented_customers)
    segment_metrics.to_csv(TABLES_DIR / "segment_metrics.csv", index=False)

    # Charts
    plot_conversion_rate_comparison(ab_metrics)
    plot_gmv_per_user_comparison(ab_metrics)
    plot_order_value_distribution(fact_orders)
    plot_rfm_distribution(segmented_customers)
    plot_uplift_by_segment(segment_metrics)


if __name__ == "__main__":
    run_pipeline()

