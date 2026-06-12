"""Interactive Streamlit dashboard for exploring loan datasets."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st


COMMON_COLUMN_ALIASES = {
    "loan_amount": ["loan_amount", "loanamount", "loan_amnt", "amount", "principal"],
    "interest_rate": ["interest_rate", "interest", "int_rate", "rate"],
    "income": ["income", "annual_income", "annual_inc", "applicantincome"],
    "term": ["term", "loan_term", "duration"],
    "status": ["loan_status", "status", "approval_status", "approved"],
    "grade": ["grade", "risk_grade", "loan_grade"],
    "purpose": ["purpose", "loan_purpose", "reason"],
    "employment_length": ["emp_length", "employment_length", "employment"],
    "credit_score": ["credit_score", "fico", "fico_score", "cibil_score"],
}


@dataclass(frozen=True)
class DashboardColumns:
    """Resolved column names used by dashboard visuals."""

    loan_amount: str | None = None
    interest_rate: str | None = None
    income: str | None = None
    term: str | None = None
    status: str | None = None
    grade: str | None = None
    purpose: str | None = None
    employment_length: str | None = None
    credit_score: str | None = None


def normalize_column_name(column_name: str) -> str:
    """Normalize a column name so aliases can be matched consistently."""

    return re.sub(r"[^a-z0-9]", "", column_name.lower())


def resolve_columns(columns: Iterable[str]) -> DashboardColumns:
    """Map known loan-data concepts to the columns present in a dataset."""

    normalized = {normalize_column_name(column): column for column in columns}
    resolved: dict[str, str | None] = {}

    for concept, aliases in COMMON_COLUMN_ALIASES.items():
        resolved[concept] = None
        for alias in aliases:
            match = normalized.get(normalize_column_name(alias))
            if match is not None:
                resolved[concept] = match
                break

    return DashboardColumns(**resolved)


def create_sample_dataset() -> pd.DataFrame:
    """Create a small sample dataset so the dashboard works before upload."""

    return pd.DataFrame(
        {
            "loan_amount": [5000, 12000, 8000, 25000, 16000, 30000, 7000, 18500, 11000, 22000],
            "interest_rate": [7.5, 9.2, 6.8, 13.4, 10.5, 15.1, 8.0, 11.8, 7.9, 12.6],
            "annual_income": [42000, 68000, 54000, 120000, 75000, 95000, 39000, 83000, 61000, 102000],
            "term": [36, 60, 36, 60, 36, 60, 36, 60, 36, 60],
            "loan_status": [
                "Approved",
                "Approved",
                "Approved",
                "Rejected",
                "Approved",
                "Rejected",
                "Approved",
                "Approved",
                "Approved",
                "Rejected",
            ],
            "grade": ["A", "B", "A", "D", "C", "E", "B", "C", "A", "D"],
            "purpose": [
                "Debt consolidation",
                "Home improvement",
                "Education",
                "Business",
                "Car",
                "Debt consolidation",
                "Medical",
                "Home improvement",
                "Car",
                "Business",
            ],
            "credit_score": [720, 690, 735, 640, 675, 610, 705, 665, 730, 650],
        }
    )


def coerce_numeric(df: pd.DataFrame, columns: Iterable[str | None]) -> pd.DataFrame:
    """Return a copy with selected columns converted to numeric values where possible."""

    cleaned = df.copy()
    for column in columns:
        if column and column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    return cleaned


def render_metric_cards(df: pd.DataFrame, columns: DashboardColumns) -> None:
    """Render high-level KPI cards for the active dataset."""

    metric_columns = st.columns(4)
    metric_columns[0].metric("Records", f"{len(df):,}")

    if columns.loan_amount:
        metric_columns[1].metric("Total loan amount", f"${df[columns.loan_amount].sum(skipna=True):,.0f}")
        metric_columns[2].metric("Average loan", f"${df[columns.loan_amount].mean(skipna=True):,.0f}")
    else:
        metric_columns[1].metric("Total loan amount", "N/A")
        metric_columns[2].metric("Average loan", "N/A")

    if columns.interest_rate:
        metric_columns[3].metric("Avg interest rate", f"{df[columns.interest_rate].mean(skipna=True):.2f}%")
    else:
        metric_columns[3].metric("Avg interest rate", "N/A")


def render_sidebar_filters(df: pd.DataFrame, columns: DashboardColumns) -> pd.DataFrame:
    """Render filters in the sidebar and return the filtered dataset."""

    filtered = df.copy()
    st.sidebar.header("Filters")

    for label, column in [
        ("Loan status", columns.status),
        ("Grade", columns.grade),
        ("Purpose", columns.purpose),
        ("Term", columns.term),
    ]:
        if not column or column not in filtered.columns:
            continue
        options = sorted(filtered[column].dropna().astype(str).unique())
        selected = st.sidebar.multiselect(label, options, default=options)
        if selected:
            filtered = filtered[filtered[column].astype(str).isin(selected)]

    for label, column in [
        ("Loan amount", columns.loan_amount),
        ("Interest rate", columns.interest_rate),
        ("Annual income", columns.income),
        ("Credit score", columns.credit_score),
    ]:
        if not column or column not in filtered.columns or filtered[column].dropna().empty:
            continue
        minimum = float(filtered[column].min(skipna=True))
        maximum = float(filtered[column].max(skipna=True))
        if minimum == maximum:
            continue
        selected_min, selected_max = st.sidebar.slider(label, minimum, maximum, (minimum, maximum))
        filtered = filtered[filtered[column].between(selected_min, selected_max, inclusive="both")]

    return filtered


def render_charts(df: pd.DataFrame, columns: DashboardColumns) -> None:
    """Render charts that are available for the resolved dataset columns."""

    chart_left, chart_right = st.columns(2)

    with chart_left:
        if columns.loan_amount:
            st.plotly_chart(
                px.histogram(df, x=columns.loan_amount, nbins=30, title="Loan amount distribution"),
                use_container_width=True,
            )
        if columns.status:
            st.plotly_chart(
                px.pie(df, names=columns.status, title="Loan status mix"),
                use_container_width=True,
            )

    with chart_right:
        if columns.interest_rate and columns.loan_amount:
            color = columns.grade or columns.status
            st.plotly_chart(
                px.scatter(
                    df,
                    x=columns.loan_amount,
                    y=columns.interest_rate,
                    color=color,
                    hover_data=[column for column in [columns.purpose, columns.credit_score] if column],
                    title="Loan amount vs interest rate",
                ),
                use_container_width=True,
            )
        if columns.purpose and columns.loan_amount:
            purpose_summary = (
                df.groupby(columns.purpose, dropna=False)[columns.loan_amount]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            st.plotly_chart(
                px.bar(purpose_summary, x=columns.purpose, y=columns.loan_amount, title="Top purposes by funded amount"),
                use_container_width=True,
            )

    if columns.income and columns.loan_amount:
        st.plotly_chart(
            px.scatter(
                df,
                x=columns.income,
                y=columns.loan_amount,
                color=columns.status or columns.grade,
                trendline="ols",
                title="Income vs loan amount",
            ),
            use_container_width=True,
        )


def load_dataset() -> pd.DataFrame:
    """Load a user-uploaded CSV file or fall back to sample data."""

    uploaded_file = st.sidebar.file_uploader("Upload a loan CSV file", type=["csv"])
    if uploaded_file is None:
        st.sidebar.info("Using sample loan data. Upload a CSV to explore your own dataset.")
        return create_sample_dataset()
    return pd.read_csv(uploaded_file)


def main() -> None:
    """Run the Streamlit loan dashboard."""

    st.set_page_config(page_title="Loan Data Dashboard", page_icon="💸", layout="wide")
    st.title("💸 Loan Data Dashboard")
    st.caption("Upload a CSV file to explore loan volumes, rates, status mix, borrower income, and risk segments.")

    raw_df = load_dataset()
    columns = resolve_columns(raw_df.columns)
    df = coerce_numeric(
        raw_df,
        [columns.loan_amount, columns.interest_rate, columns.income, columns.term, columns.credit_score],
    )
    filtered_df = render_sidebar_filters(df, columns)

    render_metric_cards(filtered_df, columns)
    st.divider()

    if filtered_df.empty:
        st.warning("No rows match the selected filters. Adjust the sidebar filters to continue.")
        return

    render_charts(filtered_df, columns)

    with st.expander("Preview filtered data", expanded=False):
        st.dataframe(filtered_df, use_container_width=True)

    with st.expander("Detected dashboard columns", expanded=False):
        st.json(columns.__dict__)


if __name__ == "__main__":
    main()
