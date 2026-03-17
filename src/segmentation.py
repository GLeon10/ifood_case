from __future__ import annotations

import pandas as pd


def _rfm_scores(customer_metrics: pd.DataFrame) -> pd.DataFrame:
    """
    Compute R, F, M scores (1-5) based on quintiles.
    """
    df = customer_metrics.copy()

    # Lower recency (more recent) is better
    df["R_score"] = pd.qcut(df["recency"], 5, labels=[5, 4, 3, 2, 1])

    # Higher frequency and monetary are better
    df["F_score"] = pd.qcut(df["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    df["M_score"] = pd.qcut(df["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

    df["R_score"] = df["R_score"].astype(int)
    df["F_score"] = df["F_score"].astype(int)
    df["M_score"] = df["M_score"].astype(int)

    df["RFM_score"] = df["R_score"] * 100 + df["F_score"] * 10 + df["M_score"]
    return df


def _segment_from_scores(row) -> str:
    """
    Map RFM scores to business-friendly segments.
    """
    r, f, m = row["R_score"], row["F_score"], row["M_score"]

    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal"
    if r >= 3 and m >= 3:
        return "Potential"
    if r <= 2 and f >= 3:
        return "At Risk"
    return "Low Engagement"


def assign_rfm_segments(customer_metrics: pd.DataFrame) -> pd.DataFrame:
    """
    Assign RFM-based segments to each customer.

    Segments:
    - Champions
    - Loyal
    - Potential
    - At Risk
    - Low Engagement
    """
    df = _rfm_scores(customer_metrics)
    df["segment"] = df.apply(_segment_from_scores, axis=1)
    return df


def segment_ab_performance(
    fact_orders: pd.DataFrame,
    segmented_customers: pd.DataFrame,
) -> pd.DataFrame:
    """
    Analyze A/B test performance by RFM segment.

    Returns a DataFrame by segment and is_target with:
    - users
    - conversion_rate
    - orders_per_user
    - gmv_per_user
    """
    # Merge segment labels into orders
    merged = fact_orders.merge(
        segmented_customers[["customer_id", "segment"]],
        on="customer_id",
        how="left",
    )

    user = (
        merged.groupby(["segment", "customer_id", "is_target"])
        .agg(
            total_orders=("order_id", "nunique"),
            gmv=("order_total_amount", "sum"),
        )
        .reset_index()
    )
    user["converted"] = user["total_orders"] > 0

    grouped = (
        user.groupby(["segment", "is_target"])
        .agg(
            users=("customer_id", "nunique"),
            conversion_rate=("converted", "mean"),
            orders_per_user=("total_orders", "mean"),
            gmv_per_user=("gmv", "mean"),
        )
        .reset_index()
    )

    return grouped


__all__ = ["assign_rfm_segments", "segment_ab_performance"]

