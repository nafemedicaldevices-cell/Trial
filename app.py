import streamlit as st
import data_pipeline as dp

# =========================
# 🎨 CONFIG
# =========================
st.set_page_config(layout="wide")

st.title("📊 Sales Performance Dashboard")


# =========================
# 📥 LOAD DATA
# =========================
data = dp.load_data()


# =========================
# 🚀 SALES PIPELINE
# =========================
sales = dp.build_sales_pipeline(
    data["sales"],
    data["mapping"],
    data["codes"]
)


# =========================
# 📊 VALUE KPI
# =========================
st.header("💰 SALES VALUE KPI")

st.dataframe(sales["rep_value"], use_container_width=True)
st.dataframe(sales["manager_value"], use_container_width=True)
st.dataframe(sales["area_value"], use_container_width=True)
st.dataframe(sales["supervisor_value"], use_container_width=True)


# =========================
# 📦 PRODUCTS KPI
# =========================
st.header("📦 PRODUCTS KPI")

st.dataframe(sales["rep_products"], use_container_width=True)
st.dataframe(sales["manager_products"], use_container_width=True)
st.dataframe(sales["area_products"], use_container_width=True)
