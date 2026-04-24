import streamlit as st
import pandas as pd
import numpy as np
import os

from cleaning import (
    load_targets,
    load_haraka,
    load_overdue,
    load_client_haraka
)

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales + KPI Dashboard")

def load_file(path):
    if not os.path.exists(path):
        st.error(f"❌ File not found: {path}")
        st.stop()
    return pd.read_excel(path)

@st.cache_data
def load_data():
    sales = load_file("Sales.xlsx")
    mapping = load_file("Mapping.xlsx")
    codes = load_file("Code.xlsx")
    return sales, mapping, codes

sales, mapping, codes = load_data()

# =========================
# SALES CLEANING
# =========================
sales.columns = sales.columns.str.strip()

sales.columns = [
    'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
    'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
    'Sales Price','Invoice Discounts','Sales Value'
]

num_cols = [
    'Sales Unit Before Edit',
    'Returns Unit Before Edit',
    'Sales Price',
    'Invoice Discounts',
    'Sales Value'
]

sales[num_cols] = sales[num_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

# =========================
# MERGE
# =========================
sales = sales.merge(codes, on='Rep Code', how='left')

# =========================
# KPI
# =========================
sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']
sales['Returns Value'] = sales['Returns Unit Before Edit'] * sales['Sales Price']
sales['Net Sales'] = sales['Total Sales Value'] - sales['Returns Value']

# =========================
# LOAD MODULES
# =========================
targets = load_targets()
haraka = load_haraka()
overdue = load_overdue("Overdue.xlsx", codes)
client_haraka = load_client_haraka()

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Sales",
    "🎯 Targets",
    "📈 Harakah",
    "⏳ Overdue",
    "👤 Client Harakah"
])

with tab1:
    st.dataframe(sales, use_container_width=True)

with tab2:
    st.subheader("🎯 Targets by Level")

    for level, df in targets.items():
        st.markdown(f"### {level}")
        st.dataframe(df, use_container_width=True)

with tab3:
    st.dataframe(haraka, use_container_width=True)

with tab4:
    st.dataframe(overdue, use_container_width=True)
    st.metric("Overdue Total", overdue["Overdue"].sum())

with tab5:
    st.dataframe(client_haraka, use_container_width=True)
