# Loan Data Analysis Dashboard

An interactive Python dashboard for exploring loan datasets. The app is built with Streamlit, pandas, and Plotly so you can upload a CSV file and quickly inspect loan volumes, interest rates, approval/status mix, borrower income, and risk segments.

## Features

- Upload a CSV file from the sidebar or use the built-in sample loan dataset.
- Automatically detects common loan columns such as `loan_amount`, `interest_rate`, `annual_income`, `loan_status`, `grade`, `purpose`, `term`, and `credit_score`.
- Filter by categorical fields and numeric ranges.
- View KPI cards for record count, total loan amount, average loan amount, and average interest rate.
- Explore interactive charts for distributions, status mix, purpose totals, and borrower relationships.
- Preview filtered data and inspect the detected column mapping.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The dashboard opens in your browser. Upload your loan CSV from the left sidebar, or keep the sample data to preview the dashboard.

## CSV column guidance

The dashboard works best when your CSV includes some of these common fields:

| Concept | Example column names |
| --- | --- |
| Loan amount | `loan_amount`, `loan_amnt`, `amount`, `principal` |
| Interest rate | `interest_rate`, `int_rate`, `rate` |
| Income | `annual_income`, `annual_inc`, `income`, `applicantincome` |
| Status | `loan_status`, `status`, `approval_status`, `approved` |
| Risk grade | `grade`, `risk_grade`, `loan_grade` |
| Purpose | `purpose`, `loan_purpose`, `reason` |
| Term | `term`, `loan_term`, `duration` |
| Credit score | `credit_score`, `fico_score`, `cibil_score` |

If your dataset uses different names, rename those CSV columns to one of the aliases above for richer visuals.
