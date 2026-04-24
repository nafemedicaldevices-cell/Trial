import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 Sales Dashboard")

# =========================
# Upload Files
# =========================
sales_file = st.file_uploader("Upload Sales", type=["xlsx"])
mapping_file = st.file_uploader("Upload Mapping", type=["xlsx"])
codes_file = st.file_uploader("Upload Codes", type=["xlsx"])

# =========================import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 Sales Dashboard")

# =========================
# Load files مباشرة
# =========================
sales = pd.read_excel("sales.xlsx")
mapping = pd.read_excel("mapping.xlsx")
codes = pd.read_excel("codes.xlsx")

# =========================
# CLEAN FUNCTION
# =========================
def clean_sales(sales, mapping, codes):

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
    sales.loc[mask,'Old Product Code'] = sales.loc[mask,'Warehouse Name']
    sales.loc[mask,'Old Product Name'] = sales.loc[mask,'Client Code']

    sales[['Old Product Code','Old Product Name']] = sales[['Old Product Code','Old Product Name']].ffill()

    sales = sales[
        sales['Date'].notna() &
        (sales['Date'].astype(str).str.strip() != '') &
        (~sales['Date'].astype(str).str.contains('المندوب|كود الفرع|تاريخ|كود الصنف', na=False))
    ].copy()

    num_cols = [
        'Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]

    sales[num_cols] = sales[num_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    sales['Old Product Code'] = pd.to_numeric(sales['Old Product Code'], errors='coerce').astype('Int64')
    sales['Rep Code'] = pd.to_numeric(sales['Rep Code'], errors='coerce').astype('Int64')

    sales = sales.merge(mapping, on='Old Product Code', how='left')

    sales['Next Factor'] = sales.get('Next Factor', 1).fillna(1)

    codes['Rep Code'] = pd.to_numeric(codes['Rep Code'], errors='coerce').astype('Int64')
    sales = sales.merge(codes, on='Rep Code', how='left')

    sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']
    sales['Returns Value'] = sales['Returns Unit Before Edit'] * sales['Sales Price']
    sales['Sales After Returns'] = sales['Total Sales Value'] - sales['Returns Value']

    return sales


# =========================
# RUN
# =========================
sales = clean_sales(sales, mapping, codes)

st.dataframe(sales)
# CLEAN FUNCTION (داخل نفس الملف)
# =========================
def clean_sales(sales, mapping, codes):

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
    sales.loc[mask,'Old Product Code'] = sales.loc[mask,'Warehouse Name']
    sales.loc[mask,'Old Product Name'] = sales.loc[mask,'Client Code']

    sales[['Old Product Code','Old Product Name']] = sales[['Old Product Code','Old Product Name']].ffill()

    sales = sales[
        sales['Date'].notna() &
        (sales['Date'].astype(str).str.strip() != '') &
        (~sales['Date'].astype(str).str.contains('المندوب|كود الفرع|تاريخ|كود الصنف', na=False))
    ].copy()

    num_cols = [
        'Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]

    sales[num_cols] = sales[num_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    sales['Old Product Code'] = pd.to_numeric(sales['Old Product Code'], errors='coerce').astype('Int64')
    sales['Rep Code'] = pd.to_numeric(sales['Rep Code'], errors='coerce').astype('Int64')

    sales = sales.merge(
        mapping,
        on='Old Product Code',
        how='left'
    )

    sales['Next Factor'] = sales.get('Next Factor', 1).fillna(1)

    codes['Rep Code'] = pd.to_numeric(codes['Rep Code'], errors='coerce').astype('Int64')
    sales = sales.merge(codes, on='Rep Code', how='left')

    sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']
    sales['Returns Value'] = sales['Returns Unit Before Edit'] * sales['Sales Price']
    sales['Sales After Returns'] = sales['Total Sales Value'] - sales['Returns Value']
    sales['Net Sales Unit'] = (sales['Sales Unit Before Edit'] - sales['Returns Unit Before Edit']) * sales['Next Factor']

    return sales


# =========================
# RUN APP
# =========================
if sales_file and mapping_file and codes_file:

    sales = pd.read_excel(sales_file)
    mapping = pd.read_excel(mapping_file)
    codes = pd.read_excel(codes_file)

    # Clean
    sales = clean_sales(sales, mapping, codes)

    # =========================
    # VIEW 1 - FULL DATA
    # =========================
    st.subheader("📌 Full Data")
    st.dataframe(sales)

    # =========================
    # VIEW 2 - REP SUMMARY
    # =========================
    st.subheader("📊 Rep Summary")

    rep_summary = sales.groupby("Rep Code", as_index=False)[
        ["Total Sales Value","Returns Value","Sales After Returns"]
    ].sum()

    st.dataframe(rep_summary)

    # =========================
    # VIEW 3 - TOP PRODUCTS
    # =========================
    st.subheader("📦 Product Summary")

    product_summary = sales.groupby(
        ["Rep Code","Product Code","Product Name"], as_index=False
    )[["Total Sales Value"]].sum()

    st.dataframe(product_summary)

else:
    st.info("📂 ارفع كل الملفات عشان يبدأ العرض")
