import streamlit as st

from cleaning import load_targets, load_haraka, build_sales_vs_target

st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("📊 Sales vs Target Dashboard")

# =========================
# LOAD DATA
# =========================
targets = load_targets()
sales = load_haraka()

# =========================
# BUILD TABLE
# =========================
df = build_sales_vs_target(targets, sales)

# =========================
# SHOW
# =========================
st.dataframe(df, use_container_width=True)
