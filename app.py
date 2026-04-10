import streamlit as st
import pandas as pd

st.title("Step 8 - Merge Codes")

overdue = pd.read_excel("Overdue.xlsx")
codes = pd.read_excel("Code.xlsx")

# =========================
# BASIC CLEANING
# =========================
overdue = overdue.iloc[:, :9].copy()

overdue.columns = [
    "Client Name", "Client Code", "15 Days", "30 Days", "60 Days", "90 Days",
    "120 Days", "More Than 120 Days", "Balance"
]

# =========================
# KPI (needed before merge)
# =========================
overdue["120 Days"] = pd.to_numeric(overdue["120 Days"], errors="coerce").fillna(0)
overdue["More Than 120 Days"] = pd.to_numeric(overdue["More Than 120 Days"], errors="coerce").fillna(0)

overdue["Overdue"] = overdue["120 Days"] + overdue["More Than 120 Days"]

# =========================
# CLEAN CODES
# =========================
codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce").astype("Int64")

# =========================
# MERGE
# =========================
overdue = overdue.merge(codes, on="Rep Code", how="left")

# =========================
# SHOW RESULT
# =========================
st.subheader("📄 After Merge")
st.dataframe(overdue)

st.write("Shape:", overdue.shape)
