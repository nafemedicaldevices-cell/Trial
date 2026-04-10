import streamlit as st
import data_pipeline as dp

st.set_page_config(layout="wide")

st.title("💰 SALES KPI FIXED")

data = dp.load_data()

sales = dp.build_sales_pipeline(
    data["sales"],
    data["mapping"],
    data["codes"]
)

st.header("Rep")
st.dataframe(sales["rep_value"], use_container_width=True)

st.header("Manager")
st.dataframe(sales["manager_value"], use_container_width=True)

st.header("Area")
st.dataframe(sales["area_value"], use_container_width=True)

st.header("Supervisor")
st.dataframe(sales["supervisor_value"], use_container_width=True)

st.header("Products")
st.dataframe(sales["rep_products"], use_container_width=True)
