import streamlit as st
import data_pipeline as dp

st.set_page_config(layout="wide")
st.title("📊 Sales & Target Unified Dashboard")

data = dp.load_data()

kpi = dp.build_kpi(data)


# =========================
# 🎯 REP
# =========================
st.header("👨‍💼 REP KPI")

st.dataframe(kpi["rep"])


# =========================
# 🏢 MANAGER
# =========================
st.header("🏢 MANAGER KPI")

st.dataframe(kpi["manager"])


# =========================
# 🌍 AREA
# =========================
st.header("🌍 AREA KPI")

st.dataframe(kpi["area"])


# =========================
# 🧑‍💼 SUPERVISOR
# =========================
st.header("🧑‍💼 SUPERVISOR KPI")

st.dataframe(kpi["supervisor"])


# =========================
# 🧬 EVAK
# =========================
st.header("🧬 EVAK KPI")

st.dataframe(kpi["evak"])
