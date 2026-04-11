import streamlit as st
import pandas as pd

# =========================
# LOAD DATA
# =========================
opening = pd.read_excel("Opening.xlsx")
codes = pd.read_excel("Code.xlsx")

st.title("📊 Opening Dashboard")

st.subheader("Raw Data")
st.dataframe(opening.head())

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

st.subheader("After Column Cleaning")
st.dataframe(opening.head())

# =========================
# REP EXTRACTION
# =========================
opening["Rep Code"] = pd.NA
opening["Old Rep Name"] = pd.NA

mask = opening["Branch"].astype(str).str.strip().eq("كود المندوب")

opening.loc[mask, "Rep Code"] = opening.loc[mask, "Opening Balance"]
opening.loc[mask, "Old Rep Name"] = opening.loc[mask, "Total Sales After Invoice Discounts"]

opening[["Rep Code", "Old Rep Name"]] = opening[["Rep Code", "Old Rep Name"]].ffill()

st.subheader("After Rep Extraction")
st.dataframe(opening[["Branch", "Rep Code", "Old Rep Name"]].head(15))
