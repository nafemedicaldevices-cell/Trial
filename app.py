import streamlit as st
import data_pipeline as dp

st.set_page_config(layout="wide")
st.title("📊 CLEAN DATA CHECK DASHBOARD")


# =========================
# LOAD
# =========================
data = dp.load_data()

sales = dp.clean_sales(data["sales"])

rep_target = dp.clean_target(data["target_rep"], "Rep Code")
manager_target = dp.clean_target(data["target_manager"], "Manager Code")
area_target = dp.clean_target(data["target_area"], "Area Code")
supervisor_target = dp.clean_target(data["target_supervisor"], "Supervisor Code")


# =========================
# SHOW ONLY (NO MERGE)
# =========================
st.header("📦 SALES CLEAN DATA")
st.dataframe(sales, use_container_width=True)

st.header("🎯 REP TARGET CLEAN")
st.dataframe(rep_target, use_container_width=True)

st.header("🎯 MANAGER TARGET CLEAN")
st.dataframe(manager_target, use_container_width=True)

st.header("🎯 AREA TARGET CLEAN")
st.dataframe(area_target, use_container_width=True)

st.header("🎯 SUPERVISOR TARGET CLEAN")
st.dataframe(supervisor_target, use_container_width=True)
