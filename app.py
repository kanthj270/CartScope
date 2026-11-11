"""CartScope - E-Commerce Intelligence & Analytics Platform."""

from __future__ import annotations

import io

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.analytics import apply_filters, group_revenue, monthly_revenue, problematic_skus
from utils.calculations import kpis, revenue_sensitivity
from utils.data_cleaning import clean_dataset
from utils.data_loader import DEFAULT_DATASET, load_dataset

st.set_page_config(page_title="CartScope", page_icon="📊", layout="wide")

st.markdown(
    """<style>
    [data-testid="stSidebar"] {background: #101b35;}
    [data-testid="stSidebar"] * {color: #f7f9fc;}
    .brand {font-size: 2rem; font-weight: 800; color: #f97316; margin-bottom: 0;}
    .subtitle {color: #64748b; margin-top: 0;}
    .kpi {background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
          padding: 18px; min-height: 100px; box-shadow: 0 2px 6px #0f172a0d;}
    .kpi-label {color: #64748b; font-size: .82rem; text-transform: uppercase; letter-spacing: .04em;}
    .kpi-value {color: #101b35; font-size: 1.55rem; font-weight: 750; margin-top: 7px;}
    </style>""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Loading and cleaning dataset...")
def get_data(source: str = str(DEFAULT_DATASET)) -> pd.DataFrame:
    return clean_dataset(load_dataset(source))


def money(value: float) -> str:
    return f"₹{value:,.0f}"


def render_kpis(df: pd.DataFrame) -> None:
    values = kpis(df)
    cards = [
        ("Order records", f"{values['order_records']:,}"),
        ("Unique orders", f"{values['unique_orders']:,}"),
        ("Revenue", money(values["revenue"])),
        ("AOV", money(values["aov"])),
        ("Units sold", f"{values['units_sold']:,.0f}"),
        ("Cancellation rate", f"{values['record_cancellation_rate']:.1%}"),
        ("Return rate", f"{values['return_rate']:.1%}"),
    ]
    cols = st.columns(len(cards))
    for col, (label, value) in zip(cols, cards):
        col.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)


def chart(data: pd.DataFrame, kind: str, x: str, y: str, title: str, **kwargs: object) -> None:
    if data.empty:
        st.info("No data matches the current filters.")
        return
    figure = getattr(px, kind)(data, x=x, y=y, title=title, **kwargs)
    figure.update_layout(
        template="plotly_white", height=380, margin=dict(l=10, r=10, t=55, b=10),
        yaxis={"automargin": True}, xaxis={"automargin": True},
    )
    st.plotly_chart(figure, width="stretch")


def filter_panel(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.markdown('<div class="brand">CartScope</div><div class="subtitle">E-Commerce Intelligence & Analytics Platform</div>', unsafe_allow_html=True)
        st.divider()
        page = st.radio("Navigate", ["Executive Overview", "Sales Analytics", "Regional Analytics", "Product Analytics", "Order & Fulfilment", "Data Explorer"])
        st.subheader("Global filters")
        date_values = df["Date"].dropna()
        date_range = st.date_input("Date range", (date_values.min().date(), date_values.max().date()))
        months = st.multiselect("Month", sorted(df["Month"].dropna().unique()))
        categories = st.multiselect("Category", sorted(df["Category"].unique()))
        states = st.multiselect("State", sorted(df["ship-state"].unique()))
        statuses = st.multiselect("Order status", sorted(df["Status"].unique()))
        fulfilments = st.multiselect("Fulfilment", sorted(df["Fulfilment"].dropna().unique())) if "Fulfilment" in df else []
        b2b = st.multiselect("Customer type", ["B2B", "B2C"])
        apply = st.button("Apply filters", type="primary")
        reset = st.button("Reset")
    if reset:
        st.session_state.pop("active_filters", None)
        st.rerun()
    if not apply and "active_filters" not in st.session_state:
        st.session_state.active_filters = {}
    if apply:
        start, end = date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (date_values.min().date(), date_values.max().date())
        st.session_state.active_filters = {
            "Month": months, "Category": categories, "ship-state": states, "Status": statuses,
            "Fulfilment": fulfilments, "B2B_Label": b2b,
            "_date_range": (pd.Timestamp(start), pd.Timestamp(end)),
        }
    filters = st.session_state.get("active_filters", {})
    date_filter = filters.get("_date_range")
    filtered = apply_filters(df, {k: v for k, v in filters.items() if not k.startswith("_")})
    if date_filter:
        filtered = filtered[filtered["Date"].between(*date_filter)]
    return filtered, page


def overview(df: pd.DataFrame) -> None:
    st.header("Executive Overview")
    st.caption("Decision-ready performance view using cancellation-excluded revenue and units.")
    render_kpis(df)
    left, right = st.columns(2)
    with left:
        monthly = monthly_revenue(df)
        chart(monthly, "line", "Month_Label", "Revenue_Amount", "Monthly revenue (March is partial)", markers=True)
    with right:
        status = df["Status"].value_counts().rename_axis("Status").reset_index(name="Records")
        chart(status, "bar", "Records", "Status", "Order status distribution", color="Status", orientation="h")
    left, right = st.columns(2)
    with left:
        category = group_revenue(df, "Category")
        chart(category, "bar", "Category", "Revenue", "Revenue by category", color="Category")
    with right:
        region = group_revenue(df, "ship-state", 10)
        chart(region, "bar", "ship-state", "Revenue", "Top states by revenue", color="ship-state")
    st.subheader("Business insights")
    top = group_revenue(df, "Category", 1)
    state = group_revenue(df, "ship-state", 1)
    if not top.empty and not state.empty:
        st.info(f"{top.iloc[0]['Category']} is the leading category by revenue; {state.iloc[0]['ship-state']} leads state revenue in the selected slice.")


def sales(df: pd.DataFrame) -> None:
    st.header("Sales Analytics")
    left, right = st.columns(2)
    with left:
        chart(monthly_revenue(df), "line", "Month_Label", "Revenue_Amount", "Monthly revenue", markers=True)
    with right:
        daily = df.groupby("Day_Name", as_index=False)["Revenue_Amount"].sum()
        daily["sort"] = pd.Categorical(daily["Day_Name"], ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        chart(daily.sort_values("sort"), "bar", "Day_Name", "Revenue_Amount", "Revenue by weekday")
    chart(group_revenue(df, "Category"), "bar", "Category", "Revenue", "Category performance", color="Category")
    st.caption("March 2022 is partial in the source data (starting 31 March), so avoid direct full-month comparisons.")


def regional(df: pd.DataFrame) -> None:
    st.header("Regional Analytics")
    top = group_revenue(df, "ship-state", 10)
    chart(top, "bar", "ship-state", "Revenue", "Top 10 states by revenue", color="ship-state")
    orders = group_revenue(df, "ship-state", 10).sort_values("Orders", ascending=False)
    chart(orders, "bar", "ship-state", "Orders", "Top states by unique orders", color="ship-state")
    st.dataframe(group_revenue(df, "ship-state"), width="stretch", hide_index=True)


def product(df: pd.DataFrame) -> None:
    st.header("Product Analytics")
    left, right = st.columns(2)
    with left:
        chart(group_revenue(df, "Category"), "bar", "Category", "Units", "Units sold by category", color="Category")
    with right:
        if "Size" in df:
            size = df.groupby("Size", as_index=False)["Units_Sold"].sum().sort_values("Units_Sold", ascending=False)
            chart(size, "bar", "Size", "Units_Sold", "Units sold by size", color="Size")
    if "SKU" in df:
        st.subheader("Problematic SKUs (cancellation + return rates)")
        st.dataframe(problematic_skus(df), width="stretch", hide_index=True)


def fulfilment(df: pd.DataFrame) -> None:
    st.header("Order & Fulfilment Analytics")
    left, right = st.columns(2)
    with left:
        status = df["Status"].value_counts().rename_axis("Status").reset_index(name="Records")
        chart(status, "bar", "Records", "Status", "Status mix", color="Status", orientation="h")
    with right:
        if "Fulfilment" in df:
            f = df.groupby("Fulfilment", as_index=False).agg(Records=("Order ID", "size"), Revenue=("Revenue_Amount", "sum"))
            chart(f, "bar", "Fulfilment", "Records", "Records by fulfilment", color="Fulfilment")
    st.metric("Cancelled order value (reported separately)", money(kpis(df)["cancelled_value"]))
    st.caption("Return analysis includes both returned and returning-to-seller statuses. Delivery comparisons are not inferred where source fields do not support them.")


def explorer(df: pd.DataFrame) -> None:
    st.header("Data Explorer")
    upload = st.file_uploader("Upload CSV or XLSX", type=["csv", "xlsx"])
    if upload:
        try:
            df = clean_dataset(load_dataset(upload))
            st.success(f"Loaded {len(df):,} cleaned records.")
        except ValueError as exc:
            st.error(str(exc))
            return
    st.write(f"**Shape:** {df.shape[0]:,} rows × {df.shape[1]} columns")
    tab1, tab2, tab3 = st.tabs(["Preview", "Quality", "Statistics"])
    with tab1:
        st.dataframe(df.head(100), width="stretch", hide_index=True)
        st.download_button("Download filtered CSV", df.to_csv(index=False).encode("utf-8"), "cartscope_filtered.csv", "text/csv")
    with tab2:
        quality = pd.DataFrame({"Column": df.columns, "Type": [str(t) for t in df.dtypes], "Missing": df.isna().sum().values, "Unique": df.nunique(dropna=False).values})
        st.dataframe(quality, width="stretch", hide_index=True)
        st.metric("Exact duplicate records", int(df.duplicated().sum()))
    with tab3:
        statistics = df.describe(include="all").T.reset_index(names="Statistic").astype("string")
        st.dataframe(statistics, width="stretch", hide_index=True)


def main() -> None:
    st.markdown('<div class="brand">CartScope</div><div class="subtitle">E-Commerce Intelligence & Analytics Platform</div>', unsafe_allow_html=True)
    try:
        data = get_data()
    except ValueError as exc:
        st.error(str(exc))
        st.stop()
    filtered, page = filter_panel(data)
    st.caption(f"Showing {len(filtered):,} of {len(data):,} cleaned records")
    if page == "Executive Overview":
        overview(filtered)
    elif page == "Sales Analytics":
        sales(filtered)
    elif page == "Regional Analytics":
        regional(filtered)
    elif page == "Product Analytics":
        product(filtered)
    elif page == "Order & Fulfilment":
        fulfilment(filtered)
    else:
        explorer(filtered)


if __name__ == "__main__":
    main()
