import streamlit as st
import data_pipeline as dp

data = dp.run_pipeline()

st.title("📊 KPI Dashboard")

st.subheader("🎯 Sales vs Target")

st.dataframe(data["kpi"])
