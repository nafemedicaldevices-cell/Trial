import streamlit as st
import pandas as pd

st.title("Step 1 - Load Data Only")

# =========================
# 📥 LOAD FILES
# =========================
overdue = pd.read_excel("Overdue.xlsx")
codes = pd.read_excel("Code.xlsx")

# =========================
# SHOW RAW DATA
# =========================
st.subheader("📄 Overdue")
st.dataframe(overdue)

st.subheader("📄 Codes")
st.dataframe(codes)

# =========================
# DEBUG
# =========================
st.write("Overdue shape:", overdue.shape)
st.write("Codes shape:", codes.shape)
