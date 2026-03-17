from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


BASE_DIR = Path(__file__).resolve().parents[1]
CHARTS_DIR = BASE_DIR / "outputs" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def _save_current_fig(name: str) -> Path:
    path = CHARTS_DIR / f"{name}.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_conversion_rate_comparison(ab_metrics: pd.DataFrame) -> Path:
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(
        data=ab_metrics,
        x="is_target",
        y="conversion_rate",
        ax=ax,
        palette=["#1f77b4", "#ff7f0e"],
    )
    ax.set_xlabel("Group (False = Control, True = Target)")
    ax.set_ylabel("Conversion rate")
    ax.set_title("Conversion rate by group")
    return _save_current_fig("conversion_rate_comparison")


def plot_gmv_per_user_comparison(ab_metrics: pd.DataFrame) -> Path:
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(
        data=ab_metrics,
        x="is_target",
        y="gmv_per_user",
        ax=ax,
        palette=["#1f77b4", "#ff7f0e"],
    )
    ax.set_xlabel("Group (False = Control, True = Target)")
    ax.set_ylabel("GMV per user")
    ax.set_title("GMV per user by group")
    return _save_current_fig("gmv_per_user_comparison")


def plot_order_value_distribution(fact_orders: pd.DataFrame) -> Path:
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.histplot(
        data=fact_orders,
        x="order_total_amount",
        hue="is_target",
        kde=True,
        ax=ax,
        element="step",
        stat="density",
    )
    ax.set_xlabel("Order value")
    ax.set_title("Order value distribution by group")
    return _save_current_fig("order_value_distribution")


def plot_uplift_by_segment(segment_metrics: pd.DataFrame) -> Path:
    """
    Expect segment_metrics from segment_ab_performance.
    """
    # Pivot to compute uplift in GMV per user between target and control
    pivot = segment_metrics.pivot(
        index="segment", columns="is_target", values="gmv_per_user"
    )
    pivot["uplift"] = pivot[True] - pivot[False]
    uplift_df = pivot.reset_index()

    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(
        data=uplift_df,
        x="segment",
        y="uplift",
        ax=ax,
        palette="viridis",
    )
    ax.set_xlabel("Segment")
    ax.set_ylabel("GMV per user uplift (target - control)")
    ax.set_title("Coupon uplift by RFM segment")
    ax.tick_params(axis="x", rotation=30)
    return _save_current_fig("uplift_by_segment")


def plot_rfm_distribution(segmented_customers: pd.DataFrame) -> Path:
    sns.set(style="whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    sns.histplot(segmented_customers["recency"], ax=axes[0], bins=30)
    axes[0].set_title("Recency distribution")
    axes[0].set_xlabel("Recency (days)")

    sns.histplot(segmented_customers["frequency"], ax=axes[1], bins=30)
    axes[1].set_title("Frequency distribution")
    axes[1].set_xlabel("Orders")

    sns.histplot(segmented_customers["monetary"], ax=axes[2], bins=30)
    axes[2].set_title("Monetary distribution")
    axes[2].set_xlabel("GMV")

    return _save_current_fig("rfm_distribution")


__all__ = [
    "plot_conversion_rate_comparison",
    "plot_gmv_per_user_comparison",
    "plot_order_value_distribution",
    "plot_uplift_by_segment",
    "plot_rfm_distribution",
]

