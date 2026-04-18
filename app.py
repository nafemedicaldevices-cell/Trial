import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(layout="wide")
st.title("📊 KPI Dashboard")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    sales = pd.read_excel("Sales.xlsx", header=None)
    codes = pd.read_excel("Code.xlsx")
    opening = pd.read_excel("Opening.xlsx", header=None)
    return sales, codes, opening


# =========================
# FIX SALES
# =========================
def fix_sales(sales):
    cols = [
        'Date','Warehouse','Client Code','Client Name','Notes','MF','Doc',
        'Rep Code','Sales Unit','Returns Unit','Price','Discount','Value'
    ]
    sales = sales.iloc[:, :len(cols)].copy()
    sales.columns = cols
    return sales


# =========================
# SALES KPI
# =========================
def sales_kpi(sales, codes):
    sales = fix_sales(sales)

    for col in ["Sales Unit","Returns Unit","Price"]:
        sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="left")

    sales["Sales Value"] = sales["Sales Unit"] * sales["Price"]
    sales["Returns Value"] = sales["Returns Unit"] * sales["Price"]

    return sales.groupby("Rep Code", as_index=False)[
        ["Sales Value","Returns Value"]
    ].sum()


# =========================
# OPENING KPI
# =========================
def opening_kpi(opening, codes):

    opening.columns = [
        'Branch',"Evak",'Opening Balance','Total Sales',
        'Returns','x','Cash','Checks','x2','x3',"x4",'x5','End'
    ]

    opening['Rep Code'] = None
    mask = opening['Branch'].astype(str).str.strip() == "كود المندوب"
    opening.loc[mask, 'Rep Code'] = opening.loc[mask, 'Opening Balance']
    opening['Rep Code'] = opening['Rep Code'].ffill()

    opening = opening[opening['Branch'].notna()]

    for col in ['Total Sales','Returns','Cash','Checks']:
        opening[col] = pd.to_numeric(opening[col], errors="coerce").fillna(0)

    opening["Collection"] = opening["Cash"] + opening["Checks"]
    opening["Net Sales"] = opening["Total Sales"] - opening["Returns"]
    opening["Opening KPI"] = opening["Net Sales"] + opening["Collection"]

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    opening = opening.merge(codes, on="Rep Code", how="left")

    return opening.groupby("Rep Code", as_index=False)[
        ["Net Sales","Collection","Opening KPI"]
    ].sum()


# =========================
# RUN APP
# =========================
sales_df, codes_df, opening_df = load_data()

st.header("💰 Sales KPI")
st.dataframe(sales_kpi(sales_df, codes_df))

st.header("📦 Opening KPI")
st.dataframe(opening_kpi(opening_df, codes_df))
