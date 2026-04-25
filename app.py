import streamlit as st
import pandas as pd

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
# CLEAN PRODUCT NAME
# =========================
df["Product Name"] = df.get("Old Product Name", "Unknown")
df["Product Name"] = df["Product Name"].astype(str).str.strip()

# =========================
# FILTERS (OPTIONAL)
# =========================
st.sidebar.header("🔎 Filters")

product_list = ["All"] + sorted(df["Product Name"].dropna().unique().tolist())
product_filter = st.sidebar.selectbox("📦 Product Name", product_list)

filtered_df = df.copy()

if product_filter != "All":
    filtered_df = filtered_df[filtered_df["Product Name"] == product_filter]

# =========================
# KPI TABLE
# =========================
kpi_table = filtered_df[[
    "Product Name",
    "Target (Unit)",
    "Sales Value",
    "Target (Value)",
    "Achievement %"
]].copy()

# Sales Unit (مشتقة)
kpi_table["Sales Unit"] = kpi_table["Sales Value"] / filtered_df["Sales Price"]

# ترتيب الأعمدة
kpi_table = kpi_table[[
    "Product Name",
    "Target (Unit)",
    "Sales Unit",
    "Target (Value)",
    "Sales Value",
    "Achievement %"
]]

# =========================
# SHOW
# =========================
st.dataframe(kpi_table, use_container_width=True)
