import streamlit as st
import pandas as pd

st.title("Overdue Step 4")

overdue = pd.read_excel("Overdue.xlsx")

# =========================
# BASIC CLEANING
# =========================
overdue = overdue.iloc[:, :9].copy()

overdue.columns = [
    "Client Name",
    "Client Code",
    "15 Days",
    "30 Days",
    "60 Days",
    "90 Days",
    "120 Days",
    "More Than 120 Days",
    "Balance"
]

# =========================
# FIX DTYPE (IMPORTANT 🚨)
# =========================
overdue["Rep Code"] = pd.Series(dtype="object")
overdue["Old Rep Name"] = pd.Series(dtype="object")

# =========================
# SHOW RESULT
# =========================
st.subheader("📄 After Adding Empty Columns")
st.dataframe(overdue)
