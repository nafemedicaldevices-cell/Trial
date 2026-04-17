import pandas as pd
import numpy as np
import streamlit as st

# =========================
# 📂 LOAD DATA
# =========================
@st.cache_data
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx", header=None),
        "codes": pd.read_excel("Code.xlsx"),
        "opening": pd.read_excel("Opening.xlsx", header=None),
        "overdue": pd.read_excel("Overdue.xlsx", header=None),
        "target": pd.read_excel("Target Rep.xlsx"),
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
    sales = sales.iloc[:, :len(expected_cols)].copy()
    sales.columns = expected_cols
    return sales


# =========================
# 💰 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, codes):

    sales = fix_sales_columns(sales)

    sales.columns = sales.columns.str.strip()
    codes.columns = codes.columns.str.strip()

    for col in [
        "Sales Unit Before Edit","Returns Unit Before Edit",
        "Sales Price","Invoice Discounts"
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
            ["Total Sales Value","Returns Value","Sales After Returns"]
        ].sum()

    return {
        "rep": group(sales,"Rep Name"),
        "manager": group(sales,"Manager Name"),
        "area": group(sales,"Area Name"),
        "supervisor": group(sales,"Supervisor Name"),
    }


# =========================
# 📦 OPENING PIPELINE
# =========================
def build_opening_pipeline(opening, codes):

    opening = opening.iloc[:, :13]

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
    ]

    for col in ['Opening Balance','Total Sales','Returns','Cash Collection','Collection Checks']:
        opening[col] = pd.to_numeric(opening[col], errors='coerce').fillna(0)

    opening['Total Collection'] = opening['Cash Collection'] + opening['Collection Checks']
    opening["Sales After Returns"] = opening["Total Sales"] - opening['Returns']

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    opening = opening.merge(codes, on='Rep Code', how='left')

    def group(df, col):
        return df.groupby(col, as_index=False)[
            ["Total Sales","Returns","Sales After Returns","Total Collection"]
        ].sum()

    return {
        "rep": group(opening,"Rep Name"),
        "manager": group(opening,"Manager Name"),
        "area": group(opening,"Area Name"),
        "supervisor": group(opening,"Supervisor Name"),
    }


# =========================
# ⏳ OVERDUE PIPELINE
# =========================
def build_overdue_pipeline(overdue, codes):

    overdue.columns = [
        "Client Name","Client Code","30 Days","60 Days","90 Days",
        "120 Days","150 Days","More Than 150 Days","Balance"
    ]

    overdue['Rep Code'] = overdue['Client Code'].ffill()

    overdue['Overdue Value'] = overdue['120 Days'] + overdue['150 Days'] + overdue['More Than 150 Days']

    overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce")
    overdue = overdue.merge(codes, on='Rep Code', how='left')

    def group(df, col):
        return df.groupby(col, as_index=False)[["Overdue Value"]].sum()

    return {
        "rep": group(overdue,"Rep Name"),
        "manager": group(overdue,"Manager Name"),
        "area": group(overdue,"Area Name"),
        "supervisor": group(overdue,"Supervisor Name"),
    }


# =========================
# 🎯 TARGET (FIXED)
# =========================
def build_target(target, codes):

    target = target.copy()
    codes = codes.copy()

    target.columns = target.columns.str.strip()
    codes.columns = codes.columns.str.strip()

    # 🔍 محاولة اكتشاف اسم العمود
    possible_rep_cols = ["Rep Code", "RepCode", "كود المندوب"]

    rep_col = None
    for col in possible_rep_cols:
        if col in target.columns:
            rep_col = col
            break

    if rep_col is None:
        st.error(f"❌ الأعمدة الموجودة: {list(target.columns)}")
        return pd.DataFrame()

    target.rename(columns={rep_col: "Rep Code"}, inplace=True)

    target["Rep Code"] = pd.to_numeric(target["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    target = target.merge(codes, on="Rep Code", how="left")

    if "Target (Unit)" not in target.columns:
        target["Target (Unit)"] = 0

    if "Sales Price" not in target.columns:
        target["Sales Price"] = 0

    target["Target (Unit)"] = pd.to_numeric(target["Target (Unit)"], errors="coerce").fillna(0)
    target["Sales Price"] = pd.to_numeric(target["Sales Price"], errors="coerce").fillna(0)

    target["Target Value"] = target["Target (Unit)"] * target["Sales Price"]

    return target


# =========================
# 🎛️ FILTER
# =========================
def apply_filter(data, filter_type, value):

    key_map = {
        "Rep": "rep",
        "Supervisor": "supervisor",
        "Area": "area",
        "Manager": "manager"
    }

    col_map = {
        "Rep": "Rep Name",
        "Supervisor": "Supervisor Name",
        "Area": "Area Name",
        "Manager": "Manager Name"
    }

    df = data[key_map[filter_type]]

    return df[df[col_map[filter_type]] == value]


# =========================
# 🎨 UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 KPI Dashboard")

data = load_data()

sales = build_sales_pipeline(data["sales"], data["codes"])
opening = build_opening_pipeline(data["opening"], data["codes"])
overdue = build_overdue_pipeline(data["overdue"], data["codes"])
target = build_target(data["target"], data["codes"])

# =========================
# 🎛️ FILTER
# =========================
st.sidebar.header("Filters")

filter_type = st.sidebar.radio("Filter By", ["Rep","Supervisor","Area","Manager"])

options = sales[filter_type.lower()][f"{filter_type} Name"].dropna().unique()
selected_value = st.sidebar.selectbox("Select", options)

# =========================
# 📊 KPI
# =========================
filtered_sales = apply_filter(sales, filter_type, selected_value)
total_sales = filtered_sales["Sales After Returns"].sum()

target_filtered = target[target[f"{filter_type} Name"] == selected_value]
total_target = target_filtered["Target Value"].sum()

achievement = (total_sales / total_target * 100) if total_target != 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("🎯 Target", f"{total_target:,.0f}")
col2.metric("💰 Sales", f"{total_sales:,.0f}")
col3.metric("📊 Achievement %", f"{achievement:.1f}%")

# =========================
# 📊 TABLES
# =========================
st.header("💰 SALES")
st.dataframe(filtered_sales)

st.header("📦 OPENING")
st.dataframe(apply_filter(opening, filter_type, selected_value))

st.header("⏳ OVERDUE")
st.dataframe(apply_filter(overdue, filter_type, selected_value))
