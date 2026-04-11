import streamlit as st
import data_pipeline as dp

st.set_page_config(layout="wide")
st.title("📊 Unified KPI Dashboard")

data = dp.load_data()

# =========================
# RUN PIPELINES
# =========================
sales = dp.build_sales_pipeline(data["sales"], data["mapping"], data["codes"])
overdue = dp.build_overdue(data["overdue"], data["codes"])
opening = dp.build_opening(data["opening"], data["codes"])

targets_rep = dp.build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
targets_manager = dp.build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])

# =========================
# 💰 SALES
# =========================
st.header("💰 Sales")
st.dataframe(sales["rep"])

# =========================
# ⚠️ OVERDUE
# =========================
st.header("⚠️ Overdue")
st.dataframe(overdue["rep"])

# =========================
# 🏦 OPENING
# =========================
st.header("🏦 Opening")
st.dataframe(opening["rep"])

# =========================
# 🎯 TARGETS
# =========================
st.header("🎯 Targets - Rep")
st.dataframe(targets_rep["value"])

st.header("🎯 Targets - Manager")
st.dataframe(targets_manager["value"])
