import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📊 Sales vs Target Dashboard")

# =========================
# 📂 LOAD CODES
# =========================
codes = pd.read_excel("Code.xlsx")
codes.columns = codes.columns.str.strip()
codes["Rep Code"] = codes["Rep Code"].astype(str).str.strip()

# =========================
# 🎯 FILTERS (HIERARCHY)
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
targets["Code"] = targets["Code"].astype(str).str.strip()
targets = targets[targets["Code"].isin(valid_reps)]

# =========================
# 📂 LOAD SALES
# =========================
def load_sales():

    df = pd.read_excel("Sales.xlsx")
    df.columns = df.columns.str.strip()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    for col in ["Sales Value", "Returns Value", "Invoice Discounts"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Net Sales"] = (
        df["Sales Value"]
        - df["Returns Value"]
        - df["Invoice Discounts"]
    )

    df["Rep Code"] = df["Rep Code"].astype(str).str.strip()

    df = df[df["Rep Code"].isin(valid_reps)]

    return df


sales = load_sales()

# =========================
# 📆 TIME LOGIC
# =========================
month_order = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

current_month = datetime.now().month
current_index = current_month - 1

sales["Month"] = sales["Date"].dt.month

# =========================
# 🎯 TARGET KPIS
# =========================
yearly_target = targets["Target (Value)"].sum()

ytd_target = targets[
    targets["Month"].isin(month_order[:current_index + 1])
]["Target (Value)"].sum()

quarterly_target = targets[
    targets["Month"].isin(month_order[max(current_index-2,0):current_index+1])
]["Target (Value)"].sum()

monthly_target = targets[
    targets["Month"] == month_order[current_index]
]["Target (Value)"].sum()

# =========================
# 💰 SALES KPIS
# =========================
monthly_sales = sales[
    sales["Month"] == current_month
]["Net Sales"].sum()

ytd_sales = sales[
    sales["Month"] <= current_month
]["Net Sales"].sum()

yearly_sales = sales["Net Sales"].sum()

# =========================
# 📊 TARGET CARDS
# =========================
st.subheader("🎯 Targets")

c1, c2, c3, c4 = st.columns(4)

c1.metric("📆 Yearly Target", f"{yearly_target:,.0f}")
c2.metric("⏳ YTD Target", f"{ytd_target:,.0f}")
c3.metric("📊 Quarterly Target", f"{quarterly_target:,.0f}")
c4.metric("📅 Monthly Target", f"{monthly_target:,.0f}")

# =========================
# 📊 SALES CARDS
# =========================
st.subheader("💰 Sales (Net Sales)")

s1, s2, s3 = st.columns(3)

s1.metric("📅 Monthly Sales", f"{monthly_sales:,.0f}")
s2.metric("⏳ YTD Sales", f"{ytd_sales:,.0f}")
s3.metric("📆 Yearly Sales", f"{yearly_sales:,.0f}")
