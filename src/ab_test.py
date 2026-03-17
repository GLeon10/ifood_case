from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats import proportion as sm_proportion


def _user_level_from_orders(fact_orders: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate order-level fact table to user-level A/B dataset.
    """
    df = fact_orders.copy()
    user = (
        df.groupby(["customer_id", "is_target"])
        .agg(
            total_orders=("order_id", "nunique"),
            gmv=("order_total_amount", "sum"),
        )
        .reset_index()
    )
    user["orders_per_user"] = user["total_orders"]
    user["gmv_per_user"] = user["gmv"]
    user["converted"] = user["total_orders"] > 0
    return user


def compute_ab_metrics(fact_orders: pd.DataFrame) -> pd.DataFrame:
    """
    Compute A/B test metrics from fact_orders.

    Returns a DataFrame indexed by is_target (False = control, True = target)
    with columns:
    - users
    - conversion_rate
    - orders_per_user
    - gmv
    - gmv_per_user
    - average_order_value
    """
    user = _user_level_from_orders(fact_orders)

    # Number of users by group
    group_users = user.groupby("is_target")["customer_id"].nunique().rename("users")

    # Conversion rate (at least one order within window)
    conv = (
        user.groupby("is_target")["converted"].mean().rename("conversion_rate")
    )

    # Orders per user within group
    orders_per_user = (
        user.groupby("is_target")["orders_per_user"].mean().rename("orders_per_user")
    )

    # GMV per group and per user
    gmv = fact_orders.groupby("is_target")["order_total_amount"].sum().rename("gmv")
    gmv_per_user = (gmv / group_users).rename("gmv_per_user")

    # Average order value (order-level)
    aov = (
        fact_orders.groupby("is_target")["order_total_amount"].mean().rename(
            "average_order_value"
        )
    )

    metrics = pd.concat(
        [group_users, conv, orders_per_user, gmv, gmv_per_user, aov],
        axis=1,
    ).reset_index()

    return metrics


@dataclass
class TTestResult:
    p_value: float
    ci_low: float
    ci_high: float
    significant: bool


def t_test_order_value(
    fact_orders: pd.DataFrame,
    alpha: float = 0.05,
) -> TTestResult:
    """
    Welch t-test comparing order_total_amount between target and control.
    """
    control = fact_orders.loc[~fact_orders["is_target"], "order_total_amount"].values
    treatment = fact_orders.loc[fact_orders["is_target"], "order_total_amount"].values

    t_stat, p_val = stats.ttest_ind(
        treatment, control, equal_var=False, nan_policy="omit"
    )

    # Compute confidence interval for difference in means
    mean_diff = np.nanmean(treatment) - np.nanmean(control)
    n1, n0 = len(treatment), len(control)
    var1, var0 = np.nanvar(treatment, ddof=1), np.nanvar(control, ddof=1)
    se = np.sqrt(var1 / n1 + var0 / n0)

    z = stats.norm.ppf(1 - alpha / 2)
    ci_low = mean_diff - z * se
    ci_high = mean_diff + z * se

    return TTestResult(
        p_value=float(p_val),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        significant=bool(p_val < alpha),
    )


@dataclass
class ProportionTestResult:
    p_value: float
    ci_low: float
    ci_high: float
    significant: bool


def proportion_test_conversion(
    fact_orders: pd.DataFrame,
    alpha: float = 0.05,
) -> ProportionTestResult:
    """
    Proportion z-test for conversion rate (users with >=1 order).
    """
    user = _user_level_from_orders(fact_orders)

    group = user.groupby("is_target").agg(
        conversions=("converted", "sum"),
        users=("customer_id", "nunique"),
    )

    # Ensure control is index 0, treatment 1
    control = group.loc[False]
    treatment = group.loc[True]

    count = np.array([treatment["conversions"], control["conversions"]], dtype=float)
    nobs = np.array([treatment["users"], control["users"]], dtype=float)

    stat, p_val = sm_proportion.proportions_ztest(count, nobs)

    # Confidence interval for difference in proportions (Wald)
    p1 = count[0] / nobs[0]
    p0 = count[1] / nobs[1]
    diff = p1 - p0
    se = np.sqrt(p1 * (1 - p1) / nobs[0] + p0 * (1 - p0) / nobs[1])
    z = stats.norm.ppf(1 - alpha / 2)
    ci_low = diff - z * se
    ci_high = diff + z * se

    return ProportionTestResult(
        p_value=float(p_val),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        significant=bool(p_val < alpha),
    )


def evaluate_coupon_viability(
    ab_metrics: pd.DataFrame,
    coupon_value: float = 10.0,
    ifood_take_rate: float = 0.15,
) -> Dict[str, float]:
    """
    Evaluate financial viability of the coupon campaign.

    Expects ab_metrics from compute_ab_metrics with columns:
    - is_target
    - users
    - gmv_per_user
    """
    metrics = ab_metrics.set_index("is_target")
    treatment = metrics.loc[True]
    control = metrics.loc[False]

    n_target_users = treatment["users"]

    incremental_gmv_per_user = treatment["gmv_per_user"] - control["gmv_per_user"]
    incremental_gmv = incremental_gmv_per_user * n_target_users

    incremental_revenue = incremental_gmv * ifood_take_rate
    coupon_cost = coupon_value * n_target_users
    net_profit = incremental_revenue - coupon_cost

    return {
        "incremental_gmv": float(incremental_gmv),
        "incremental_revenue": float(incremental_revenue),
        "coupon_cost": float(coupon_cost),
        "net_profit": float(net_profit),
    }


__all__ = [
    "compute_ab_metrics",
    "t_test_order_value",
    "proportion_test_conversion",
    "evaluate_coupon_viability",
    "TTestResult",
    "ProportionTestResult",
]

