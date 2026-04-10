import streamlit as st
import pandas as pd

st.title("Overdue Step 2")

overdue = pd.read_excel("Overdue.xlsx")

# =========================
# BASIC CLEANING (Step 2)
# =========================
overdue = overdue.iloc[:, :9].copy()

st.subheader("📄 After Selecting 9 Columns")
st.dataframe(overdue)
