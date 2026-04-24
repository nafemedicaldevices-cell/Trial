import streamlit as st
import pandas as pd

from clean_sales import clean_sales

st.set_page_config(layout="wide")
st.title("📊 Sales Dashboard")

# =========================
# Upload files
# =========================
sales_file = st.file_uploader("Upload Sales", type=["xlsx"])
mapping_file = st.file_uploader("Upload Mapping", type=["xlsx"])
codes_file = st.file_uploader("Upload Codes", type=["xlsx"])

if sales_file and mapping_file and codes_file:

    sales = pd.read_excel(sales_file)
    mapping = pd.read_excel(mapping_file)
    codes = pd.read_excel(codes_file)

    # =========================
    # Clean
    # =========================
    sales = clean_sales(sales, mapping, codes)

    # =========================
    # Aggregations
    # =========================
    st.subheader("📌 Rep Summary")

    rep_summary = sales.groupby("Rep Code", as_index=False)[
        ["Total Sales Value","Returns Value","Sales After Returns","Invoice Discounts"]
    ].sum()

    st.dataframe(rep_summary)

    st.subheader("📌 Top Products")

    product_summary = sales.groupby(
        ["Rep Code","Product Code","Product Name"], as_index=False
    )[["Sales Value","Net Sales Unit"]].sum()

    st.dataframe(product_summary)

else:
    st.warning("Please upload all required files")
