import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Target Dashboard")

# =========================
# 📂 LOAD CODES
# =========================
codes = pd.read_excel("Code.xlsx")
codes.columns = codes.columns.str.strip()
codes["Rep Code"] = codes["Rep Code"].astype(str).str.strip()

# =========================
# 🎯 HIERARCHY FILTERS ONLY
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

    FILES = {
        "Rep": "Target Rep.xlsx"
    }

    all_data = []

    for _, file in FILES.items():

        sheets = pd.read_excel(file, sheet_name=None)

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

target_df = targets.copy()
target_df["Code"] = target_df["Code"].astype(str).str.strip()

target_df = target_df[target_df["Code"].isin(valid_reps)]

# =========================
# 📆 MONTH LOGIC (AUTO ONLY)
# =========================
month_order = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

# =========================
# 🎯 CALCULATIONS (AUTO)
# =========================

monthly_target = target_df[target_df["Month"] == month_order[-1]]["Target (Value)"].sum()

quarterly_target = target_df[
    target_df["Month"].isin(month_order[-3:])
]["Target (Value)"].sum()

ytd_target = target_df[
    target_df["Month"].isin(month_order)
]["Target (Value)"].sum()

yearly_target = target_df["Target (Value)"].sum()

# =========================
# 📊 KPI CARDS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("📅 Monthly Target", f"{monthly_target:,.0f}")
col2.metric("📊 Quarterly Target", f"{quarterly_target:,.0f}")
col3.metric("⏳ YTD Target", f"{ytd_target:,.0f}")
col4.metric("📆 Yearly Target", f"{yearly_target:,.0f}")
