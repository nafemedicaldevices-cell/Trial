import streamlit as st
import pandas as pd

st.title("Step 3 - Numeric + KPI + Merge")

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
# REP SETUP (from previous step assumed)
# =========================
overdue["Rep Code"] = pd.NA
overdue["Old Rep Name"] = pd.NA

mask = overdue["Client Name"].astype(str).str.strip().eq("كود المندوب")

overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"]
overdue.loc[mask, "Old Rep Name"] = overdue.loc[mask, "30 Days"]

overdue[["Rep Code", "Old Rep Name"]] = overdue[["Rep Code", "Old Rep Name"]].ffill()

# =========================
# NUMERIC CONVERSION
# =========================
num_cols = [
    "15 Days", "30 Days", "60 Days", "90 Days",
    "120 Days", "More Than 120 Days",
    "Client Code", "Rep Code"
]

for col in num_cols:
    overdue[col] = pd.to_numeric(overdue[col], errors="coerce").fillna(0)

overdue["Rep Code"] = overdue["Rep Code"].astype("Int64")
overdue["Client Code"] = overdue["Client Code"].astype("Int64")

st.write("After Numeric Conversion")
st.dataframe(overdue)

# =========================
# OVERDUE KPI
# =========================
overdue["Overdue"] = overdue["120 Days"] + overdue["More Than 120 Days"]

st.write("After KPI Calculation")
st.dataframe(overdue)

# =========================
# MERGE CODES
# =========================
codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce").astype("Int64")

overdue = overdue.merge(codes, on="Rep Code", how="left")

# =========================
# FINAL OUTPUT
# =========================
st.subheader("📊 Final Data After Merge")
st.dataframe(overdue)

st.write("Shape:", overdue.shape)
