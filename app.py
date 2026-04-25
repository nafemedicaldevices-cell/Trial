import streamlit as st

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
# FILTERS
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

# Sales Unit
kpi_table["Sales Unit"] = filtered_df["Sales Value"] / filtered_df["Sales Price"]

# Target Unit (للتأكيد)
kpi_table["Target Unit"] = filtered_df["Target (Unit)"]

# =========================
# FINAL FORMAT
# =========================
kpi_table = kpi_table[[
    "Product Name",
    "Target Unit",
    "Sales Unit",
    "Target (Value)",
    "Sales Value",
    "Achievement %",
]]

# =========================
# SHOW
# =========================
st.dataframe(kpi_table, use_container_width=True)
