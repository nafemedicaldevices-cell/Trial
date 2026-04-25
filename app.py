import streamlit as st

from cleaning import load_targets, load_haraka, load_codes, build_sales_vs_target

st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("📊 Sales vs Target Dashboard")

# =========================
# LOAD DATA
# =========================
targets = load_targets()
sales = load_haraka()
codes = load_codes()

# =========================
# BUILD FINAL DF (IMPORTANT FIX)
# =========================
df = build_sales_vs_target(targets, sales, codes)

# =========================
# CLEAN NAMES
# =========================
df["Rep Name"] = df["Rep Name"].astype(str).str.strip()

# =========================
# FILTERS (NAMES FROM CODE FILE)
# =========================
st.sidebar.header("🔎 Filters")

# Rep Name filter
rep_list = ["All"] + sorted(df["Rep Name"].dropna().unique().tolist())
rep_filter = st.sidebar.selectbox("👤 Rep Name", rep_list)

# Area Name filter
if "Area Name" in df.columns:
    area_list = ["All"] + sorted(df["Area Name"].dropna().unique().tolist())
    area_filter = st.sidebar.selectbox("🌍 Area Name", area_list)
else:
    area_filter = "All"

# =========================
# APPLY FILTERS
# =========================
filtered_df = df.copy()

if rep_filter != "All":
    filtered_df = filtered_df[filtered_df["Rep Name"] == rep_filter]

if area_filter != "All":
    filtered_df = filtered_df[filtered_df["Area Name"] == area_filter]

# =========================
# SHOW TABLE
# =========================
st.dataframe(filtered_df, use_container_width=True)
