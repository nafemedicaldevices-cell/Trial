import streamlit as st
from cleaning import load_targets, load_haraka, build_sales_vs_target

st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("📊 Sales Dashboard")

# =========================
# LOAD DATA
# =========================
targets = load_targets()
haraka = load_haraka()

rep_target = targets["Rep"]

df = build_sales_vs_target(rep_target, haraka)

# =========================
# SHOW TABLE
# =========================
st.dataframe(df, use_container_width=True)
