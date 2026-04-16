import streamlit as st
from pipelines import (
    load_data,
    build_target_pipeline,
    build_sales_pipeline,
    build_opening_pipeline,
    build_overdue_pipeline
)

st.set_page_config(layout="wide")
st.title("📊 Unified KPI System")

data = load_data()

# =========================
# 🎯 TARGET
# =========================
st.header("🎯 TARGET KPI")

target_rep = build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])

st.dataframe(target_rep["value_table"])
st.dataframe(target_rep["products_full"])


# =========================
# 💰 SALES
# =========================
st.header("💰 SALES KPI")

sales = build_sales_pipeline(data["sales"], data["codes"])

st.dataframe(sales["rep"])
st.dataframe(sales["manager"])
st.dataframe(sales["area"])
st.dataframe(sales["supervisor"])


# =========================
# 📦 OPENING
# =========================
st.header("📦 OPENING KPI")

opening = build_opening_pipeline(data["opening"], data["codes"])

st.dataframe(opening["rep"])
st.dataframe(opening["manager"])
st.dataframe(opening["area"])
st.dataframe(opening["supervisor"])


# =========================
# ⏳ OVERDUE
# =========================
st.header("⏳ OVERDUE KPI")

overdue = build_overdue_pipeline(data["overdue"], data["codes"])

st.dataframe(overdue["rep"])
st.dataframe(overdue["manager"])
st.dataframe(overdue["area"])
st.dataframe(overdue["supervisor"])
