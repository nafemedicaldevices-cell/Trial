import streamlit as st
import pandas as pd

from cleaning import load_targets, load_haraka
from cleaning_sales import process_sales

st.set_page_config(layout="wide")

st.title("📊 KPI Dashboard")

# =========================
# LOAD DATA
# =========================
targets = load_targets()
haraka = load_haraka()

sales_df = pd.read_excel("Sales.xlsx")
mapping = pd.read_excel("mapping.xlsx")
codes = pd.read_excel("codes.xlsx")

sales = process_sales(sales_df, mapping, codes)

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["Targets", "Harakah", "Sales"])

# =========================
# TARGETS
# =========================
with tab1:
    for lvl in ["Rep","Manager","Area","Supervisor","Evak"]:
        st.markdown(f"### 📌 {lvl}")
        st.dataframe(targets[targets["Level"] == lvl], use_container_width=True)

# =========================
# HARKA
# =========================
with tab2:
    st.dataframe(haraka, use_container_width=True)

# =========================
# SALES
# =========================
with tab3:

    st.subheader("Rep Value")
    st.dataframe(sales["rep_value"], use_container_width=True)

    st.subheader("Rep Client")
    st.dataframe(sales["rep_client"], use_container_width=True)

    st.subheader("Rep Products")
    st.dataframe(sales["rep_products"], use_container_width=True)
