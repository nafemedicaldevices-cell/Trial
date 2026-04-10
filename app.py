import streamlit as st
import data_pipeline as dp

st.set_page_config(layout="wide")

st.title("📊 Sales Performance Dashboard")


# =========================
# 📂 LOAD DATA
# =========================
data = dp.load_data()


# =========================
# 🚀 BUILD KPI
# =========================
kpi = dp.build_kpi(data)


# =========================
# 👨‍💼 REP
# =========================
st.header("👨‍💼 Rep KPI")
st.dataframe(kpi["rep"], use_container_width=True)


# =========================
# 🏢 MANAGER
# =========================
st.header("🏢 Manager KPI")
st.dataframe(kpi["manager"], use_container_width=True)


# =========================
# 🌍 AREA
# =========================
st.header("🌍 Area KPI")
st.dataframe(kpi["area"], use_container_width=True)


# =========================
# 🧑‍💼 SUPERVISOR
# =========================
st.header("🧑‍💼 Supervisor KPI")
st.dataframe(kpi["supervisor"], use_container_width=True)


# =========================
# 🧬 EVAK
# =========================
st.header("🧬 Evak KPI")
st.dataframe(kpi["evak"], use_container_width=True)
