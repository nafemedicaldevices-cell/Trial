import streamlit as st
import pandas as pd
from datetime import datetime

from cleaning import load_sales, load_targets

st.set_page_config(layout="wide")
st.title("📊 KPI Dashboard - Sales vs Target")

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
# 📈 ACHIEVEMENT %
# =========================
df["Achievement %"] = (
    df["Net Sales"] / df["Target (Value)"]
) * 100

df["Achievement %"] = df["Achievement %"].fillna(0)

# =========================
# 📊 GLOBAL KPIs
# =========================
total_target = df["Target (Value)"].sum()
total_sales = df["Net Sales"].sum()

achievement = (total_sales / total_target * 100) if total_target else 0

# =========================
# 📌 KPI CARDS
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("🎯 Total Target", f"{total_target:,.0f}")
col2.metric("💰 Net Sales", f"{total_sales:,.0f}")
col3.metric("📈 Achievement %", f"{achievement:.2f}%")

# =========================
# 🏆 TOP / BOTTOM
# =========================
st.subheader("🏆 Performance Ranking")

top = df.sort_values("Achievement %", ascending=False).head(10)
bottom = df.sort_values("Achievement %", ascending=True).head(10)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔥 Top 10 Reps")
    st.dataframe(top, use_container_width=True)

with col2:
    st.markdown("### ⚠️ Bottom 10 Reps")
    st.dataframe(bottom, use_container_width=True)

# =========================
# 📊 FULL TABLE
# =========================
st.subheader("📊 Full Performance Table")

st.dataframe(
    df.sort_values("Achievement %", ascending=False),
    use_container_width=True
)
