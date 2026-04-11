import streamlit as st
import pipelines_test as p

data = p.load_data()

target = p.build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
sales = p.build_sales_pipeline(data["sales"], data["mapping"], data["codes"])

st.title("Test Dashboard")

st.subheader("Target")
st.dataframe(target["value_table"])

st.subheader("Sales")
st.dataframe(sales["rep_value"])
