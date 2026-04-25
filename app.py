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
# CLEAN FOR FILTERS
# =========================
df["Rep Code"] = df["Rep Code"].astype(str)

# =========================
# FILTERS
# =========================
st.sidebar.header("🔎 Filters")

# Rep Filter
rep_list = ["All"] + sorted(df["Rep Code"].dropna().unique().tolist())
rep_filter = st.sidebar.selectbox("Rep Code", rep_list)

# Product Filter (لو موجود)
if "Product Code" in df.columns:
    product_list = ["All"] + sorted(df["Product Code"].dropna().unique().tolist())
    product_filter = st.sidebar.selectbox("Product Code", product_list)
else:
    product_filter = "All"

# =========================
# APPLY FILTERS
# =========================
filtered_df = df.copy()

if rep_filter != "All":
    filtered_df = filtered_df[filtered_df["Rep Code"] == rep_filter]

if product_filter != "All" and "Product Code" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Product Code"] == product_filter]

# =========================
# SHOW TABLE
# =========================
st.dataframe(filtered_df, use_container_width=True)
