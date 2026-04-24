import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales Dashboard")

# =========================
# 📥 Load Files مباشرة
# =========================
@st.cache_data
def load_data():
    sales = pd.read_excel("Sales.xlsx")
    mapping = pd.read_excel("Mapping.xlsx")
    codes = pd.read_excel("Codes.xlsx")
    return sales, mapping, codes

sales, mapping, codes = load_data()

# =========================
# 🧹 Clean Columns
# =========================
sales.columns = sales.columns.str.strip()

sales.columns = [
    'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
    'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
    'Sales Price','Invoice Discounts','Sales Value'
]

# =========================
# ➕ Ensure Columns
# =========================
for col in ['Old Product Code', 'Old Product Name']:
    if col not in sales.columns:
        sales[col] = None

# =========================
# 🧠 Product header handling
# =========================
mask = sales['Date'].astype(str).str.strip() == "كود الصنف"

sales.loc[mask, 'Old Product Code'] = sales.loc[mask, 'Warehouse Name']
sales.loc[mask, 'Old Product Name'] = sales.loc[mask, 'Client Code']

sales[['Old Product Code','Old Product Name']] = sales[['Old Product Code','Old Product Name']].ffill()

# =========================
# 🚫 Remove junk rows
# =========================
sales = sales[
    sales['Date'].notna() &
    (sales['Date'].astype(str).str.strip() != '') &
    (~sales['Date'].astype(str).str.contains('المندوب|كود الفرع|تاريخ|كود الصنف', na=False))
].copy()

# =========================
# 🔢 Numeric conversion
# =========================
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
# 🔗 Merge Mapping + Codes
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
# 📊 Calculations
# =========================
sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']
sales['Returns Value'] = sales['Returns Unit Before Edit'] * sales['Sales Price']
sales['Sales After Returns'] = sales['Total Sales Value'] - sales['Returns Value']

sales['Net Sales Unit Before Edit'] = (
    sales['Sales Unit Before Edit'] - sales['Returns Unit Before Edit']
)

sales['Net Sales Unit'] = sales['Net Sales Unit Before Edit'] * sales['Next Factor']

# =========================
# 📊 Output
# =========================
st.subheader("📋 Data Preview")
st.dataframe(sales, use_container_width=True)

st.subheader("📌 KPIs")

col1, col2, col3 = st.columns(3)

col1.metric("Total Sales", f"{sales['Total Sales Value'].sum():,.0f}")
col2.metric("Returns", f"{sales['Returns Value'].sum():,.0f}")
col3.metric("Net Sales", f"{sales['Sales After Returns'].sum():,.0f}")
