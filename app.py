import streamlit as st
import data_pipeline as dp
from overdue_pipeline import build_overdue_pipeline


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
# 🚀 RUN OVERDUE PIPELINE
# =========================
overdue = build_overdue_pipeline(
    data["overdue"],
    data["codes"]
)


# =========================
# 📊 DISPLAY KPI
# =========================
st.header("💰 Overdue KPI")

st.subheader("👨‍💼 Rep")
st.dataframe(overdue["rep_value"], use_container_width=True)

st.subheader("🏢 Manager")
st.dataframe(overdue["manager_value"], use_container_width=True)

st.subheader("🌍 Area")
st.dataframe(overdue["area_value"], use_container_width=True)

st.subheader("🧑‍💼 Supervisor")
st.dataframe(overdue["supervisor_value"], use_container_width=True)


# =========================
# 📦 CLIENT BREAKDOWN
# =========================
st.header("📦 Client Level Overdue")

st.dataframe(overdue["rep_client"], use_container_width=True)
st.dataframe(overdue["manager_client"], use_container_width=True)
st.dataframe(overdue["area_client"], use_container_width=True)
st.dataframe(overdue["supervisor_client"], use_container_width=True)
