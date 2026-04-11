import streamlit as st
import pandas as pd

# =========================
# LOAD DATA
# =========================
opening = pd.read_excel("Opening.xlsx")
codes = pd.read_excel("Code.xlsx")

st.title("📊 Opening Dashboard")

# =========================
# COLUMN STANDARDIZATION
# =========================
opening = opening.copy()

opening.columns = [
    'Branch',"Evak",'Opening Balance','Total Sales After Invoice Discounts',
    'Returns','Sales Value Before Extra Discounts',
    'Cash Collection','Collection Checks',
    'Returned Chick','Collection Returned Chick',
    "Extra Discounts",'Daienah','End Balance'
]

# =========================
# REP EXTRACTION
# =========================
opening["Rep Code"] = pd.NA
opening["Old Rep Name"] = pd.NA

mask = opening["Branch"].astype(str).str.strip().eq("كود المندوب")

opening.loc[mask, "Rep Code"] = opening.loc[mask, "Opening Balance"]
opening.loc[mask, "Old Rep Name"] = opening.loc[mask, "Total Sales After Invoice Discounts"]

opening[["Rep Code", "Old Rep Name"]] = opening[["Rep Code", "Old Rep Name"]].ffill()

# =========================
# FINAL DISPLAY
# =========================
st.subheader("Opening Data After Rep Extraction")
st.dataframe(opening.head(20))
