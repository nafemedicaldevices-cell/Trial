import streamlit as st
import pandas as pd

st.title("Step 5 - Filter Valid Rows")

# =========================
# LOAD DATA
# =========================
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
# INIT REP COLUMNS
# =========================
overdue["Rep Code"] = pd.NA
overdue["Old Rep Name"] = pd.NA

mask_rep = overdue["Client Name"].astype(str).str.strip().eq("كود المندوب")

overdue.loc[mask_rep, "Rep Code"] = overdue.loc[mask_rep, "Client Code"]
overdue.loc[mask_rep, "Old Rep Name"] = overdue.loc[mask_rep, "30 Days"]

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
# SHOW RESULT
# =========================
st.subheader("📄 After Filtering")
st.dataframe(overdue)

# =========================
# DEBUG
# =========================
st.write("Rows after filter:", overdue.shape[0])
