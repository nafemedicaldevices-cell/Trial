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

# =========================
# 📁 FILE LOADER
# =========================
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
# 🧹 SALES CLEANING
# =========================
sales.columns = sales.columns.str.strip()

sales.columns = [
    'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
    'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
    'Sales Price','Invoice Discounts','Sales Value'
]

for col in ['Old Product Code', 'Old Product Name']:
    if col not in sales.columns:
        sales[col] = None

mask = sales['Date'].astype(str).str.strip() == "كود الصنف"

sales.loc[mask, 'Old Product Code'] = sales.loc[mask, 'Warehouse Name']
sales.loc[mask, 'Old Product Name'] = sales.loc[mask, 'Client Code']

sales[['Old Product Code','Old Product Name']] = sales[['Old Product Code','Old Product Name']].ffill()

sales = sales[
    sales['Date'].notna() &
    (sales['Date'].astype(str).str.strip() != '') &
    (~sales['Date'].astype(str).str.contains('المندوب|كود الفرع|تاريخ|كود الصنف', na=False))
].copy()

num_cols = [
    'Sales Unit Before Edit',
    'Returns Unit Before Edit',
    'Sales Price',
    'Invoice Discounts',
    'Sales Value'
]

sales[num_cols] = sales[num_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

sales['Old Product Code'] = pd.to_numeric(sales['Old Product Code'], errors='coerce').astype('Int64')
sales['Rep Code'] = pd.to_numeric(sales['Rep Code'], errors='coerce').astype('Int64')
codes['Rep Code'] = pd.to_numeric(codes['Rep Code'], errors='coerce').astype('Int64')

# =========================
# 🔗 MERGE
# =========================
sales = sales.merge(
    mapping[
        ['Old Product Code','4 Classification','Product Name',
         'Product Code','Category','Next Factor','2 Classification']
    ],
    on='Old Product Code',
    how='left'
)

sales['Next Factor'] = sales.get('Next Factor', 1).fillna(1)

sales = sales.merge(codes, on='Rep Code', how='left')

# =========================
# 📊 KPIs
# =========================
sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']
sales['Returns Value'] = sales['Returns Unit Before Edit'] * sales['Sales Price']
sales['Sales After Returns'] = sales['Total Sales Value'] - sales['Returns Value']

# =========================
# 📥 LOAD MODULES
# =========================
targets = load_targets()
haraka = load_haraka()
overdue = load_overdue("Overdue.xlsx", codes)
client_haraka = load_client_haraka()

# =========================
# 📌 TABS
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Sales",
    "🎯 Targets",
    "📈 Harakah",
    "⏳ Overdue",
    "👤 Client Harakah"
])

# =========================
# SALES
# =========================
with tab1:
    st.subheader("📊 Sales Data")
    st.dataframe(sales, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sales", f"{sales['Total Sales Value'].sum():,.0f}")
    c2.metric("Returns", f"{sales['Returns Value'].sum():,.0f}")
    c3.metric("Net Sales", f"{sales['Sales After Returns'].sum():,.0f}")

# =========================
# TARGETS
# =========================
with tab2:
    st.subheader("🎯 Targets")
    st.dataframe(targets, use_container_width=True)

# =========================
# HARKAH
# =========================
with tab3:
    st.subheader("📈 Harakah")
    st.dataframe(haraka, use_container_width=True)

# =========================
# OVERDUE
# =========================
with tab4:
    st.subheader("⏳ Overdue")
    st.dataframe(overdue, use_container_width=True)
    st.metric("Total Overdue", f"{overdue['Overdue'].sum():,.0f}")

# =========================
# CLIENT HARKAH
# =========================
with tab5:
    st.subheader("👤 Client Harakah")

    if client_haraka.empty:
        st.warning("No data found")
    else:
        st.dataframe(client_haraka, use_container_width=True)

        c1, c2, c3 = st.columns(3)

        c1.metric("Sales", f"{client_haraka['Sales Value'].sum():,.0f}")
        c2.metric("Returns", f"{client_haraka['Returns Value'].sum():,.0f}")
        c3.metric(
            "Net",
            f"{client_haraka['Sales Value'].sum() - client_haraka['Returns Value'].sum():,.0f}"
        )
