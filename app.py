import streamlit as st
import pandas as pd

st.title("Step 7 - Overdue KPI")

overdue = pd.read_excel("Overdue.xlsx")

# =========================
# BASIC CLEANING
# =========================
overdue = overdue.iloc[:, :9].copy()

overdue.columns = [
    "Client Name", "Client Code", "15 Days", "30 Days", "60 Days", "90 Days",
    "120 Days", "More Than 120 Days", "Balance"
]

# =========================
# NUMERIC CONVERSION (minimal needed)
# =========================
num_cols = [
    "120 Days", "More Than 120 Days"
]

for col in num_cols:
    overdue[col] = pd.to_numeric(overdue[col], errors="coerce").fillna(0)

# =========================
# OVERDUE KPI
# =========================
overdue["Overdue"] = overdue["120 Days"] + overdue["More Than 120 Days"]

# =========================
# SHOW RESULT
# =========================
st.subheader("📄 After KPI Calculation")
st.dataframe(overdue)

st.write("Total Overdue:", overdue["Overdue"].sum())
