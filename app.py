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
# CLEAN NAMES (DISPLAY ONLY)
# =========================
df["Rep Name"] = df.get("Old Rep Name", "Unknown")

# =========================
# FILTERS (NAMES ONLY)
# =========================
st.sidebar.header("🔎 Filters")

rep_list = ["All"] + sorted(df["Rep Name"].dropna().unique().tolist())
rep_filter = st.sidebar.selectbox("👤 Rep Name", rep_list)

# =========================
# APPLY FILTER USING CODE INTERNALLY
# =========================
filtered_df = df.copy()

if rep_filter != "All":
    # هنا الربط الحقيقي (بالكود لكن بدون ما المستخدم يشوفه)
    rep_codes = df[df["Rep Name"] == rep_filter]["Rep Code"].unique()
    filtered_df = filtered_df[filtered_df["Rep Code"].isin(rep_codes)]

# =========================
# PRODUCT FILTER (لو موجود)
# =========================
if "Product Name" in df.columns:
    product_list = ["All"] + sorted(df["Product Name"].dropna().astype(str).unique().tolist())
    product_filter = st.sidebar.selectbox("📦 Product Name", product_list)

    if product_filter != "All":
        filtered_df = filtered_df[filtered_df["Product Name"] == product_filter]

# =========================
# AREA FILTER (لو موجود)
# =========================
if "Area Name" in df.columns:
    area_list = ["All"] + sorted(df["Area Name"].dropna().astype(str).unique().tolist())
    area_filter = st.sidebar.selectbox("🌍 Area Name", area_list)

    if area_filter != "All":
        filtered_df = filtered_df[filtered_df["Area Name"] == area_filter]

# =========================
# SHOW
# =========================
st.dataframe(filtered_df, use_container_width=True)
