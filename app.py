import streamlit as st
import data_pipeline as dp

st.set_page_config(layout="wide")

st.title("📊 Sales Performance Dashboard")


# =========================
# 📂 LOAD DATA
# =========================
data = dp.load_data()


# =========================
# 💰 SALES KPI
# =========================
st.header("💰 SALES KPI")

sales = dp.build_sales_pipeline(data["sales"])

st.subheader("Rep Sales")
st.dataframe(sales["rep_value"], use_container_width=True)

st.subheader("Manager Sales")
st.dataframe(sales["manager_value"], use_container_width=True)

st.subheader("Area Sales")
st.dataframe(sales["area_value"], use_container_width=True)

st.subheader("Supervisor Sales")
st.dataframe(sales["supervisor_value"], use_container_width=True)


# =========================
# 🎯 TARGET KPI
# =========================
st.header("🎯 TARGET KPI")

rep_target = dp.build_target(data["target_rep"], "Rep Code", data["mapping"])
manager_target = dp.build_target(data["target_manager"], "Manager Code", data["mapping"])
area_target = dp.build_target(data["target_area"], "Area Code", data["mapping"])
supervisor_target = dp.build_target(data["target_supervisor"], "Supervisor Code", data["mapping"])

st.dataframe(rep_target)
st.dataframe(manager_target)
st.dataframe(area_target)
st.dataframe(supervisor_target)
