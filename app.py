import streamlit as st
import pandas as pd

st.title("Overdue Step 8 - KPI")

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
# NUMERIC CONVERSION (safe minimal)
# =========================
num_cols = [
    "15 Days", "30 Days", "60 Days", "90 Days",
    "120 Days", "More Than 120 Days"
]

for col in num_cols:
    overdue[col] = pd.to_numeric(overdue[col], errors="coerce").fillna(0)

# =========================
# OVERDUE KPI
# =========================
overdue["Overdue"] = overdue["120 Days"] + overdue["More Than 120 Days"]

# =========================
# MERGE CODES (if exists)
# =========================
try:
    codes = pd.read_excel("Codes.xlsx")

    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce").astype("Int64")
    overdue = overdue.merge(codes, on="Rep Code", how="left")

except Exception as e:
    st.warning("Codes file not found or merge skipped")
    st.write(e)

# =========================
# SAFE GROUP FUNCTION
# =========================
def safe_group(df, group_cols, sum_cols):
    group_cols = [c for c in group_cols if c in df.columns]
    sum_cols = [c for c in sum_cols if c in df.columns]

    if not group_cols or not sum_cols:
        return pd.DataFrame()

    return df.groupby(group_cols, as_index=False)[sum_cols].sum()

# =========================
# EXAMPLE GROUPING
# =========================
grouped = safe_group(
    overdue,
    ["Rep Code"],
    ["Overdue", "Balance"]
)

# =========================
# SHOW RESULTS
# =========================
st.subheader("📊 KPI Data")
st.dataframe(overdue)

st.subheader("📈 Grouped KPI (Rep Level)")
st.dataframe(grouped)
