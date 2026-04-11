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
# FILTER VALID ROWS
# =========================
opening = opening[
    opening['Branch'].notna() &
    (opening['Branch'].astype(str).str.strip() != '') &
    (~opening['Branch'].astype(str).str.contains(
        'نسبة المندوب|كود المندوب|اجماليات|كود الفرع',
        na=False
    ))
].copy()

# =========================
# NUMERIC CONVERSION
# =========================
num_cols = [
    'Opening Balance','Total Sales After Invoice Discounts','Returns',
    'Sales Value Before Extra Discounts',
    'Cash Collection','Collection Checks',
    'Returned Chick','Collection Returned Chick',
    'Extra Discounts','Daienah','End Balance'
]

for col in num_cols:
    opening[col] = pd.to_numeric(opening[col], errors='coerce').fillna(0)

# =========================
# KPI CALCULATIONS
# =========================
opening['Total Collection'] = opening['Cash Collection'] + opening['Collection Checks']

opening['Sales After Returns'] = (
    opening['Total Sales After Invoice Discounts'] - opening['Returns']
)

# =========================
# MERGE CODES
# =========================
opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce").astype("Int64")
codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce").astype("Int64")

opening = opening.merge(codes, on="Rep Code", how="left")

# =========================
# BUILD LEVEL (زي Overdue 🔥)
# =========================
def build_level(df, level_code):
    return (
        df.groupby(level_code)[
            ["Opening Balance","Cash Collection","Collection Checks","Extra Discounts","End Balance"]
        ]
        .sum()
        .reset_index()
    )

# =========================
# REP LEVEL ONLY
# =========================
opening_rep = build_level(opening, "Rep Code")

# =========================
# FINAL OUTPUT
# =========================
st.subheader("📌 Opening - Rep Level")
st.dataframe(opening_rep)
