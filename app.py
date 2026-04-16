import pandas as pd
import numpy as np
import streamlit as st

# ==============================
# 🎯 PAGE CONFIG
# ==============================
st.set_page_config(page_title="Rep KPI Dashboard", layout="wide")
st.title("📊 Unified Rep Performance Dashboard")


# ==============================
# 🧹 CLEAN FUNCTIONS
# ==============================
def clean_numeric(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r'[^0-9.-]', '', regex=True),
                errors='coerce'
            ).fillna(0)
    return df


def unify_rep_code(df):
    if 'Rep Code' in df.columns:
        df['Rep Code'] = df['Rep Code'].astype(str).str.strip()
    return df


# ==============================
# 📂 LOAD DATA
# ==============================
opening_rep = pd.read_excel("Opening.xlsx")
target_rep_value_uptodate = pd.read_excel("Target.xlsx")
extra_discounts_rep = pd.read_excel("Extra Discounts.xlsx")
overdue_rep = pd.read_excel("Overdue.xlsx")
sales_rep_value = pd.read_excel("Sales.xlsx")


# ==============================
# 🧹 CLEAN DATA
# ==============================
financial_cols_opening = [
    'Opening Balance','Total Sales','Returns','Sales After Returns',
    'Sales Value Before Extra Discounts','Cash Collection','Collection Checks',
    'Total Collection','End Balance'
]

opening_rep = clean_numeric(opening_rep, financial_cols_opening)
target_rep_value_uptodate = clean_numeric(target_rep_value_uptodate, ['Target Value'])
extra_discounts_rep = clean_numeric(extra_discounts_rep, ['Extra Disocunts'])
overdue_rep = clean_numeric(overdue_rep, ['Overdue'])

opening_rep = unify_rep_code(opening_rep)
target_rep_value_uptodate = unify_rep_code(target_rep_value_uptodate)
extra_discounts_rep = unify_rep_code(extra_discounts_rep)
overdue_rep = unify_rep_code(overdue_rep)
sales_rep_value = unify_rep_code(sales_rep_value)


# ==============================
# 💸 SALES CLEAN
# ==============================
if 'Invoice Discounts' in sales_rep_value.columns:
    sales_rep_value['Invoice Discounts'] = pd.to_numeric(
        sales_rep_value['Invoice Discounts']
        .astype(str)
        .str.replace(r'[^0-9.-]', '', regex=True),
        errors='coerce'
    ).fillna(0)


# ==============================
# 🔗 MERGE DATA
# ==============================
rep_summary = opening_rep.merge(
    target_rep_value_uptodate[['Rep Code','Target Value']], on='Rep Code', how='left'
).merge(
    extra_discounts_rep[['Rep Code','Extra Disocunts']], on='Rep Code', how='left'
).merge(
    overdue_rep[['Rep Code','Overdue']], on='Rep Code', how='left'
).merge(
    sales_rep_value[['Rep Code','Invoice Discounts']], on='Rep Code', how='left'
)

rep_summary.fillna(0, inplace=True)


# ==============================
# 📊 CALCULATIONS
# ==============================
rep_summary['Total Discounts'] = (
    rep_summary['Extra Disocunts'] + rep_summary['Invoice Discounts']
)

rep_summary['Net Sales'] = (
    rep_summary['Sales After Returns'] - rep_summary['Total Discounts']
)

rep_summary['Achievement %'] = np.where(
    rep_summary['Target Value'] > 0,
    rep_summary['Net Sales'] / rep_summary['Target Value'],
    0
)


# ==============================
# 🎯 FILTERS
# ==============================
st.sidebar.header("🔎 Filters")

rep_list = rep_summary["Rep Code"].unique()
selected_rep = st.sidebar.selectbox("Select Rep", rep_list)

filtered_df = rep_summary[rep_summary["Rep Code"] == selected_rep]


# ==============================
# 📌 KPI CARDS
# ==============================
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Net Sales", f"{rep_summary['Net Sales'].sum():,.0f}")
col2.metric("🎯 Target", f"{rep_summary['Target Value'].sum():,.0f}")
col3.metric("💸 Discounts", f"{rep_summary['Total Discounts'].sum():,.0f}")
col4.metric("⏳ Overdue", f"{rep_summary['Overdue'].sum():,.0f}")


# ==============================
# 📋 DETAILS TABLE
# ==============================
st.subheader("📋 Rep Details")
st.dataframe(filtered_df, use_container_width=True)


# ==============================
# 📊 CHART 1 - Achievement (FIXED)
# ==============================
st.subheader("📊 Achievement % by Rep")

chart_data = rep_summary.copy()
chart_data = chart_data.set_index("Rep Code")[["Achievement %"]]

st.bar_chart(chart_data)


# ==============================
# 📊 CHART 2 - Net Sales vs Target
# ==============================
st.subheader("🎯 Net Sales vs Target")

chart2 = rep_summary.copy()
chart2 = chart2.set_index("Rep Code")[["Net Sales", "Target Value"]]

st.bar_chart(chart2)


# ==============================
# 📊 CHART 3 - Discounts
# ==============================
st.subheader("💸 Discounts Breakdown")

chart3 = rep_summary.copy()
chart3 = chart3.set_index("Rep Code")[[
    "Extra Disocunts",
    "Invoice Discounts",
    "Total Discounts"
]]

st.bar_chart(chart3)


# ==============================
# ✅ SUCCESS
# ==============================
st.success("✅ Dashboard running successfully بدون Plotly")
