"""Cleaning and feature engineering rules used by the application."""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from .validators import validate_dataset

RETURN_STATUSES = {
    "Shipped - Returned to Seller",
    "Shipped - Returning to Seller",
}

_STATE_ALIASES = {
    "ANDAMAN & NICOBAR": "Andaman and Nicobar Islands",
    "ANDHRA PRADESH": "Andhra Pradesh",
    "ARUNACHAL PRADESH": "Arunachal Pradesh",
    "ASSAM": "Assam",
    "BIHAR": "Bihar",
    "CHANDIGARH": "Chandigarh",
    "CHHATTISGARH": "Chhattisgarh",
    "DELHI": "Delhi",
    "GOA": "Goa",
    "GUJARAT": "Gujarat",
    "HARYANA": "Haryana",
    "HIMACHAL PRADESH": "Himachal Pradesh",
    "JAMMU & KASHMIR": "Jammu and Kashmir",
    "JHARKHAND": "Jharkhand",
    "KARNATAKA": "Karnataka",
    "KERALA": "Kerala",
    "LADAKH": "Ladakh",
    "MADHYA PRADESH": "Madhya Pradesh",
    "MAHARASHTRA": "Maharashtra",
    "MANIPUR": "Manipur",
    "MEGHALAYA": "Meghalaya",
    "MIZORAM": "Mizoram",
    "NAGALAND": "Nagaland",
    "ODISHA": "Odisha",
    "PUDUCHERRY": "Puducherry",
    "PUNJAB": "Punjab",
    "RAJASTHAN": "Rajasthan",
    "SIKKIM": "Sikkim",
    "TAMIL NADU": "Tamil Nadu",
    "TELANGANA": "Telangana",
    "TRIPURA": "Tripura",
    "UTTAR PRADESH": "Uttar Pradesh",
    "UTTARAKHAND": "Uttarakhand",
    "WEST BENGAL": "West Bengal",
}


def standardize_state(value: object) -> str:
    """Normalize state casing and whitespace without inventing geography."""
    if pd.isna(value):
        return "Unknown"
    text = re.sub(r"\s+", " ", str(value).strip())
    return _STATE_ALIASES.get(text.upper(), text.title())


def standardize_category(value: object) -> str:
    """Normalize product category labels while preserving unknown labels."""
    if pd.isna(value):
        return "Unknown"
    text = re.sub(r"\s+", " ", str(value).strip())
    return text.title()


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Apply validated rules and add analysis-ready columns."""
    errors = validate_dataset(df)
    if errors:
        raise ValueError("Invalid dataset: " + " ".join(errors))
    clean = df.copy().drop_duplicates().reset_index(drop=True)
    clean["Date"] = pd.to_datetime(clean["Date"], errors="coerce")
    clean["Status"] = clean["Status"].fillna("Unknown").astype(str).str.strip()
    clean["Category"] = clean["Category"].map(standardize_category)
    if "ship-state" in clean:
        clean["ship-state"] = clean["ship-state"].map(standardize_state)
    else:
        clean["ship-state"] = "Unknown"
    clean["Amount"] = pd.to_numeric(clean["Amount"], errors="coerce")
    clean["Qty"] = pd.to_numeric(clean["Qty"], errors="coerce").fillna(0)
    non_cancelled_positive = clean.loc[
        (clean["Status"] != "Cancelled") & (clean["Amount"] > 0), "Amount"
    ]
    median_amount = float(non_cancelled_positive.median()) if not non_cancelled_positive.empty else 0.0
    clean["Amount_Imputed"] = clean["Amount"].isna()
    clean["Amount"] = clean["Amount"].fillna(median_amount)
    clean["Is_Cancelled"] = clean["Status"].eq("Cancelled")
    clean["Is_Returned"] = clean["Status"].isin(RETURN_STATUSES)
    clean["Revenue_Amount"] = clean["Amount"].where(~clean["Is_Cancelled"], 0.0)
    clean["Units_Sold"] = clean["Qty"].where(~clean["Is_Cancelled"], 0.0)
    clean["Month"] = clean["Date"].dt.to_period("M").astype("string")
    clean["Month_Label"] = clean["Date"].dt.strftime("%b %Y")
    clean["Day_Name"] = clean["Date"].dt.day_name()
    b2b = (
        clean["B2B"].map(lambda value: str(value).strip().lower() in {"true", "1", "yes", "y"})
        if "B2B" in clean
        else pd.Series(False, index=clean.index)
    )
    clean["B2B_Label"] = np.where(b2b, "B2B", "B2C")
    clean["Partial_Month"] = clean["Month"].eq("2022-03")
    return clean
