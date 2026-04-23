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
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),

        "sales": pd.read_excel("Sales.xlsx", header=None),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx"),

        "opening": pd.read_excel("Opening.xlsx", header=None),
        "overdue": pd.read_excel("Overdue.xlsx", header=None),
    }


# =========================
# 🧹 CLEANING LAYER
# =========================

def clean_sales(sales):

    expected_cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]

    sales = sales.iloc[:, :len(expected_cols)].copy()
    sales.columns = expected_cols

    num_cols = [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price",
        "Invoice Discounts"
    ]

    for col in num_cols:
        sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")

    return sales


def clean_opening(opening):

    opening = opening.copy()

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

    opening = opening[
        opening['Branch'].notna() &
        (~opening['Branch'].astype(str).str.contains('كود|اجماليات', na=False))
    ].copy()

    num_cols = [
        'Opening Balance','Total Sales','Returns',
        'Cash Collection','Collection Checks','End Balance'
    ]

    for col in num_cols:
        opening[col] = pd.to_numeric(opening[col], errors='coerce').fillna(0)

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")

    return opening


def clean_overdue(overdue):

    overdue = overdue.copy()

    overdue.columns = [
        "Client Name", "Client Code", "30 Days", "60 Days", "90 Days", "120 Days",
        "150 Days", "More Than 150 Days", "Balance"
    ]

    overdue['Rep Code'] = None

    mask = overdue['Client Name'].astype(str).str.strip() == "كود المندوب"
    overdue.loc[mask, 'Rep Code'] = overdue.loc[mask, 'Client Code']
    overdue['Rep Code'] = overdue['Rep Code'].ffill()

    overdue = overdue[
        overdue['Client Name'].notna() &
        (~overdue['Client Name'].astype(str).str.contains(
            'اجمال|كود', na=False
        ))
    ].copy()

    num_cols = [
        '30 Days','60 Days','90 Days','120 Days',
        '150 Days','More Than 150 Days','Rep Code'
    ]

    for col in num_cols:
        overdue[col] = pd.to_numeric(overdue[col], errors='coerce').fillna(0)

    overdue['Rep Code'] = overdue['Rep Code'].astype(int)

    return overdue


def clean_codes(codes):
    codes = codes.copy()
    codes.columns = codes.columns.str.strip()
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")
    return codes


# =========================
# 🚀 PROCESSING LAYER
# =========================

def build_sales_pipeline(sales, codes):

    sales = sales.merge(codes, on="Rep Code", how="inner")

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    return sales.groupby("Rep Code", as_index=False)[
        ["Total Sales Value","Returns Value","Sales After Returns"]
    ].sum()


def build_opening_pipeline(opening, codes):

    opening["Total Collection"] = opening["Cash Collection"] + opening["Collection Checks"]
    opening["Sales After Returns"] = opening["Total Sales"] - opening["Returns"]

    opening["Opening KPI"] = opening["Sales After Returns"] + opening["Total Collection"]

    opening = opening.merge(codes, on="Rep Code", how="left")

    return opening.groupby("Rep Code", as_index=False)[
        ["Sales After Returns","Total Collection","Opening KPI"]
    ].sum()


def build_overdue_pipeline(overdue, codes):

    overdue["Overdue Value"] = (
        overdue['120 Days'] +
        overdue['150 Days'] +
        overdue['More Than 150 Days']
    )

    overdue = overdue.merge(codes, on="Rep Code", how="left")

    return overdue.groupby("Rep Code", as_index=False)[
        ["Overdue Value"]
    ].sum()


# =========================
# 🎨 STREAMLIT UI
# =========================

st.set_page_config(layout="wide")
st.title("📊 KPI Dashboard (Clean Architecture)")

data = load_data()

# CLEAN
sales_clean = clean_sales(data["sales"])
opening_clean = clean_opening(data["opening"])
overdue_clean = clean_overdue(data["overdue"])
codes_clean = clean_codes(data["codes"])

# PROCESS
sales = build_sales_pipeline(sales_clean, codes_clean)
opening = build_opening_pipeline(opening_clean, codes_clean)
overdue = build_overdue_pipeline(overdue_clean, codes_clean)

# UI
st.header("💰 Sales KPI")
st.dataframe(sales)

st.header("📦 Opening KPI")
st.dataframe(opening)

st.header("⏳ Overdue KPI")
st.dataframe(overdue)
