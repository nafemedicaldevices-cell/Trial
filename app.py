import streamlit as st
import data_pipeline as dp

st.set_page_config(layout="wide")
st.title("💰 SALES KPI TEST")

data = dp.load_data()

sales = dp.build_sales_pipeline(data["sales"])


# =========================
# 👨‍💼 REP
# =========================
st.header("Rep Sales")
st.dataframe(sales["rep_value"], use_container_width=True)


# =========================
# 🏢 MANAGER
# =========================
st.header("Manager Sales")
st.dataframe(sales["manager_value"], use_container_width=True)


# =========================
# 🌍 AREA
# =========================
st.header("Area Sales")
st.dataframe(sales["area_value"], use_container_width=True)


# =========================
# 🧑‍💼 SUPERVISOR
# =========================
st.header("Supervisor Sales")
st.dataframe(sales["supervisor_value"], use_container_width=True)
