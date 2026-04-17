import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# =========================
# 📅 TIME SETTINGS
# =========================
current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1

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
    }

# =========================
# 🧠 FIX SALES
# =========================
def fix_sales_columns(sales):
    expected_cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit','Returns Unit',
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

    num_cols = ["Sales Unit","Returns Unit","Sales Price","Invoice Discounts"]

    for col in num_cols:
        sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="inner")

    sales["Total Sales Value"] = sales["Sales Unit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    def group(df, col):
        return df.groupby(col, as_index=False)[["Sales After Returns"]].sum()

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

    for col in ['Total Sales','Returns','Cash Collection','Collection Checks']:
        opening[col] = pd.to_numeric(opening[col], errors='coerce').fillna(0)

    opening['Total Collection'] = opening['Cash Collection'] + opening['Collection Checks']
    opening["Sales After Returns"] = opening["Total Sales"] - opening['Returns']

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    opening = opening.merge(codes, on='Rep Code', how='left')

    def group(df, col):
        return df.groupby(col, as_index=False)[["Sales After Returns"]].sum()

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

    overdue['Overdue Value'] = (
        overdue['120 Days'] +
        overdue['150 Days'] +
        overdue['More Than 150 Days']
    )

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
# 🚀 UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 KPI Dashboard - Waterfall Analysis")

data = load_data()

sales = build_sales_pipeline(data["sales"], data["codes"])
opening = build_opening_pipeline(data["opening"], data["codes"])
overdue = build_overdue_pipeline(data["overdue"], data["codes"])

# =========================
# 🎛️ FILTER
# =========================
st.sidebar.header("Filters")

filter_type = st.sidebar.radio(
    "Filter By",
    ["Rep","Supervisor","Area","Manager"]
)

col_map = {
    "Rep": "Rep Name",
    "Supervisor": "Supervisor Name",
    "Area": "Area Name",
    "Manager": "Manager Name"
}

options = sales["rep"][col_map[filter_type]].dropna().unique()
selected_value = st.sidebar.selectbox("Select", options)

def apply_filter(data, key, col, value):
    df = data[key]
    if col in df.columns:
        return df[df[col] == value]
    return df

filtered_sales = apply_filter(sales, "rep", col_map[filter_type], selected_value)
filtered_opening = apply_filter(opening, "rep", col_map[filter_type], selected_value)
filtered_overdue = apply_filter(overdue, "rep", col_map[filter_type], selected_value)

# =========================
# 🎯 KPI SIMPLE
# =========================
actual = filtered_sales["Sales After Returns"].sum()
target = 1000000
pct = (actual / target * 100) if target else 0

st.markdown(f"""
### 📊 Sales: {actual:,.0f} | 🎯 Target: {target:,.0f} | 📈 {pct:.1f}%
""")

# =========================
# 💰 WATERFALL ANALYSIS
# =========================
st.header("💰 Sales Waterfall Analysis")

df = filtered_sales.copy()

total_sales = df["Sales After Returns"].sum()
returns = df["Returns Value"].sum() if "Returns Value" in df.columns else 0
discounts = df["Invoice Discounts"].sum() if "Invoice Discounts" in df.columns else 0

net_after_returns = total_sales - returns
net_sales = net_after_returns - discounts

# =========================
# 📊 WATERFALL CHART
# =========================
fig = go.Figure(go.Waterfall(
    name="Sales Flow",
    orientation="v",

    measure=[
        "absolute",
        "relative",
        "relative",
        "total"
    ],

    x=[
        "Total Sales",
        "Returns",
        "Discounts",
        "Net Sales"
    ],

    y=[
        total_sales,
        -returns,
        -discounts,
        net_sales
    ],

    connector={"line": {"color": "gray"}}
))

fig.update_layout(
    title="Sales Flow (Waterfall Diagram)",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 📋 TABLES
# =========================
st.header("💰 Sales Data")
st.dataframe(filtered_sales)

st.header("📦 Opening Data")
st.dataframe(filtered_opening)

st.header("⏳ Overdue Data")
st.dataframe(filtered_overdue)
