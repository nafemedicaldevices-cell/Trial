import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Overdue KPI - Clean Levels")

# =========================
# LOAD DATA
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
# NUMERIC
# =========================
num_cols = [
    "15 Days","30 Days","60 Days","90 Days",
    "120 Days","More Than 120 Days","Balance"
]

for col in num_cols:
    overdue[col] = pd.to_numeric(overdue[col], errors="coerce").fillna(0)

# =========================
# KPI
# =========================
overdue["Overdue"] = overdue["120 Days"] + overdue["More Than 120 Days"]

# =========================
# REP EXTRACTION (optional)
# =========================
overdue["Rep Code"] = pd.NA

mask = overdue["Client Name"].astype(str).str.strip().eq("كود المندوب")
overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"]
overdue["Rep Code"] = overdue["Rep Code"].ffill()

# =========================
# CLEAN CODES
# =========================
codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce").astype("Int64")
overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce").astype("Int64")

overdue = overdue.merge(codes, on="Rep Code", how="left")

# =========================
# 🔥 FUNCTION: STANDARD LEVEL BUILDER
# =========================
def build_level(df, level_code):
    return df[[level_code, "Client Code", "Overdue"]].copy()

# =========================
# 🔥 LEVELS
# =========================

rep_kpi = build_level(overdue, "Rep Code")
manager_kpi = build_level(overdue, "Manager Code")
area_kpi = build_level(overdue, "Area Code")
supervisor_kpi = build_level(overdue, "Supervisor Code")

# =========================
# OUTPUT
# =========================
st.subheader("📌 Rep Level")
st.dataframe(rep_kpi)

st.subheader("📌 Manager Level")
st.dataframe(manager_kpi)

st.subheader("📌 Area Level")
st.dataframe(area_kpi)

st.subheader("📌 Supervisor Level")
st.dataframe(supervisor_kpi)
