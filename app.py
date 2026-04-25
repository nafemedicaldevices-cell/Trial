import streamlit as st
import pandas as pd

# =========================
# 🎯 FILTERS (FROM CODE SHEET)
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
# 🔥 FILTER MASTER CODES
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
# 🎯 TARGET BASE
# =========================

target_rep = targets["Rep"].copy()
target_rep["Code"] = target_rep["Code"].astype(str).str.strip()

# فلترة التارجت حسب reps المختارة
target_rep = target_rep[target_rep["Code"].isin(valid_reps)]

# =========================
# 🗓️ PERIOD SETUP
# =========================

month_order = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

quarter_map = {
    "Q1": ["Jan","Feb","Mar"],
    "Q2": ["Apr","May","Jun"],
    "Q3": ["Jul","Aug","Sep"],
    "Q4": ["Oct","Nov","Dec"]
}

period_type = st.sidebar.selectbox(
    "Period",
    ["Monthly", "Quarterly", "YTD", "Full Year"]
)

selected_month = st.sidebar.selectbox("Month", month_order)
selected_quarter = st.sidebar.selectbox("Quarter", list(quarter_map.keys()))

# =========================
# 🎯 TARGET CALCULATION
# =========================

if period_type == "Monthly":

    target_value = target_rep[
        target_rep["Month"] == selected_month
    ]["Target (Value)"].sum()

elif period_type == "Quarterly":

    target_value = target_rep[
        target_rep["Month"].isin(quarter_map[selected_quarter])
    ]["Target (Value)"].sum()

elif period_type == "YTD":

    idx = month_order.index(selected_month) + 1
    months = month_order[:idx]

    target_value = target_rep[
        target_rep["Month"].isin(months)
    ]["Target (Value)"].sum()

else:

    target_value = target_rep["Target (Value)"].sum()
