import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Overdue KPI Dashboard")

# =========================
# 📥 LOAD DATA
# =========================
overdue = pd.read_excel("Overdue.xlsx")
codes = pd.read_excel("Code.xlsx")

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
# NUMERIC CLEANING
# =========================
num_cols = [
    "15 Days", "30 Days", "60 Days", "90 Days",
    "120 Days", "More Than 120 Days", "Balance"
]

for col in num_cols:
    overdue[col] = pd.to_numeric(overdue[col], errors="coerce").fillna(0)

# =========================
# REP EXTRACTION (لو موجود في نفس الشيت)
# =========================
overdue["Rep Code"] = pd.NA

mask = overdue["Client Name"].astype(str).str.strip().eq("كود المندوب")

overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"]

overdue["Rep Code"] = overdue["Rep Code"].ffill()

# =========================
# KPI
# =========================
overdue["Overdue"] = overdue["120 Days"] + overdue["More Than 120 Days"]

# =========================
# CLEAN CODES
# =========================
codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce").astype("Int64")

overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce").astype("Int64")

# =========================
# MERGE
# =========================
overdue = overdue.merge(codes, on="Rep Code", how="left")

# =========================
# =========================
# 📊 KPI GROUPS (HIERARCHY)
# =========================
# =========================

# 🔹 REP LEVEL
rep_value = overdue.groupby("Rep Code", as_index=False)["Overdue"].sum()
rep_client = overdue.groupby(["Rep Code", "Client Code"], as_index=False)["Overdue"].sum()

# 🔹 MANAGER LEVEL
manager_value = overdue.groupby("Manager Code", as_index=False)["Overdue"].sum()
manager_client = overdue.groupby(["Manager Code", "Client Code"], as_index=False)["Overdue"].sum()

# 🔹 AREA LEVEL
area_value = overdue.groupby("Area Code", as_index=False)["Overdue"].sum()
area_client = overdue.groupby(["Area Code", "Client Code"], as_index=False)["Overdue"].sum()

# 🔹 SUPERVISOR LEVEL
supervisor_value = overdue.groupby("Supervisor Code", as_index=False)["Overdue"].sum()
supervisor_client = overdue.groupby(["Supervisor Code", "Client Code"], as_index=False)["Overdue"].sum()

# =========================
# 📄 OUTPUTS
# =========================
st.subheader("📌 Main Data")
st.dataframe(overdue)

st.subheader("📊 Rep KPI")
st.dataframe(rep_value)

st.subheader("📊 Manager KPI")
st.dataframe(manager_value)

st.subheader("📊 Area KPI")
st.dataframe(area_value)

st.subheader("📊 Supervisor KPI")
st.dataframe(supervisor_value)

# =========================
# DEBUG
# =========================
st.write("Shape:", overdue.shape)
