import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("📊 Sales Dashboard")

# =========================
# 📥 Upload Files
# =========================
sales_file = st.file_uploader("Upload Sales File", type=["xlsx"])
mapping_file = st.file_uploader("Upload Mapping File", type=["xlsx"])
codes_file = st.file_uploader("Upload Codes File", type=["xlsx"])


if sales_file and mapping_file and codes_file:

    # =========================
    # 📥 Load Data
    # =========================
    sales = pd.read_excel(sales_file)
    mapping = pd.read_excel(mapping_file)
    codes = pd.read_excel(codes_file)

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
    # ➕ Ensure required columns
    # =========================
    for col in ['Old Product Code', 'Old Product Name']:
        if col not in sales.columns:
            sales[col] = None

    # =========================
    # 🧠 Handle product header rows
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
    # 🔢 Convert numeric columns
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
    codes['Rep Code'] = pd.to_numeric(codes['Rep Code'], errors='coerce').astype('Int64')
    sales['Rep Code'] = pd.to_numeric(sales['Rep Code'], errors='coerce').astype('Int64')

    # =========================
    # 🔗 Merge Mapping
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

    # =========================
    # 🔗 Merge Codes
    # =========================
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
    # 📊 Show Data
    # =========================
    st.subheader("📋 Processed Data")
    st.dataframe(sales, use_container_width=True)

    # =========================
    # 📊 Summary KPIs
    # =========================
    st.subheader("📌 KPIs")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Sales", f"{sales['Total Sales Value'].sum():,.0f}")
    col2.metric("Returns", f"{sales['Returns Value'].sum():,.0f}")
    col3.metric("Net Sales", f"{sales['Sales After Returns'].sum():,.0f}")

else:
    st.info("⬆️ Please upload all required files to start processing.")
