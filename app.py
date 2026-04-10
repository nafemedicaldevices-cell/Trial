import streamlit as st
from data_pipeline import run_pipeline

data = run_pipeline()

st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("📊 Sales Performance Dashboard")

# =========================
# SALES
# =========================
st.subheader("Sales Data")
st.dataframe(data["sales"].head())

# =========================
# OVERDUE
# =========================
st.subheader("Overdue Data")
st.dataframe(data["overdue"].head())

# =========================
# OPENING DETAIL
# =========================
st.subheader("Opening Detail")
st.dataframe(data["opening_detail"].head())
