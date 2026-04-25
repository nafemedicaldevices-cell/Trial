import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📊 Target Dashboard")

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
# 📂 LOAD TARGETS (FIXED)
# =========================
def load_targets():
    file = "Target Rep.xlsx"
    sheets = pd.read_excel(file, sheet_name=None)

    all_data = []

    for _, df in sheets.items():
        df.columns = df.columns.str.strip()

        fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]

        df = df.melt(
            id_vars=fixed_cols,
            var_name="Code",
            value_name="Target (Year)"
        )

        df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")
        df["Target (Unit)"] = df["Target (Year)"] / 12
        df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

        months = [
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ]

        df_long = df.loc[df.index.repeat(12)].copy()
        df_long["Month"] = months * len(df)

        df_long["Target (Value)"] = df["Target (Value)"].repeat(12).values

        all_data.append(df_long)

    return pd.concat(all_data, ignore_index=True)

targets = load_targets()

# =========================
# 🔎 FILTER TARGETS
# =========================
target_df = targets.copy()
target_df["Code"] = target_df["Code"].astype(str).str.strip()
target_df = target_df[target_df["Code"].isin(valid_reps)]

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
# 🎯 KPI CALCULATIONS
# =========================
yearly_target = target_df["Target (Value)"].sum()

ytd_target = target_df[
    target_df["Month"].isin(month_order[:current_index + 1])
]["Target (Value)"].sum()

quarterly_target = target_df[
    target_df["Month"].isin(month_order[max(current_index-2,0):current_index+1])
]["Target (Value)"].sum()

monthly_target = target_df[
    target_df["Month"] == current_month
]["Target (Value)"].sum()

# =========================
# 📊 KPI DISPLAY (FIXED UI)
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📆 Yearly Target", f"{yearly_target:,.0f}")

with col2:
    st.metric("⏳ YTD", f"{ytd_target:,.0f}")

with col3:
    st.metric("📊 Quarterly", f"{quarterly_target:,.0f}")

with col4:
    st.metric("📅 Monthly", f"{monthly_target:,.0f}")

# =========================
# 📋 DATA TABLE (optional view)
# =========================
with st.expander("📄 View Data"):
    st.dataframe(target_df)
