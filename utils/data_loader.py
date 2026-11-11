"""Portable loading and schema normalization."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import pandas as pd

from .validators import validate_dataset

DEFAULT_DATASET = Path(__file__).resolve().parents[1] / "data" / "sales_dataset.xlsx"


def load_dataset(source: str | Path | BinaryIO = DEFAULT_DATASET) -> pd.DataFrame:
    """Load CSV/XLSX input and fail with a user-readable validation error."""
    name = str(getattr(source, "name", source)).lower()
    try:
        df = pd.read_csv(source) if name.endswith(".csv") else pd.read_excel(source)
    except (OSError, ValueError, ImportError) as exc:
        raise ValueError(f"Unable to read the dataset: {exc}") from exc
    errors = validate_dataset(df)
    if errors:
        raise ValueError("Invalid dataset: " + " ".join(errors))
    return df
