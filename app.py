import streamlit as st
import pandas as pd

from cleaning_all import load_targets, load_haraka, load_sales

st.set_page_config(layout="wide")

st.title("📊 KPI Dashboard")

# =========================
# LOAD DATA
# =========================
targets = load_targets()
haraka = load_haraka()

# ⚠️ لازم يكون عندك sales DataFrame جاهز
# مثال:
# sales = pd.read_excel("Sales.xlsx")
# sales = load_sales(sales)

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["Targets", "Harakah", "Sales"])

# =========================
# TARGETS
# =========================
with tab1:
    st.subheader("Targets Data")
    st.dataframe(targets, use_container_width=True)

# =========================
# HARKA
# =========================
with tab2:
    st.subheader("Harakah Data")
    st.dataframe(haraka, use_container_width=True)

# =========================
# SALES
# =========================
with tab3:
    st.subheader("Sales Data")
    
    # ⚠️ مهم: لازم تسلّم sales هنا
    # st.dataframe(sales, use_container_width=True)
    st.warning("⚠️ اربط ملف Sales هنا في الكود")
