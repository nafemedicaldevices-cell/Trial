import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales Dashboard")

# =========================
# 📂 LOAD FILES
# =========================
@st.cache_data
def load_data():
    sales = pd.read_excel("Sales.xlsx")
    mapping = pd.read_excel("Mapping.xlsx")
    codes = pd.read_excel("Code.xlsx")
    return sales, mapping, codes

sales, mapping, codes = load_data()

# =========================
# 🧹 CLEAN SALES
# =========================
sales.columns = sales.columns.str.strip()

sales.columns = [
    'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
    'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
    'Sales Price','Invoice Discounts','Sales Value'
]

for col in ['Old Product Code','Old Product Name']:
    if col not in sales.columns:
        sales[col] = None

mask = sales['Date'].astype(str).str.strip() == "كود الصنف"
sales.loc[mask,'Old Product Code'] = sales.loc[mask,'Warehouse Name']
sales.loc[mask,'Old Product Name'] = sales.loc[mask,'Client Code']
sales[['Old Product Code','Old Product Name']] = sales[['Old Product Code','Old Product Name']].ffill()

sales = sales[
    sales['Date'].notna() &
    (sales['Date'].astype(str).str.strip() != '') &
    (~sales['Date'].astype(str).str.contains('المندوب|كود الفرع|تاريخ|كود الصنف', na=False))
].copy()

# =========================
# 🔢 NUMERIC
# =========================
num_cols = ['Sales Unit Before Edit','Returns Unit Before Edit','Sales Price','Invoice Discounts','Sales Value']
sales[num_cols] = sales[num_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

sales['Old Product Code'] = pd.to_numeric(sales['Old Product Code'], errors='coerce').astype('Int64')
sales['Rep Code'] = pd.to_numeric(sales['Rep Code'], errors='coerce').astype('Int64')

# =========================
# 🔗 MERGE
# =========================
sales = sales.merge(
    mapping[['Old Product Code','4 Classification','Product Name','Product Code','Category','Next Factor','2 Classification']],
    on='Old Product Code',
    how='left'
)

sales['Next Factor'] = sales.get('Next Factor', 1).fillna(1)

codes['Rep Code'] = pd.to_numeric(codes['Rep Code'], errors='coerce').astype('Int64')
sales = sales.merge(codes, on='Rep Code', how='left')

# =========================
# ➕ CALC
# =========================
sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']
sales['Returns Value'] = sales['Returns Unit Before Edit'] * sales['Sales Price']
sales['Sales After Returns'] = sales['Total Sales Value'] - sales['Returns Value']
sales['Net Sales Unit Before Edit'] = sales['Sales Unit Before Edit'] - sales['Returns Unit Before Edit']
sales['Net Sales Unit'] = sales['Net Sales Unit Before Edit'] * sales['Next Factor']

# =========================
# 📊 GROUP FUNCTION
# =========================
def group(df, group_cols, sum_cols):
    return df.groupby(group_cols, as_index=False)[sum_cols].sum()

# =========================
# 📌 RESULTS
# =========================
sales_rep_value = group(
    sales,
    ['Rep Code'],
    ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
)

sales_manager_value = group(
    sales,
    ['Manager Code'],
    ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
)

sales_area_value = group(
    sales,
    ['Area Code'],
    ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
)

# =========================
# 📺 STREAMLIT UI
# =========================
tab1, tab2, tab3 = st.tabs(["Rep", "Manager", "Area"])

with tab1:
    st.subheader("👤 Rep KPI")
    st.dataframe(sales_rep_value)

with tab2:
    st.subheader("👔 Manager KPI")
    st.dataframe(sales_manager_value)

with tab3:
    st.subheader("🌍 Area KPI")
    st.dataframe(sales_area_value)
