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
# REP EXTRACTION
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
# FUNCTION
# =========================
def build_level(df, level_code):
    # DETAILS
    details = df[[level_code, "Client Code", "Overdue"]].copy()
    
    # SUMMARY
    summary = (
        df.groupby(level_code)["Overdue"]
        .sum()
        .reset_index()
    )
    
    return summary, details

# =========================
# LEVELS
# =========================
rep_summary, rep_details = build_level(overdue, "Rep Code")
manager_summary, manager_details = build_level(overdue, "Manager Code")
area_summary, area_details = build_level(overdue, "Area Code")
supervisor_summary, supervisor_details = build_level(overdue, "Supervisor Code")

# =========================
# UI
# =========================

# REP
st.subheader("📌 Rep Summary")
st.dataframe(rep_summary)

st.subheader("📌 Rep Details")
st.dataframe(rep_details)

# MANAGER
st.subheader("📌 Manager Summary")
st.dataframe(manager_summary)

st.subheader("📌 Manager Details")
st.dataframe(manager_details)

# AREA
st.subheader("📌 Area Summary")
st.dataframe(area_summary)

st.subheader("📌 Area Details")
st.dataframe(area_details)

# SUPERVISOR
st.subheader("📌 Supervisor Summary")
st.dataframe(supervisor_summary)

st.subheader("📌 Supervisor Details")
st.dataframe(supervisor_details)
