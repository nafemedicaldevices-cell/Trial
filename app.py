import streamlit as st
import pandas as pd

# =========================
# LOAD DATA
# =========================
opening_detail = pd.read_excel("Opening Detail.xlsx")
codes = pd.read_excel("Code.xlsx")

st.title("📊 Opening Detail Dashboard")

# =========================
# COLUMN CLEANING
# =========================
opening_detail = opening_detail.iloc[:, :11].copy()

opening_detail.columns = [
    'Client Code',"Client Name",'Opening Balance',
    'Total Sales After Invoice Discounts','Returns',
    'Extra Discounts','Total Collection',"Madfoaat",
    'Tasweyat Daiinah',"End Balance",
    'Motalbet El Fatrah'
]

# =========================
# REP EXTRACTION
# =========================
opening_detail["Rep Code"] = pd.NA
opening_detail["Old Rep Name"] = pd.NA

mask = opening_detail['Client Code'].astype(str).str.strip().eq("كود الفرع")

opening_detail.loc[mask, 'Rep Code'] = opening_detail.loc[mask, 'Returns']
opening_detail.loc[mask, 'Old Rep Name'] = opening_detail.loc[mask, 'Extra Discounts']

opening_detail[["Rep Code","Old Rep Name"]] = opening_detail[["Rep Code","Old Rep Name"]].ffill()

opening_detail["Rep Code"] = pd.to_numeric(opening_detail["Rep Code"], errors="coerce").astype("Int64")

# =========================
# FILTER VALID ROWS
# =========================
opening_detail = opening_detail[
    opening_detail['Client Code'].notna() &
    (opening_detail['Client Code'].astype(str).str.strip() != '') &
    (~opening_detail['Client Code'].astype(str).str.contains(
        "كود الفرع|كود العميل",
        na=False
    ))
].copy()

# =========================
# NUMERIC CONVERSION
# =========================
num_cols = [
    'Opening Balance','Total Sales After Invoice Discounts','Returns',
    'Extra Discounts','Total Collection','End Balance'
]

for col in num_cols:
    opening_detail[col] = pd.to_numeric(opening_detail[col], errors='coerce').fillna(0)

# =========================
# MERGE CODES
# =========================
codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce").astype("Int64")
opening_detail = opening_detail.merge(codes, on="Rep Code", how="left")

# =========================
# BUILD LEVEL (DETAIL 🔥)
# =========================
def build_level(df, level_code):
    return (
        df.groupby([level_code, "Client Code"])[
            ["Opening Balance","End Balance","Total Collection","Extra Discounts"]
        ]
        .sum()
        .reset_index()
    )

# =========================
# LEVELS
# =========================
opening_detail_rep = build_level(opening_detail, "Rep Code")
opening_detail_manager = build_level(opening_detail, "Manager Code")
opening_detail_area = build_level(opening_detail, "Area Code")
opening_detail_supervisor = build_level(opening_detail, "Supervisor Code")

# =========================
# FINAL OUTPUT
# =========================
st.subheader("📌 Rep - Client Level")
st.dataframe(opening_detail_rep)

st.subheader("📌 Manager - Client Level")
st.dataframe(opening_detail_manager)

st.subheader("📌 Area - Client Level")
st.dataframe(opening_detail_area)

st.subheader("📌 Supervisor - Client Level")
st.dataframe(opening_detail_supervisor)
