"""Consistent KPI calculations."""

from __future__ import annotations

import pandas as pd


def kpis(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {
            "order_records": 0, "unique_orders": 0, "revenue": 0.0,
            "cancelled_value": 0.0, "aov": 0.0, "units_sold": 0.0,
            "record_cancellation_rate": 0.0, "order_cancellation_rate": 0.0,
            "return_rate": 0.0,
        }
    active = df[~df["Is_Cancelled"]]
    return {
        "order_records": int(len(df)),
        "unique_orders": int(df["Order ID"].nunique()),
        "revenue": float(df["Revenue_Amount"].sum()),
        "cancelled_value": float(df.loc[df["Is_Cancelled"], "Amount"].sum()),
        "aov": float(df["Revenue_Amount"].sum() / active["Order ID"].nunique()) if active["Order ID"].nunique() else 0.0,
        "units_sold": float(df["Units_Sold"].sum()),
        "record_cancellation_rate": float(df["Is_Cancelled"].mean()),
        "order_cancellation_rate": float(
            df.loc[df["Is_Cancelled"], "Order ID"].nunique() / df["Order ID"].nunique()
        ) if df["Order ID"].nunique() else 0.0,
        "return_rate": float(df["Is_Returned"].sum() / len(active)) if len(active) else 0.0,
    }


def revenue_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    """Compare imputed values with a conservative zero-imputation scenario."""
    imputed = float(df["Revenue_Amount"].sum())
    zero_nulls = df["Revenue_Amount"].where(~df["Amount_Imputed"], 0).sum()
    return pd.DataFrame({"Scenario": ["Median imputation", "Null amounts treated as zero"],
                         "Revenue": [imputed, float(zero_nulls)]})
