import streamlit as st
import data_pipeline as dp

data = dp.run_pipeline()

st.title("Dashboard")

st.subheader("🎯 Target Rep Value")

st.dataframe(data["target"])
