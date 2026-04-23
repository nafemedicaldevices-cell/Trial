import pandas as pd
import numpy as np
import streamlit as st

# =========================
# 📂 LOAD DATA
# =========================
def load_data():
    return {
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),

        "sales": pd.read_excel("Sales.xlsx", header=None),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx"),

        "opening": pd.read_excel("Opening.xlsx", header=None),
        "overdue": pd.read_excel("Overdue.xlsx", header=None),
    }


# =========================
# 🧠 FIX SALES COLUMNS
# =========================
def fix_sales_columns(sales):

    expected_cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]

    sales = sales.iloc[:, :len(expected_cols)].copy()
    sales.columns = expected_cols

    return sales


# =========================
# 🧼 CLEAN TARGET (NO KPI)
# =========================
def clean_target(df, mapping, id_name):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()
    mapping.columns = mapping.columns.str.strip()

    if "Sales Price" not in df.columns:
        df["Sales Price"] = 0

    fixed_cols = [c for c in ["Year", "Product Code", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    df[id_name] = pd.to_numeric(
        df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True),
        errors="coerce"
    )

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce")

    # 🔥 CLEAN ONLY (no calculations)

    return df


# =========================
# 🧼 CLEAN SALES (NO KPI)
# =========================
def clean_sales(sales, codes):

    sales = fix_sales_columns(sales)

    sales.columns = sales.columns.str.strip()
    codes.columns = codes.columns.str.strip()

    sales = sales.dropna(how="all")

    # Text cleaning
    text_cols = ["Warehouse Name", "Client Name", "Notes", "MF", "Mostanad"]
    for col in text_cols:
        if col in sales.columns:
            sales[col] = sales[col].astype(str).str.strip()

    # Date only
    sales["Date"] = pd.to_datetime(sales["Date"], errors="coerce")

    # Numeric only
    num_cols = [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price",
        "Invoice Discounts"
    ]

    for col in num_cols:
        sales[col] = pd.to_numeric(sales[col], errors="coerce")

    # Codes
    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    # Merge only
    sales = sales.merge(codes, on="Rep Code", how="left")

    return sales


# =========================
# 🧼 CLEAN OPENING (NO KPI)
# =========================
def clean_opening(opening, codes):

    opening.columns = [
        'Branch',"Evak",'Opening Balance','Total Sales',
        'Returns','Sales Value Before Extra Discounts',
        'Cash Collection','Collection Checks',
        'Returned Chick','Collection Returned Chick',
        "Madinah",'Daienah','End Balance'
    ]

    opening['Rep Code'] = None

    mask = opening['Branch'].astype(str).str.strip() == "كود المندوب"
    opening.loc[mask, 'Rep Code'] = opening.loc[mask, 'Opening Balance']

    opening['Rep Code'] = opening['Rep Code'].ffill()

    num_cols = [
        'Opening Balance','Total Sales','Returns',
        'Cash Collection','Collection Checks','End Balance'
    ]

    for col in num_cols:
        opening[col] = pd.to_numeric(opening[col], errors='coerce')

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    opening = opening.merge(codes, on='Rep Code', how='left')

    return opening


# =========================
# 🧼 CLEAN OVERDUE (NO KPI)
# =========================
def clean_overdue(overdue, codes):

    overdue.columns = [
        "Client Name", "Client Code", "30 Days", "60 Days", "90 Days", "120 Days",
        "150 Days", "More Than 150 Days", "Balance"
    ]

    overdue["Rep Code"] = None

    mask = overdue['Client Name'].astype(str).str.strip() == "كود المندوب"
    overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"]

    overdue["Rep Code"] = overdue["Rep Code"].ffill()

    num_cols = [
        '30 Days','60 Days','90 Days','120 Days',
        '150 Days','More Than 150 Days'
    ]

    for col in num_cols:
        overdue[col] = pd.to_numeric(overdue[col], errors="coerce")

    overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce")

    overdue = overdue.merge(codes, on="Rep Code", how="left")

    return overdue


# =========================
# 🎨 STREAMLIT UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 CLEANING LAYER ONLY")

data = load_data()

st.header("🎯 TARGET CLEAN")
st.dataframe(clean_target(data["target_rep"], data["mapping"], "Rep Code"))

st.header("💰 SALES CLEAN")
st.dataframe(clean_sales(data["sales"], data["codes"]))

st.header("📦 OPENING CLEAN")
st.dataframe(clean_opening(data["opening"], data["codes"]))

st.header("⏳ OVERDUE CLEAN")
st.dataframe(clean_overdue(data["overdue"], data["codes"]))
