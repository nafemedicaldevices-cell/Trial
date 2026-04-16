import os
import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(page_title="Rep Dashboard", layout="wide")
st.title("📊 Unified Rep Performance Dashboard")

BASE_DIR = os.path.dirname(__file__)


# ==============================
# 📂 LOAD FILES (FIXED)
# ==============================
target_rep_value_uptodate = pd.read_excel(os.path.join(BASE_DIR, "Target Rep.xlsx"))
target_manager_value_uptodate = pd.read_excel(os.path.join(BASE_DIR, "Target Manager.xlsx"))
target_area_value_uptodate = pd.read_excel(os.path.join(BASE_DIR, "Target Area.xlsx"))
target_supervisor_value_uptodate = pd.read_excel(os.path.join(BASE_DIR, "Target Supervisor.xlsx"))

opening_rep = pd.read_excel(os.path.join(BASE_DIR, "Opening.xlsx"))
extra_discounts_rep = pd.read_excel(os.path.join(BASE_DIR, "Extra Discounts.xlsx"))
overdue_rep = pd.read_excel(os.path.join(BASE_DIR, "Overdue.xlsx"))
sales_rep_value = pd.read_excel(os.path.join(BASE_DIR, "Sales.xlsx"))


# ==============================
# 🧹 CLEAN FUNCTION
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
# 🧹 CLEAN DATA
# ==============================
financial_cols_opening = [
    'Opening Balance','Total Sales','Returns','Sales After Returns',
    'Sales Value Before Extra Discounts','Cash Collection','Collection Checks',
    'Total Collection','End Balance'
]

opening_rep = clean_numeric(opening_rep, financial_cols_opening)

target_rep_value_uptodate = clean_numeric(target_rep_value_uptodate, ['Target Value'])
target_manager_value_uptodate = clean_numeric(target_manager_value_uptodate, ['Target Value'])
target_area_value_uptodate = clean_numeric(target_area_value_uptodate, ['Target Value'])
target_supervisor_value_uptodate = clean_numeric(target_supervisor_value_uptodate, ['Target Value'])

extra_discounts_rep = clean_numeric(extra_discounts_rep, ['Extra Disocunts'])
overdue_rep = clean_numeric(overdue_rep, ['Overdue'])

opening_rep = unify_rep_code(opening_rep)
target_rep_value_uptodate = unify_rep_code(target_rep_value_uptodate)
target_manager_value_uptodate = unify_rep_code(target_manager_value_uptodate)
target_area_value_uptodate = unify_rep_code(target_area_value_uptodate)
target_supervisor_value_uptodate = unify_rep_code(target_supervisor_value_uptodate)
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
# 🔗 MERGE (REP LEVEL)
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
# 🎯 DASHBOARD
# ==============================
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Net Sales", f"{rep_summary['Net Sales'].sum():,.0f}")
col2.metric("🎯 Target", f"{rep_summary['Target Value'].sum():,.0f}")
col3.metric("💸 Discounts", f"{rep_summary['Total Discounts'].sum():,.0f}")
col4.metric("⏳ Overdue", f"{rep_summary['Overdue'].sum():,.0f}")


# ==============================
# 📋 TABLE
# ==============================
st.subheader("📋 Rep Details")
st.dataframe(rep_summary, use_container_width=True)


# ==============================
# 📊 CHART (NO PLOTLY)
# ==============================
st.subheader("📊 Achievement %")

st.bar_chart(
    rep_summary.set_index("Rep Code")[["Achievement %"]]
)
