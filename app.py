import streamlit as st
import pandas as pd

from cleaning import load_targets, load_haraka, load_sales

st.set_page_config(layout="wide")

st.title("📊 KPI Dashboard")

# =========================
# LOAD DATA
# =========================
targets = load_targets()
haraka = load_haraka()

# ⚠️ لو عندك ملف sales
# sales_df = pd.read_excel("Sales.xlsx")
# sales = load_sales(sales_df)

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["Targets", "Harakah", "Sales"])

with tab1:
    st.subheader("Targets")
    st.dataframe(targets, use_container_width=True)

with tab2:
    st.subheader("Harakah")
    st.dataframe(haraka, use_container_width=True)

with tab3:
    st.subheader("Sales")
    st.warning("اربط ملف Sales هنا في الكود")
