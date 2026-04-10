import streamlit as st
import pandas as pd

st.title("Overdue Pipeline - Full Clean Version")

# =========================
# 📥 LOAD DATA
# =========================
overdue = pd.read_excel("Overdue.xlsx")
codes = pd.read_excel("Code.xlsx")   # ✔ مهم زي ما طلبت

# =========================
# BASIC CLEANING
# =========================
overdue = overdue.iloc[:, :9].copy()

overdue.columns = [
    "Client Name", "Client Code", "15 Days", "30 Days", "60 Days", "90 Days",
    "120 Days", "More Than 120 Days", "Balance"
]

# =========================
# INIT REP COLUMNS
# =========================
overdue["Rep Code"] = pd.NA
overdue["Old Rep Name"] = pd.NA

# =========================
# EXTRACT REP HEADER ROWS
# =========================
mask = overdue["Client Name"].astype(str).str.strip().eq("كود المندوب")

overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"]
overdue.loc[mask, "Old Rep Name"] = overdue.loc[mask, "30 Days"]

# forward fill
overdue[["Rep Code", "Old Rep Name"]] = overdue[["Rep Code", "Old Rep Name"]].ffill()

# =========================
# FILTER VALID ROWS
# =========================
overdue = overdue[
    overdue["Client Name"].notna() &
    (overdue["Client Name"].astype(str).str.strip() != "") &
    (~overdue["Client Name"].astype(str).str.contains(
        "اجمالــــــي التقرير|اجمالى الفرع/المندوب|كود الفرع|كود المندوب|اسم العميل",
        na=False
    ))
].copy()

# =========================
# NUMERIC CONVERSION
# =========================
num_cols = [
    "15 Days","30 Days","60 Days","90 Days",
    "120 Days","More Than 120 Days","Balance"
]

for col in num_cols:
    overdue[col] = pd.to_numeric(overdue[col], errors="coerce").fillna(0)

# safe IDs
overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce").astype("Int64")
overdue["Client Code"] = pd.to_numeric(overdue["Client Code"], errors="coerce").astype("Int64")

# =========================
# KPI
# =========================
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
# OUTPUT
# =========================
st.subheader("📊 Final Data")
st.dataframe(overdue)

st.write("Shape:", overdue.shape)
