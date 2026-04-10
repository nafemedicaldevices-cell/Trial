import streamlit as st
import data_pipeline as dp

st.set_page_config(layout="wide")
st.title("📊 Sales Performance Dashboard")

# =========================
# 📂 LOAD DATA
# =========================
data = dp.load_data()


# =========================
# 🎯 TARGET
# =========================
rep = dp.build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
manager = dp.build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])
area = dp.build_target_pipeline(data["target_area"], "Area Code", data["mapping"])
supervisor = dp.build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"])
evak = dp.build_target_pipeline(data["target_evak"], "Evak Code", data["mapping"])

st.header("🎯 TARGET KPI")
st.dataframe(rep["value_table"])
st.dataframe(manager["value_table"])
st.dataframe(area["value_table"])
st.dataframe(supervisor["value_table"])
st.dataframe(evak["value_table"])


# =========================
# 💰 SALES
# =========================
sales = dp.build_sales_pipeline(
    data["sales"],
    data["mapping"],
    data["codes"]
)

st.header("💰 SALES KPI")

st.subheader("Rep")
st.dataframe(sales["rep_value"])

st.subheader("Manager")
st.dataframe(sales["manager_value"])

st.subheader("Area")
st.dataframe(sales["area_value"])

st.subheader("Supervisor")
st.dataframe(sales["supervisor_value"])


st.header("📦 SALES PRODUCTS")

st.dataframe(sales["rep_products"])
st.dataframe(sales["manager_products"])
st.dataframe(sales["area_products"])
