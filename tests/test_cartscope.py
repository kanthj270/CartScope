import pandas as pd

from utils.calculations import kpis, revenue_sensitivity
from utils.data_cleaning import clean_dataset
from utils.data_loader import load_dataset
from utils.analytics import apply_filters
from utils.validators import validate_dataset


def sample():
    return pd.DataFrame({
        "Order ID": ["a", "a", "b", "c"],
        "Date": ["2022-03-31", "2022-03-31", "2022-04-01", "2022-04-02"],
        "Status": ["Shipped", "Shipped", "Cancelled", "Shipped - Returned to Seller"],
        "Category": ["kurta", "kurta", "Set", "Set"],
        "Qty": [1, 1, 2, 1],
        "Amount": [100, 100, 200, None],
        "ship-state": ["TAMIL NADU", "TAMIL NADU", "MAHARASHTRA", "DELHI"],
        "B2B": [False, False, False, True],
    })


def test_validation_and_duplicate_removal():
    df = clean_dataset(sample())
    assert validate_dataset(sample()) == []
    assert len(df) == 3
    assert df["ship-state"].tolist() == ["Tamil Nadu", "Maharashtra", "Delhi"]


def test_metric_definitions():
    df = clean_dataset(sample())
    result = kpis(df)
    assert result["order_records"] == 3
    assert result["unique_orders"] == 3
    assert result["revenue"] == 200
    assert result["units_sold"] == 2
    assert result["aov"] == 100
    assert result["record_cancellation_rate"] == 1 / 3
    assert result["return_rate"] == 1 / 2


def test_filters():
    df = clean_dataset(sample())
    filtered = apply_filters(df, {"Category": ["Set"], "ship-state": ["Delhi"]})
    assert len(filtered) == 1
    assert filtered.iloc[0]["Order ID"] == "c"


def test_loader_and_imputation(tmp_path):
    path = tmp_path / "sample.csv"
    sample().to_csv(path, index=False)
    cleaned = clean_dataset(load_dataset(path))
    assert cleaned["Amount_Imputed"].sum() == 1
    assert cleaned.loc[cleaned["Amount_Imputed"], "Amount"].iloc[0] == 100
    sensitivity = revenue_sensitivity(cleaned)
    assert sensitivity["Revenue"].tolist() == [200.0, 100.0]
