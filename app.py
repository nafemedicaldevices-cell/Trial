import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📊 Sales vs Target Dashboard")

# =========================
# 🔍 DEBUG FILE SYSTEM
# =========================
st.sidebar.subheader("🔍 Debug Info")
st.sidebar.write("📁 Current Folder:", os.getcwd())
st.sidebar.write("📂 Files:", os.listdir())

# =========================
# 📂 SAFE LOAD SALES
# =========================
@st.cache_data
def load_sales():

    file_path = "Sales.xlsx"

    if not os.path.exists(file_path):
        st.error("❌ Sales.xlsx not found in project folder")
        st.stop()

    sales = pd.read_excel(file_path)
    sales.columns = sales.columns.str.strip()

    st.sidebar.success("✅ Sales file loaded")

    # =========================
    # 🔥 FIND REP COLUMN
    # =========================
    rep_candidates = [
        "Rep Code", "RepCode", "Rep_Code",
        "Sales Rep Code", "مندوب"
    ]

    rep_col = None
    for c in rep_candidates:
        if c in sales.columns:
            rep_col = c
            break

    if rep_col is None:
        st.error(f"❌ Rep column not found: {sales.columns.tolist()}")
        st.stop()

    sales["Rep Code"] = sales[rep_col].astype(str).str.strip()

    # =========================
    # NUMERIC CLEANING
    # =========================
    for col in ["Sales Value", "Returns Value", "Invoice Discounts"]:
        if col not in sales.columns:
            sales[col] = 0
        else:
            sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    # =========================
    # NET SALES
    # =========================
    sales["Net Sales"] = (
        sales["Sales Value"]
        - sales["Returns Value"]
        - sales["Invoice Discounts"]
    )

    return sales


# =========================
# 📂 LOAD TARGETS
# =========================
@st.cache_data
def load_targets():

    file_path = "Target Rep.xlsx"

    if not os.path.exists(file_path):
        st.error("❌ Target file not found")
        st.stop()

    sheets = pd.read_excel(file_path, sheet_name=None)

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


# =========================
# 🚀 LOAD DATA
# =========================
sales = load_sales()
targets = load_targets()

# =========================
# 🔗 CLEAN KEYS
# =========================
sales["Rep Code"] = sales["Rep Code"].astype(str).str.strip()
targets["Code"] = targets["Code"].astype(str).str.strip()

# =========================
# 📊 NET SALES
# =========================
net_sales_df = sales.groupby("Rep Code", as_index=False)["Net Sales"].sum()

# =========================
# 🎯 TARGET
# =========================
target_df = targets.groupby("Code", as_index=False)["Target (Value)"].sum()

# =========================
# 🔗 MERGE
# =========================
comparison = target_df.merge(
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
# 📊 KPIs
# =========================
total_target = comparison["Target (Value)"].sum()
total_sales = comparison["Net Sales"].sum()

achievement = (total_sales / total_target * 100) if total_target else 0

col1, col2, col3 = st.columns(3)

col1.metric("🎯 Target", f"{total_target:,.0f}")
col2.metric("💰 Net Sales", f"{total_sales:,.0f}")
col3.metric("📈 Achievement %", f"{achievement:.2f}%")

# =========================
# 📊 TABLE
# =========================
st.subheader("📊 Rep Performance")

st.dataframe(
    comparison.sort_values("Achievement %", ascending=False),
    use_container_width=True
)
