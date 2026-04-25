import streamlit as st
import pandas as pd
import os
import importlib

st.set_page_config(layout="wide")
st.title("📊 Sales vs Target Dashboard")

# =========================
# 🔍 DEBUG FILE SYSTEM
# =========================
st.sidebar.subheader("📁 Debug")

st.sidebar.write("Current Dir:", os.getcwd())
st.sidebar.write("Files:", os.listdir())

# =========================
# 🚀 SAFE IMPORT CLEANING
# =========================
try:
    import cleaning
    importlib.reload(cleaning)

    sales = cleaning.load_sales()
    targets = cleaning.load_targets()

except Exception as e:
    st.error("❌ Error loading cleaning module")
    st.exception(e)
    st.stop()

# =========================
# 🔗 CLEAN KEYS
# =========================
sales["Rep Code"] = sales["Rep Code"].astype(str).str.strip()
targets["Code"] = targets["Code"].astype(str).str.strip()

# =========================
# 📊 NET SALES
# =========================
net_sales = sales.groupby("Rep Code", as_index=False)["Net Sales"].sum()

# =========================
# 🎯 TARGET
# =========================
target_sum = targets.groupby("Code", as_index=False)["Target (Value)"].sum()

# =========================
# 🔗 MERGE
# =========================
df = target_sum.merge(
    net_sales,
    left_on="Code",
    right_on="Rep Code",
    how="left"
)

df["Net Sales"] = df["Net Sales"].fillna(0)

# =========================
# 📈 KPI %
# =========================
df["Achievement %"] = (
    df["Net Sales"] / df["Target (Value)"]
) * 100

df["Achievement %"] = df["Achievement %"].fillna(0)

# =========================
# 📊 KPIs
# =========================
total_target = df["Target (Value)"].sum()
total_sales = df["Net Sales"].sum()

achievement = (total_sales / total_target * 100) if total_target else 0

col1, col2, col3 = st.columns(3)

col1.metric("🎯 Target", f"{total_target:,.0f}")
col2.metric("💰 Net Sales", f"{total_sales:,.0f}")
col3.metric("📈 Achievement %", f"{achievement:.2f}%")

# =========================
# 📊 TABLE
# =========================
st.subheader("📊 Performance Table")

st.dataframe(
    df.sort_values("Achievement %", ascending=False),
    use_container_width=True
)
