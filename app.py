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
# CLEAN NAMES (IMPORTANT)
# =========================
df["Rep Name"] = df.get("Old Rep Name", df["Rep Code"])
df["Rep Name"] = df["Rep Name"].astype(str).str.strip()

df = df[df["Rep Name"].notna()]
df = df[df["Rep Name"] != "nan"]

# =========================import streamlit as st

from cleaning import load_targets, load_haraka, load_codes, build_sales_vs_target

st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("📊 Sales vs Target Dashboard")

# =========================
# LOAD DATA
# =========================
targets = load_targets()
sales = load_haraka()
codes = load_codes()

df = build_sales_vs_target(targets, sales, codes)

# =========================
# CLEAN NAMES
# =========================
df["Rep Name"] = df["Rep Name"].astype(str).str.strip()

# =========================
# FILTERS (FROM CODE FILE NAMES)
# =========================
st.sidebar.header("🔎 Filters")

rep_list = ["All"] + sorted(df["Rep Name"].dropna().unique().tolist())
rep_filter = st.sidebar.selectbox("👤 Rep Name", rep_list)

if "Area Name" in df.columns:
    area_list = ["All"] + sorted(df["Area Name"].dropna().unique().tolist())
    area_filter = st.sidebar.selectbox("🌍 Area Name", area_list)
else:
    area_filter = "All"

# =========================
# APPLY FILTERS (USING CODES INTERNALLY)
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
# FILTERS
# =========================
st.sidebar.header("🔎 Filters")

rep_list = sorted(df["Rep Name"].unique().tolist())
rep_filter = st.sidebar.selectbox("👤 Rep Name", ["All"] + rep_list)

# =========================
# APPLY FILTER (BY CODE INTERNALLY)
# =========================
filtered_df = df.copy()

if rep_filter != "All":
    codes = df[df["Rep Name"] == rep_filter]["Rep Code"].unique()
    filtered_df = filtered_df[filtered_df["Rep Code"].isin(codes)]

# =========================
# SHOW
# =========================
st.dataframe(filtered_df, use_container_width=True)
