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
# 🔄 FILTER RESET
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

    FILES = {"Rep": "Target Rep.xlsx"}
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
# 📂 LOAD SALES (MAIN INVOICE DATA)
# =========================
def load_sales():

    sales = pd.read_excel("Sales.xlsx")
    sales.columns = sales.columns.str.strip()

    # تنظيف
    sales["Rep Code"] = sales["Rep Code"].astype(str).str.strip()

    for col in ["Sales Value", "Returns Value"]:
        sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    if "Invoice Discounts" not in sales.columns:
        sales["Invoice Discounts"] = 0
    else:
        sales["Invoice Discounts"] = pd.to_numeric(
            sales["Invoice Discounts"], errors="coerce"
        ).fillna(0)

    # =========================
    # 💰 NET SALES
    # =========================
    sales["Net Sales"] = (
        sales["Sales Value"]
        - sales["Returns Value"]
        - sales["Invoice Discounts"]
    )

    return sales


sales = load_sales()

# =========================
# 📊 NET SALES AGGREGATION
# =========================
net_sales_df = sales.groupby("Rep Code", as_index=False)["Net Sales"].sum()

# =========================
# 🎯 TARGET AGGREGATION
# =========================
target_sum = target_df.groupby("Code", as_index=False)["Target (Value)"].sum()

# =========================
# 🔗 MERGE
# =========================
comparison = target_sum.merge(
    net_sales_df,
    left_on="Code",
    right_on="Rep Code",
    how="left"
)

comparison["Net Sales"] = comparison["Net Sales"].fillna(0)

# =========================
# 📈 ACHIEVEMENT %
# =========================
comparison["Achievement %"] = (
    comparison["Net Sales"] / comparison["Target (Value)"]
) * 100

comparison["Achievement %"] = comparison["Achievement %"].fillna(0)

# =========================
# 📆 TIME KPIs
# =========================
month_order = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

current_month = month_order[datetime.now().month - 1]
current_index = month_order.index(current_month)

yearly_target = target_df["Target (Value)"].sum()

ytd_target = target_df[
    target_df["Month"].isin(month_order[:current_index + 1])
]["Target (Value)"].sum()

monthly_target = target_df[
    target_df["Month"] == current_month
]["Target (Value)"].sum()

total_net_sales = comparison["Net Sales"].sum()

achievement = (
    total_net_sales / yearly_target * 100
    if yearly_target else 0
)

# =========================
# 📊 KPI CARDS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("🎯 Yearly Target", f"{yearly_target:,.0f}")
col2.metric("💰 Net Sales", f"{total_net_sales:,.0f}")
col3.metric("⏳ YTD Target", f"{ytd_target:,.0f}")
col4.metric("📈 Achievement %", f"{achievement:.2f}%")

# =========================
# 📊 TABLE
# =========================
st.subheader("📊 Rep Performance")

st.dataframe(
    comparison.sort_values("Achievement %", ascending=False),
    use_container_width=True
)
