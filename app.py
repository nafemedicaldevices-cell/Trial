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
# CLEAN NAMES FROM CODE FILE
# =========================
df["Rep Name"] = df.get("Rep Name", df["Rep Code"])
df["Rep Name"] = df["Rep Name"].astype(str).str.strip()

df["Product Name"] = df.get("Old Product Name", "Unknown")
df["Product Name"] = df["Product Name"].astype(str).str.strip()

# =========================
# FILTERS (NAMES)
# =========================
st.sidebar.header("🔎 Filters")

# Rep Name filter
rep_list = ["All"] + sorted(df["Rep Name"].dropna().unique().tolist())
rep_filter = st.sidebar.selectbox("👤 Rep Name", rep_list)

# Product filter
product_list = ["All"] + sorted(df["Product Name"].dropna().unique().tolist())
product_filter = st.sidebar.selectbox("📦 Product Name", product_list)

# =========================
# APPLY FILTERS
# =========================
filtered_df = df.copy()

if rep_filter != "All":
    filtered_df = filtered_df[filtered_df["Rep Name"] == rep_filter]

if product_filter != "All":
    filtered_df = filtered_df[filtered_df["Product Name"] == product_filter]

# =========================
# SAFE NUMBERS
# =========================
filtered_df["Target Unit"] = pd.to_numeric(filtered_df["Target (Unit)"], errors="coerce").fillna(0)
filtered_df["Target Value"] = pd.to_numeric(filtered_df["Target (Value)"], errors="coerce").fillna(0)
filtered_df["Sales Value"] = pd.to_numeric(filtered_df["Sales Value"], errors="coerce").fillna(0)

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
    "Rep Name",
    "Target Unit",
    "Sales Unit",
    "Target Value",
    "Sales Value",
    "Achievement Unit %",
    "Achievement Value %"
]]

# =========================
# DISPLAY (WITH % FORMAT)
# =========================
st.dataframe(
    kpi_table.style.format({
        "Achievement Unit %": "{:.2f}%",
        "Achievement Value %": "{:.2f}%"
    }),
    use_container_width=True
)
