import streamlit as st
import data_pipeline as dp

st.set_page_config(layout="wide")

st.title("📊 SALES KPI (CLEAN STEP 1)")

data = dp.load_data()

sales = dp.build_sales_pipeline(data["sales"])

st.header("Rep")
st.dataframe(sales["rep_value"], use_container_width=True)

st.header("Raw Data (بعد التنضيف)")
st.dataframe(sales["raw"], use_container_width=True)
