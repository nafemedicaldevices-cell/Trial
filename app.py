import streamlit as st
import pandas as pd

st.title("Overdue KPI Engine")

# =========================
# LOAD (assumed already cleaned before)
# =========================
overdue = pd.read_excel("Overdue.xlsx")
codes = pd.read_excel("Code.xlsx")

# =========================
# BASIC CLEANING (minimal example)
# =========================
overdue = overdue.iloc[:, :9].copy()

overdue.columns = [
    "Client Name", "Client Code", "15 Days", "30 Days", "60 Days", "90 Days",
    "120 Days", "More Than 120 Days", "Balance"
]

# =========================
# KPI
# =========================
overdue["120 Days"] = pd.to_numeric(overdue["120 Days"], errors="coerce").fillna(0)
overdue["More Than 120 Days"] = pd.to_numeric(overdue["More Than 120 Days"], errors="coerce").fillna(0)

overdue["Overdue"] = overdue["120 Days"] + overdue["More Than 120 Days"]

# =========================
# MERGE CODES
# =========================
codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce").astype("Int64")

if "Rep Code" in overdue.columns:
    overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce").astype("Int64")
    overdue = overdue.merge(codes, on="Rep Code", how="left")

# =========================
# SAFE GROUP ENGINE
# =========================
def safe_group(df, group_cols, sum_cols):
    group_cols = [c for c in group_cols if c in df.columns]
    sum_cols = [c for c in sum_cols if c in df.columns]

    if not group_cols or not sum_cols:
        return pd.DataFrame()

    return df.groupby(group_cols, as_index=False)[sum_cols].sum()

# =========================
# GROUP CONFIG
# =========================
OVERDUE_GROUPS = {
    "rep_value": {
        "group": ["Rep Code"],
        "sum": ["Overdue"]
    },
    "manager_value": {
        "group": ["Manager Code"],
        "sum": ["Overdue"]
    },
    "area_value": {
        "group": ["Area Code"],
        "sum": ["Overdue"]
    },
    "supervisor_value": {
        "group": ["Supervisor Code"],
        "sum": ["Overdue"]
    },
    "rep_client": {
        "group": ["Rep Code", "Client Code"],
        "sum": ["Overdue"]
    },
    "manager_client": {
        "group": ["Manager Code", "Client Code"],
        "sum": ["Overdue"]
    },
    "area_client": {
        "group": ["Area Code", "Client Code"],
        "sum": ["Overdue"]
    },
    "supervisor_client": {
        "group": ["Supervisor Code", "Client Code"],
        "sum": ["Overdue"]
    }
}

# =========================
# RUN GROUPS SAFELY
# =========================
overdue_results = {}

for name, cfg in OVERDUE_GROUPS.items():
    overdue_results[name] = safe_group(overdue, cfg["group"], cfg["sum"])

# =========================
# OUTPUT SAFE ACCESS
# =========================
for k, v in overdue_results.items():
    st.subheader(k)
    st.dataframe(v)
