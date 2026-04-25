import streamlit as st
import pandas as pd

from cleaning import (
    load_targets,
    load_haraka,
    load_overdue,
    load_client_haraka
)

st.set_page_config(layout="wide")

st.title("📊 Sales Dashboard")

# =========================
# 📂 LOAD DATA
# =========================
@st.cache_data
def load_all():

    targets = load_targets()
    rep_haraka = load_haraka()
    client_haraka = load_client_haraka()

    # =========================
    # 🔥 MASTER CODES
    # =========================
    codes = pd.read_excel("Code.xlsx")
    codes.columns = codes.columns.str.strip()
    codes["Rep Code"] = codes["Rep Code"].astype(str).str.strip()

    # =========================
    # 🔥 OVERDUE
    # =========================
    overdue = load_overdue("Overdue.xlsx", codes)

    # =========================
    # 🔥 SALES (FIXED)
    # =========================
    sales = pd.read_excel("Sales.xlsx")
    sales.columns = sales.columns.str.strip()

    # 👇 DEBUG (لو عايزة تشوفي الأعمدة في اللوج)
    print("Sales Columns:", sales.columns.tolist())

    # --- Rep Code detection ---
    possible_rep_cols = [
        "Rep Code", "RepCode", "Code", "Rep_Code", "كود المندوب"
    ]

    rep_col = None
    for col in possible_rep_cols:
        if col in sales.columns:
            rep_col = col
            break

    if rep_col is None:
        raise Exception("❌ مفيش عمود Rep Code في Sales.xlsx")

    sales = sales.rename(columns={rep_col: "Rep Code"})

    # --- Date detection ---
    possible_date_cols = [
        "Date", "Invoice Date", "Sales Date", "التاريخ"
    ]

    date_col = None
    for col in possible_date_cols:
        if col in sales.columns:
            date_col = col
            break

    if date_col is None:
        raise Exception("❌ مفيش عمود Date في Sales.xlsx")

    sales = sales.rename(columns={date_col: "Date"})

    # --- Sales Value detection ---
    possible_value_cols = [
        "Sales Value", "Value", "Net Sales", "Sales", "القيمة"
    ]

    val_col = None
    for col in possible_value_cols:
        if col in sales.columns:
            val_col = col
            break

    if val_col is None:
        raise Exception("❌ مفيش عمود Sales Value في Sales.xlsx")

    sales = sales.rename(columns={val_col: "Sales Value"})

    # تنظيف
    sales["Rep Code"] = sales["Rep Code"].astype(str).str.strip()
    sales["Date"] = pd.to_datetime(sales["Date"], errors="coerce")
    sales["Month"] = sales["Date"].dt.strftime("%b")

    return targets, rep_haraka, client_haraka, overdue, codes, sales


targets, rep_haraka, client_haraka, overdue, codes, sales = load_all()

# =========================
# 🎯 FILTERS
# =========================
st.sidebar.header("Filters")

rep_list = sorted(codes["Rep Name"].dropna().unique())
sup_list = sorted(codes["Supervisor Name"].dropna().unique())
manager_list = sorted(codes["Manager Name"].dropna().unique())
area_list = sorted(codes["Area Name"].dropna().unique())

rep_filter = st.sidebar.multiselect("Rep", rep_list)
sup_filter = st.sidebar.multiselect("Supervisor", sup_list)
manager_filter = st.sidebar.multiselect("Manager", manager_list)
area_filter = st.sidebar.multiselect("Area", area_list)

# =========================
# 🗓️ PERIOD
# =========================
period_type = st.sidebar.selectbox(
    "Period",
    ["Monthly", "Quarterly", "YTD", "Full Year"]
)

month_order = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

selected_month = st.sidebar.selectbox("Month", month_order)

quarter_map = {
    "Q1": ["Jan","Feb","Mar"],
    "Q2": ["Apr","May","Jun"],
    "Q3": ["Jul","Aug","Sep"],
    "Q4": ["Oct","Nov","Dec"]
}

quarter = st.sidebar.selectbox("Quarter", list(quarter_map.keys()))

# =========================
# 🔥 FILTER CODES FIRST
# =========================
filtered_codes = codes.copy()

if rep_filter:
    filtered_codes = filtered_codes[filtered_codes["Rep Name"].isin(rep_filter)]

if sup_filter:
    filtered_codes = filtered_codes[filtered_codes["Supervisor Name"].isin(sup_filter)]

if manager_filter:
    filtered_codes = filtered_codes[filtered_codes["Manager Name"].isin(manager_filter)]

if area_filter:
    filtered_codes = filtered_codes[filtered_codes["Area Name"].isin(area_filter)]

valid_reps = filtered_codes["Rep Code"].unique()

# =========================
# 🔗 APPLY FILTERS
# =========================
client_haraka_f = client_haraka[client_haraka["Rep Code"].isin(valid_reps)]
overdue_f = overdue[overdue["Rep Code"].isin(valid_reps)]
sales_f = sales[sales["Rep Code"].isin(valid_reps)]

# =========================
# 🎯 TARGET
# =========================
target_rep = targets["Rep"].copy()
target_rep["Code"] = target_rep["Code"].astype(str).str.strip()
target_rep = target_rep[target_rep["Code"].isin(valid_reps)]

if period_type == "Monthly":

    target_value = target_rep[target_rep["Month"] == selected_month]["Target (Value)"].sum()
    sales_value = sales_f[sales_f["Month"] == selected_month]["Sales Value"].sum()

elif period_type == "Quarterly":

    months = quarter_map[quarter]

    target_value = target_rep[target_rep["Month"].isin(months)]["Target (Value)"].sum()
    sales_value = sales_f[sales_f["Month"].isin(months)]["Sales Value"].sum()

elif period_type == "YTD":

    idx = month_order.index(selected_month) + 1
    months = month_order[:idx]

    target_value = target_rep[target_rep["Month"].isin(months)]["Target (Value)"].sum()
    sales_value = sales_f[sales_f["Month"].isin(months)]["Sales Value"].sum()

else:

    target_value = target_rep["Target (Value)"].sum()
    sales_value = sales_f["Sales Value"].sum()

# =========================
# 📊 KPIs
# =========================
achievement = (sales_value / target_value * 100) if target_value > 0 else 0
total_collection = client_haraka_f["Total Collection"].sum()
total_overdue = overdue_f["Overdue"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("🎯 Target", f"{target_value:,.0f}")
col2.metric("💰 Sales", f"{sales_value:,.0f}")
col3.metric("📈 Achievement %", f"{achievement:.1f}%")
col4.metric("⚠️ Overdue", f"{total_overdue:,.0f}")

# =========================
# 📈 CHART
# =========================
st.subheader("Target vs Sales")

compare_df = pd.DataFrame({
    "Target": [target_value],
    "Sales": [sales_value]
})

st.bar_chart(compare_df)

# =========================
# 📋 TABLES
# =========================
st.subheader("Overdue")
st.dataframe(overdue_f, use_container_width=True)

st.subheader("Client Harakah")
st.dataframe(client_haraka_f, use_container_width=True)
