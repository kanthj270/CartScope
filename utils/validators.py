"""Input validation for CartScope datasets."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

REQUIRED_COLUMNS = {"Order ID", "Date", "Status", "Category", "Qty", "Amount"}


def validate_dataset(df: pd.DataFrame) -> list[str]:
    """Return actionable validation errors; an empty list means valid."""
    errors: list[str] = []
    if not isinstance(df, pd.DataFrame):
        return ["The uploaded object is not a tabular dataset."]
    if df.empty:
        return ["The dataset is empty."]
    missing = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}.")
    if "Date" in df and pd.to_datetime(df["Date"], errors="coerce").notna().sum() == 0:
        errors.append("Date must contain at least one recognizable date.")
    if "Order ID" in df and df["Order ID"].dropna().empty:
        errors.append("Order ID must contain at least one value.")
    return errors


def first_column(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    """Find the first available column from a list of aliases."""
    return next((name for name in candidates if name in df.columns), None)
