from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


ESSENTIAL_COLUMNS = [
    "order_id",
    "customer_id",
    "merchant_id",
    "order_created_at",
    "order_total_amount",
]


def _standardize_orders_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Try to standardize different raw schemas into the canonical one.

    This helps the project stay robust to minor naming changes
    in the source system.
    """
    rename_map = {}

    candidates = {
        "order_id": ["order_id", "id", "orderid"],
        "customer_id": ["customer_id", "consumer_id", "user_id"],
        "merchant_id": ["merchant_id", "restaurant_id", "store_id"],
        "order_created_at": ["order_created_at", "created_at", "order_date"],
        "order_total_amount": [
            "order_total_amount",
            "total_amount",
            "gmv",
            "order_amount",
        ],
        "origin_platform": ["origin_platform", "platform", "device"],
    }

    lower_cols = {c.lower(): c for c in df.columns}
    for std_col, raw_options in candidates.items():
        for raw in raw_options:
            if raw in df.columns:
                rename_map[raw] = std_col
                break
            if raw.lower() in lower_cols:
                rename_map[lower_cols[raw.lower()]] = std_col
                break

    df = df.rename(columns=rename_map)
    return df


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply data cleaning rules to a single orders DataFrame.

    - Standardize column names
    - Convert timestamps
    - Remove duplicate orders
    - Filter invalid values (order_total_amount <= 0)
    - Handle missing values
    """
    df = _standardize_orders_schema(df)

    # Drop rows missing essential identifiers or amount
    df = df.dropna(subset=["order_id", "customer_id", "merchant_id", "order_total_amount"])

    # Convert timestamp
    if "order_created_at" in df.columns:
        df["order_created_at"] = pd.to_datetime(df["order_created_at"], errors="coerce", utc=True)
        df = df.dropna(subset=["order_created_at"])

    # Ensure numeric
    df["order_total_amount"] = pd.to_numeric(df["order_total_amount"], errors="coerce")
    df = df.dropna(subset=["order_total_amount"])

    # Filter invalid amounts
    df = df[df["order_total_amount"] > 0]

    # Remove duplicates by order_id, keeping the latest record
    df = df.sort_values("order_created_at").drop_duplicates(subset=["order_id"], keep="last")

    # Handle missing origin platform
    if "origin_platform" in df.columns:
        df["origin_platform"] = df["origin_platform"].fillna("unknown").astype(str)
    else:
        df["origin_platform"] = "unknown"

    return df[
        [
            "order_id",
            "customer_id",
            "merchant_id",
            "order_created_at",
            "order_total_amount",
            "origin_platform",
        ]
    ].copy()


def prepare_fact_orders(
    orders: pd.DataFrame,
    ab_assignments: Optional[pd.DataFrame] = None,
    assignment_on: str = "customer_id",
    assignment_col: str = "is_target",
) -> pd.DataFrame:
    """
    Build the fact_orders analytical dataset from raw orders and A/B assignment.

    Parameters
    ----------
    orders : pd.DataFrame
        Raw orders data.
    ab_assignments : pd.DataFrame, optional
        A/B test reference table, containing at least:
        - a key column (default 'customer_id')
        - a treatment flag column (default 'is_target' or similar)
    assignment_on : str
        Join key between orders and ab_assignments.
    assignment_col : str
        Name of the treatment flag column in the output.

    Returns
    -------
    fact_orders : pd.DataFrame
        Cleaned and enriched fact table:
        order_id, customer_id, merchant_id, order_created_at,
        order_total_amount, origin_platform, is_target.
    """
    orders_clean = clean_orders(orders)

    if ab_assignments is not None:
        ab_df = ab_assignments.copy()

        # Try to standardize A/B flag column name to `assignment_col`
        if assignment_col not in ab_df.columns:
            for col in ab_df.columns:
                if col.lower() in {"variant", "arm", "group", "is_target", "target"}:
                    ab_df = ab_df.rename(columns={col: assignment_col})
                    break

        # If we still don't have the assignment column, treat everyone as control
        if assignment_col not in ab_df.columns:
            orders_clean["is_target"] = False
            fact_orders = orders_clean.copy()
            return fact_orders[
                [
                    "order_id",
                    "customer_id",
                    "merchant_id",
                    "order_created_at",
                    "order_total_amount",
                    "origin_platform",
                    "is_target",
                ]
            ].copy()

        # Convert typical labels to boolean flag
        if ab_df[assignment_col].dtype == object:
            ab_df[assignment_col] = (
                ab_df[assignment_col]
                .astype(str)
                .str.lower()
                .isin(["treatment", "target", "variant_b", "1", "true", "yes"])
            )

        fact_orders = orders_clean.merge(
            ab_df[[assignment_on, assignment_col]],
            how="left",
            left_on="customer_id",
            right_on=assignment_on,
        )
        if assignment_on != "customer_id":
            fact_orders = fact_orders.drop(columns=[assignment_on])

        fact_orders[assignment_col] = fact_orders[assignment_col].fillna(False).astype(bool)
    else:
        fact_orders = orders_clean.copy()
        fact_orders[assignment_col] = False

    fact_orders = fact_orders.rename(columns={assignment_col: "is_target"})

    return fact_orders[
        [
            "order_id",
            "customer_id",
            "merchant_id",
            "order_created_at",
            "order_total_amount",
            "origin_platform",
            "is_target",
        ]
    ].copy()


__all__ = ["clean_orders", "prepare_fact_orders"]

