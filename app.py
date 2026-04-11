import streamlit as st
import data_pipeline as dp

st.set_page_config(layout="wide")
st.title("📊 Full KPI Dashboard")

# LOAD
data = dp.load_data()

# =========================
# SALES
# =========================
st.header("💰 Sales KPI")

rep_sales, manager_sales = dp.build_sales_pipeline(
    data["sales"],
    data["mapping"],
    data["codes"]
)

st.subheader("Rep")
st.dataframe(rep_sales)

st.subheader("Manager")
st.dataframe(manager_sales)

# =========================
# OVERDUE
# =========================
st.header("⏳ Overdue KPI")

rep_overdue, manager_overdue = dp.build_overdue_pipeline(
    data["overdue"],
    data["codes"]
)

st.subheader("Rep")
st.dataframe(rep_overdue)

st.subheader("Manager")
st.dataframe(manager_overdue)

# =========================
# OPENING
# =========================
st.header("🏦 Opening KPI")

rep_open, manager_open = dp.build_opening_pipeline(
    data["opening"],
    data["codes"]
)

st.subheader("Rep")
st.dataframe(rep_open)

st.subheader("Manager")
st.dataframe(manager_open)
