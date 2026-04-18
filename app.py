import pandas as pd
import numpy as np
import streamlit as st

# =========================
# 📅 TIME SETTINGS
# =========================
current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1


# =========================
# 📂 LOAD DATA
# =========================
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx", header=None),
        "codes": pd.read_excel("Code.xlsx"),
        "opening": pd.read_excel("Opening.xlsx", header=None),
    }


# =========================
# 🧠 FIX SALES
# =========================
def fix_sales_columns(sales):

    cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit','Returns Unit','Price','Discount','Value'
    ]

    sales = sales.iloc[:, :len(cols)].copy()
    sales.columns = cols

    return sales


# =========================
# 🚀 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, codes):

    sales = fix_sales_columns(sales)

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
# 🚀 OPENING PIPELINE
# =========================
def build_opening_pipeline(opening, codes):

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

    # 🔥 KPI
    opening["Opening KPI"] = opening["Net Sales"] + opening["Collection"]

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    opening = opening.merge(codes, on="Rep Code", how="left")

    return opening.groupby("Rep Code", as_index=False)[
        ["Net Sales","Collection","Opening KPI"]
    ].sum()


# =========================
# 🎨 UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Simple KPI Dashboard")

data = load_data()

# SALES
st.header("💰 Sales")
sales = build_sales_pipeline(data["sales"], data["codes"])
st.dataframe(sales)

# OPENING
st.header("📦 Opening")
opening = build_opening_pipeline(data["opening"], data["codes"])
st.dataframe(opening)
