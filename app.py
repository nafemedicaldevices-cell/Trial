import streamlit as st
import pandas as pd

st.title("Overdue Step 3")

overdue = pd.read_excel("Overdue.xlsx")

# =========================
# BASIC CLEANING
# =========================
overdue = overdue.iloc[:, :9].copy()

# =========================
# RENAME COLUMNS
# =========================
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
# SHOW RESULT
# =========================
st.subheader("📄 After Renaming Columns")
st.dataframe(overdue)
