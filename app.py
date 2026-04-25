import streamlit as st
import pandas as pd
import numpy as np

from cleaning import load_targets, load_haraka, load_codes, build_sales_vs_target

st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("📊 Sales KPI Dashboard")

# =========================
# LOAD DATA
# =========================
targets = load_targets()
sales = load_haraka()
codes = load_codes()

df = build_sales_vs_target(targets, sales, codes)

# =========================
# PRODUCT NAME
# =========================
df["Product Name"] = df.get("Old Product Name", "Unknown")
df["Product Name"] = df["Product Name"].astype(str).str.strip()

# =========================
# FILTER
# =========================
st.sidebar.header("🔎 Filters")

product_list = ["All"] + sorted(df["Product Name"].dropna().unique().tolist())
product_filter = st.sidebar.selectbox("📦 Product Name", product_list)

filtered_df = df.copy()

if product_filter != "All":
    filtered_df = filtered_df[filtered_df["Product Name"] == product_filter]

# =========================
# SAFE CALCULATIONS
# =========================
filtered_df["Target Unit"] = pd.to_numeric(filtered_df["Target (Unit)"], errors="coerce").fillna(0)
filtered_df["Target Value"] = pd.to_numeric(filtered_df["Target (Value)"], errors="coerce").fillna(0)
filtered_df["Sales Value"] = pd.to_numeric(filtered_df["Sales Value"], errors="coerce").fillna(0)

# Sales Unit (نفس قيمة البيع لو مفيش unit فعلي)
filtered_df["Sales Unit"] = filtered_df["Sales Value"]

# =========================
# ACHIEVEMENT %
# =========================
filtered_df["Achievement Unit %"] = np.where(
    filtered_df["Target Unit"] > 0,
    (filtered_df["Sales Unit"] / filtered_df["Target Unit"]) * 100,
    0
)

filtered_df["Achievement Value %"] = np.where(
    filtered_df["Target Value"] > 0,
    (filtered_df["Sales Value"] / filtered_df["Target Value"]) * 100,
    0
)

# =========================
# KPI TABLE
# =========================
kpi_table = filtered_df[[
    "Product Name",
    "Target Unit",
    "Sales Unit",
    "Target Value",
    "Sales Value",
    "Achievement Unit %",
    "Achievement Value %"
]]

# =========================
# SHOW
# =========================
st.dataframe(kpi_table, use_container_width=True)
