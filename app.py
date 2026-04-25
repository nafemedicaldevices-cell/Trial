import streamlit as st
from cleaning import load_targets, load_haraka, build_sales_vs_target

st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("📊 Sales vs Target Dashboard")

# =========================
# LOAD DATA
# =========================
targets = load_targets()
sales = load_haraka()

df = build_sales_vs_target(targets, sales)

# =========================
# CLEAN
# =========================
df["Rep Name"] = df.get("Old Rep Name", df["Rep Code"])

# =========================
# FILTERS (NAMES)
# =========================
st.sidebar.header("🔎 Filters")

# Rep Name
rep_list = ["All"] + sorted(df["Rep Name"].dropna().astype(str).unique().tolist())
rep_filter = st.sidebar.selectbox("👤 Rep Name", rep_list)

# Product Name
if "Product Name" in df.columns:
    product_list = ["All"] + sorted(df["Product Name"].dropna().astype(str).unique().tolist())
    product_filter = st.sidebar.selectbox("📦 Product Name", product_list)
else:
    product_filter = "All"

# Area Name (لو موجود)
if "Area Name" in df.columns:
    area_list = ["All"] + sorted(df["Area Name"].dropna().astype(str).unique().tolist())
    area_filter = st.sidebar.selectbox("🌍 Area Name", area_list)
else:
    area_filter = "All"

# =========================
# APPLY FILTERS
# =========================
filtered_df = df.copy()

if rep_filter != "All":
    filtered_df = filtered_df[filtered_df["Rep Name"] == rep_filter]

if product_filter != "All":
    filtered_df = filtered_df[filtered_df["Product Name"] == product_filter]

if area_filter != "All":
    filtered_df = filtered_df[filtered_df["Area Name"] == area_filter]

# =========================
# SHOW
# =========================
st.dataframe(filtered_df, use_container_width=True)
