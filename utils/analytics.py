"""Reusable aggregations for dashboard pages."""

from __future__ import annotations

import pandas as pd


def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["Month", "Month_Label"], as_index=False)["Revenue_Amount"].sum().sort_values("Month")


def group_revenue(df: pd.DataFrame, column: str, limit: int | None = None) -> pd.DataFrame:
    result = df.groupby(column, dropna=False, as_index=False).agg(
        Revenue=("Revenue_Amount", "sum"), Units=("Units_Sold", "sum"),
        Records=("Order ID", "size"), Orders=("Order ID", "nunique")
    ).sort_values("Revenue", ascending=False)
    return result.head(limit) if limit else result


def problematic_skus(df: pd.DataFrame, limit: int = 20) -> pd.DataFrame:
    result = df.groupby("SKU", dropna=False).agg(
        Records=("Order ID", "size"), Revenue=("Revenue_Amount", "sum"),
        Cancellation_Rate=("Is_Cancelled", "mean"), Return_Rate=("Is_Returned", "mean")
    ).reset_index()
    result["Issue_Rate"] = result["Cancellation_Rate"] + result["Return_Rate"]
    return result.sort_values(["Issue_Rate", "Records"], ascending=False).head(limit)


def apply_filters(df: pd.DataFrame, filters: dict[str, object]) -> pd.DataFrame:
    """Apply only non-empty filter values, keeping all dashboard filters centralized."""
    result = df
    for column, value in filters.items():
        if value is None or value == "All" or value == []:
            continue
        values = value if isinstance(value, (list, tuple, set)) else [value]
        if column in result:
            result = result[result[column].isin(values)]
    return result
