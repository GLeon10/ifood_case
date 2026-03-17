from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd


def compute_customer_metrics(
    fact_orders: pd.DataFrame,
    as_of: datetime | None = None,
) -> pd.DataFrame:
    """
    Compute user-level RFM-style metrics from fact_orders.

    Metrics:
    - total_orders
    - total_spent
    - avg_order_value
    - first_order_date
    - last_order_date
    - recency (days since last order, at `as_of`)
    - frequency (orders count)
    - monetary (alias of total_spent)
    """
    if as_of is None:
        # Use max observed order_created_at as reference date
        as_of = fact_orders["order_created_at"].max()
        if isinstance(as_of, pd.Timestamp):
            as_of = as_of.to_pydatetime()
        if as_of.tzinfo is None:
            as_of = as_of.replace(tzinfo=timezone.utc)

    df = fact_orders.copy()
    df["order_created_at"] = pd.to_datetime(df["order_created_at"], utc=True)

    grouped = df.groupby("customer_id").agg(
        total_orders=("order_id", "nunique"),
        total_spent=("order_total_amount", "sum"),
        avg_order_value=("order_total_amount", "mean"),
        first_order_date=("order_created_at", "min"),
        last_order_date=("order_created_at", "max"),
    )

    # Recency in days
    recency_timedelta = as_of - grouped["last_order_date"].dt.to_pydatetime()
    grouped["recency"] = recency_timedelta / pd.Timedelta(days=1)

    grouped["frequency"] = grouped["total_orders"]
    grouped["monetary"] = grouped["total_spent"]

    customer_metrics = grouped.reset_index()

    return customer_metrics[
        [
            "customer_id",
            "total_orders",
            "total_spent",
            "avg_order_value",
            "first_order_date",
            "last_order_date",
            "recency",
            "frequency",
            "monetary",
        ]
    ]


__all__ = ["compute_customer_metrics"]

