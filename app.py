import streamlit as st
import pandas as pd

st.set_page_config(page_title="Overdue Dashboard", layout="wide")

st.title("📊 Overdue Dashboard")

# =========================
# 📥 LOAD DATA
# =========================
overdue = pd.read_excel("Overdue.xlsx")
codes = pd.read_excel("Code.xlsx")

# =========================
# BASIC CLEANING (OVERDUE)
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
# NUMERIC CONVERSION
# =========================
num_cols = [
    "15 Days", "30 Days", "60 Days", "90 Days",
    "120 Days", "More Than 120 Days"
]

for col in num_cols:
    overdue[col] = pd.to_numeric(overdue[col], errors="coerce").fillna(0)

# =========================
# KPI CALCULATION
# =========================
overdue["Overdue"] = overdue["120 Days"] + overdue["More Than 120 Days"]

# =========================
# CLEAN CODES
# =========================
codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce").astype("Int64")

# =========================
# MERGE DATASETS
# =========================
if "Rep Code" in overdue.columns:
    overdue = overdue.merge(codes, on="Rep Code", how="left")

# =========================
# DISPLAY DATA
# =========================
st.subheader("📄 Final Data")
st.dataframe(overdue)

# =========================
# GROUPED KPI
# =========================
def safe_group(df, group_cols, sum_cols):
    group_cols = [c for c in group_cols if c in df.columns]
    sum_cols = [c for c in sum_cols if c in df.columns]

    if not group_cols or not sum_cols:
        return pd.DataFrame()

    return df.groupby(group_cols, as_index=False)[sum_cols].sum()

grouped = safe_group(
    overdue,
    ["Rep Code"],
    ["Overdue", "Balance"]
)

st.subheader("📊 KPI by Rep")
st.dataframe(grouped)

# =========================
# DEBUG INFO
# =========================
st.write("Rows:", overdue.shape[0])
st.write("Columns:", overdue.columns.tolist())
