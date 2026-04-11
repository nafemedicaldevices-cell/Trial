import streamlit as st
import data_pipeline as dp

st.set_page_config(layout="wide")
st.title("📊 Final KPI Dashboard 🔥")

data = dp.load_data()

# =========================
# 🚀 RUN ALL PIPELINES
# =========================
target = dp.build_target_pipeline(
    data["target_rep"],
    "Rep Code",
    data["mapping"],
    data["codes"]
)

sales = dp.build_sales_pipeline(
    data["sales"],
    data["mapping"],
    data["codes"]
)

overdue = dp.build_overdue_pipeline(
    data["overdue"],
    data["codes"]
)

opening = dp.build_opening_pipeline(
    data["opening"],
    data["codes"]
)

# =========================
# 📊 DISPLAY
# =========================
st.header("🎯 TARGET")
st.dataframe(target["Rep Code"])

st.header("💰 SALES")
st.dataframe(sales["rep"])

st.header("⏳ OVERDUE")
st.dataframe(overdue["rep"])

st.header("🏦 OPENING")
st.dataframe(opening["rep"])
