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
        "opening_detail": pd.read_excel("Opening Detail.xlsx", header=None),
        "overdue": pd.read_excel("Overdue.xlsx", header=None),
    }


# =========================
# 🧠 FIX SALES
# =========================
def fix_sales_columns(sales):

    expected_cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]

    current_cols = sales.shape[1]

    if current_cols < len(expected_cols):
        for i in range(len(expected_cols) - current_cols):
            sales[f'extra_{i}'] = np.nan

    sales = sales.iloc[:, :len(expected_cols)]
    sales.columns = expected_cols

    return sales


# =========================
# 🚀 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, codes):

    sales = fix_sales_columns(sales)

    for col in [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price"
    ]:
        sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="inner")

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    def group(df, col):
        return df.groupby(col, as_index=False)[
            ["Total Sales Value", "Returns Value", "Sales After Returns"]
        ].sum()

    return {
        "rep": group(sales, "Rep Code"),
        "manager": group(sales, "Manager Code"),
        "area": group(sales, "Area Code"),
        "supervisor": group(sales, "Supervisor Code")
    }


# =========================
# 🚀 OPENING PIPELINE
# =========================
def build_opening_pipeline(opening, codes):

    expected_cols = [
        'Branch',"Evak",'Opening Balance','Total Sales',
        'Returns','Sales Value Before Extra Discounts',
        'Cash Collection','Collection Checks',
        'Returned Chick','Collection Returned Chick',
        "Madinah",'Daienah','End Balance'
    ]

    if opening.shape[1] < len(expected_cols):
        for i in range(len(expected_cols) - opening.shape[1]):
            opening[f'extra_{i}'] = np.nan

    opening = opening.iloc[:, :len(expected_cols)]
    opening.columns = expected_cols

    opening['Rep Code'] = None
    mask = opening['Branch'].astype(str).str.strip() == "كود المندوب"
    opening.loc[mask, 'Rep Code'] = opening.loc[mask, 'Opening Balance']
    opening['Rep Code'] = opening['Rep Code'].ffill()

    opening = opening[
        opening['Branch'].notna() &
        (~opening['Branch'].astype(str).str.contains('كود|اجماليات', na=False))
    ]

    for col in ['Opening Balance','Total Sales','Returns','Cash Collection','Collection Checks','End Balance']:
        opening[col] = pd.to_numeric(opening[col], errors='coerce').fillna(0)

    opening['Total Collection'] = opening['Cash Collection'] + opening['Collection Checks']
    opening["Sales After Returns"] = opening["Total Sales"] - opening['Returns']

    opening = opening.merge(codes, on='Rep Code', how='left')

    def group(df, col):
        return df.groupby(col, as_index=False)[
            ["Total Sales","Returns","Sales After Returns","Total Collection"]
        ].sum()

    return {
        "rep": group(opening, "Rep Code"),
        "manager": group(opening, "Manager Code"),
        "area": group(opening, "Area Code"),
        "supervisor": group(opening, "Supervisor Code")
    }


# =========================
# 🚀 OPENING DETAIL PIPELINE (FIX FINAL)
# =========================
def build_opening_detail_pipeline(opening_detail, codes):

    expected_cols = [
        'Branch',"Evak",'Opening Balance','Total Sales',
        'Returned Sales','Sales Value Before Extra Discounts',
        'Cash Collection',"Blank1",'Collection Checks',
        "Blank2",'Returned Chick','Collection Returned Chick',
        "Madinah",'Daienah','End Balance'
    ]

    # 🔥 FIX: handle missing columns
    if opening_detail.shape[1] < len(expected_cols):
        for i in range(len(expected_cols) - opening_detail.shape[1]):
            opening_detail[f'extra_{i}'] = np.nan

    opening_detail = opening_detail.iloc[:, :len(expected_cols)]
    opening_detail.columns = expected_cols

    # Extract Client
    opening_detail['Client Code'] = None
    opening_detail['Client Name'] = None

    mask = opening_detail['Branch'].astype(str).str.strip() == "كود العميل"

    opening_detail.loc[mask, 'Client Code'] = opening_detail.loc[mask, 'Evak']
    opening_detail.loc[mask, 'Client Name'] = opening_detail.loc[mask, 'Opening Balance']

    opening_detail[['Client Code', 'Client Name']] = opening_detail[['Client Code', 'Client Name']].ffill()

    # Clean
    opening_detail = opening_detail[
        opening_detail['Branch'].notna() &
        (~opening_detail['Branch'].astype(str).str.contains('كود|اجماليات', na=False))
    ]

    # Convert
    for col in ['Opening Balance','Total Sales','Returned Sales','Cash Collection','Collection Checks','End Balance']:
        opening_detail[col] = pd.to_numeric(opening_detail[col], errors='coerce').fillna(0)

    # KPI
    opening_detail["Sales After Returns"] = opening_detail["Total Sales"] - opening_detail['Returned Sales']
    opening_detail['Total Collection'] = opening_detail['Cash Collection'] + opening_detail['Collection Checks']

    return opening_detail.groupby("Client Code", as_index=False)[
        ["Total Sales","Returned Sales","Sales After Returns","Total Collection"]
    ].sum()


# =========================
# 🚀 OVERDUE PIPELINE
# =========================
def build_overdue_pipeline(overdue):

    expected_cols = [
        "Client Name", "Client Code", "30 Days", "60 Days", "90 Days",
        "120 Days", "150 Days", "More Than 150 Days", "Balance"
    ]

    if overdue.shape[1] < len(expected_cols):
        for i in range(len(expected_cols) - overdue.shape[1]):
            overdue[f'extra_{i}'] = np.nan

    overdue = overdue.iloc[:, :len(expected_cols)]
    overdue.columns = expected_cols

    overdue['Overdue Value'] = overdue['120 Days'] + overdue['150 Days'] + overdue['More Than 150 Days']

    return overdue.groupby("Client Code", as_index=False)[["Overdue Value"]].sum()


# =========================
# 🎨 UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI System")

data = load_data()

# SALES
st.header("💰 SALES KPI")
sales = build_sales_pipeline(data["sales"], data["codes"])
st.dataframe(sales["rep"])

# OPENING
st.header("📦 OPENING KPI")
opening = build_opening_pipeline(data["opening"], data["codes"])
st.dataframe(opening["rep"])

# OPENING DETAIL
st.header("📦 OPENING DETAIL KPI")
opening_detail = build_opening_detail_pipeline(data["opening_detail"], data["codes"])
st.dataframe(opening_detail)

# OVERDUE
st.header("⏳ OVERDUE KPI")
overdue = build_overdue_pipeline(data["overdue"])
st.dataframe(overdue)
