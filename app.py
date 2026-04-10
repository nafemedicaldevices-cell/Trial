import streamlit as st
import pandas as pd

st.title("Overdue Step 5")

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
# 🧠 EXTRACT REP HEADER ROWS
# =========================
mask = overdue["Client Name"].astype(str).str.strip().eq("كود المندوب")

overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"].astype("object")
overdue.loc[mask, "Old Rep Name"] = overdue.loc[mask, "30 Days"].astype("object")

# =========================
# 🔁 FORWARD FILL
# =========================
overdue[["Rep Code", "Old Rep Name"]] = overdue[["Rep Code", "Old Rep Name"]].ffill()

# =========================
# SHOW RESULT
# =========================
st.subheader("📄 After Rep Extraction")
st.dataframe(overdue)

# =========================
# DEBUG (optional)
# =========================
st.write("Shape:", overdue.shape)
