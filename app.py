import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📊 Sales & Target Dashboard")

# =========================
# 📂 LOAD CODES
# =========================
codes = pd.read_excel("Code.xlsx")
codes.columns = codes.columns.str.strip()
codes["Rep Code"] = codes["Rep Code"].astype(str).str.strip()

# =========================
# 🔄 RESET FILTERS
# =========================
def reset_filters():
    st.session_state.rep_filter = []
    st.session_state.sup_filter = []
    st.session_state.manager_filter = []
    st.session_state.area_filter = []

st.sidebar.button("🔄 Reset Filters", on_click=reset_filters)

# =========================
# 🎯 FILTERS
# =========================
st.sidebar.header("Filters")

rep_list = sorted(codes["Rep Name"].dropna().unique())
sup_list = sorted(codes["Supervisor Name"].dropna().unique())
manager_list = sorted(codes["Manager Name"].dropna().unique())
area_list = sorted(codes["Area Name"].dropna().unique())

rep_filter = st.sidebar.multiselect("Rep", rep_list, key="rep_filter")
sup_filter = st.sidebar.multiselect("Supervisor", sup_list, key="sup_filter")
manager_filter = st.sidebar.multiselect("Manager", manager_list, key="manager_filter")
area_filter = st.sidebar.multiselect("Area", area_list, key="area_filter")

# =========================
# 🔥 FILTER CODES
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

valid_reps = filtered_codes["Rep Code"].astype(str).str.strip().unique()

# =========================
# 📂 LOAD TARGETS
# =========================
def load_targets():
    df = pd.read_excel("Target Rep.xlsx", sheet_name=None)

    all_data = []

    for _, sheet in df.items():
        sheet.columns = sheet.columns.str.strip()

        fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]

        sheet = sheet.melt(
            id_vars=fixed_cols,
            var_name="Code",
            value_name="Target (Year)"
        )

        sheet["Target (Year)"] = pd.to_numeric(sheet["Target (Year)"], errors="coerce")
        sheet["Target (Unit)"] = sheet["Target (Year)"] / 12
        sheet["Target (Value)"] = sheet["Target (Unit)"] * sheet["Sales Price"]

        months = [
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ]

        df_long = sheet.loc[sheet.index.repeat(12)].copy()
        df_long["Month"] = months * len(sheet)

        df_long["Target (Value)"] = sheet["Target (Value)"].repeat(12).values

        all_data.append(df_long)

    return pd.concat(all_data, ignore_index=True)

targets = load_targets()
targets["Code"] = targets["Code"].astype(str).str.strip()
targets = targets[targets["Code"].isin(valid_reps)]

# =========================
# 📂 LOAD SALES
# =========================
sales = pd.read_excel("Sales.xlsx")
sales.columns = sales.columns.str.strip()

sales["Sales After Returns"] = pd.to_numeric(sales["Sales After Returns"], errors="coerce").fillna(0)
sales["Invoice Discounts"] = pd.to_numeric(sales["Invoice Discounts"], errors="coerce").fillna(0)

sales["Net Sales"] = sales["Sales After Returns"] - sales["Invoice Discounts"]

sales["Rep Code"] = sales["Rep Code"].astype(str).str.strip()
sales = sales[sales["Rep Code"].isin(valid_reps)]

sales["Month"] = sales["Month"].astype(str).str.strip()

# =========================
# 📆 TIME
# =========================
month_order = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

current_month = month_order[datetime.now().month - 1]
current_index = month_order.index(current_month)

# =========================
# 🎯 TARGET KPI
# =========================
yearly_target = targets["Target (Value)"].sum()

ytd_target = targets[targets["Month"].isin(month_order[:current_index+1])]["Target (Value)"].sum()

quarterly_target = targets[targets["Month"].isin(month_order[max(current_index-2,0):current_index+1])]["Target (Value)"].sum()

monthly_target = targets[targets["Month"] == current_month]["Target (Value)"].sum()

# =========================
# 💰 NET SALES KPI
# =========================
net_yearly = sales["Net Sales"].sum()

net_ytd = sales[sales["Month"].isin(month_order[:current_index+1])]["Net Sales"].sum()

net_quarterly = sales[sales["Month"].isin(month_order[max(current_index-2,0):current_index+1])]["Net Sales"].sum()

net_monthly = sales[sales["Month"] == current_month]["Net Sales"].sum()

# =========================
# 📊 KPI DISPLAY
# =========================
st.subheader("🎯 Targets vs 💰 Net Sales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📆 Yearly Target", f"{yearly_target:,.0f}")
    st.metric("💰 Net Sales Yearly", f"{net_yearly:,.0f}")

with col2:
    st.metric("⏳ YTD Target", f"{ytd_target:,.0f}")
    st.metric("💰 Net Sales YTD", f"{net_ytd:,.0f}")

with col3:
    st.metric("📊 Quarterly Target", f"{quarterly_target:,.0f}")
    st.metric("💰 Net Sales Quarterly", f"{net_quarterly:,.0f}")

with col4:
    st.metric("📅 Monthly Target", f"{monthly_target:,.0f}")
    st.metric("💰 Net Sales Monthly", f"{net_monthly:,.0f}")

# =========================
# 📋 DATA VIEW
# =========================
with st.expander("📄 View Targets"):
    st.dataframe(targets)

with st.expander("📄 View Sales"):
    st.dataframe(sales)
