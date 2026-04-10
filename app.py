import streamlit as st
import pandas as pd

st.title("Overdue Step 6")

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
# FIX DTYPE
# =========================
overdue["Rep Code"] = pd.NA
overdue["Old Rep Name"] = pd.NA

# =========================
# 🧠 FILTER VALID ROWS
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
st.subheader("📄 After Filtering Valid Rows")
st.dataframe(overdue)

# =========================
# DEBUG INFO
# =========================
st.write("Shape:", overdue.shape)
