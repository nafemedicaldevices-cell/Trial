import streamlit as st
import pandas as pd
import numpy as np

st.title("📊 Dashboard")

st.write("APP IS RUNNING")

# =========================
# SAFE CHECKS
# =========================
if "sales" not in globals():
    st.error("Sales not loaded")
    st.stop()

if "codes" not in globals():
    st.error("Codes not loaded")
    st.stop()

if "targets" not in globals():
    st.error("Targets not loaded")
    st.stop()

# =========================
# FILTER
# =========================
level = st.selectbox("Level", list(targets.keys()))

selected_code = st.selectbox(
    "Select Code",
    codes["Rep Code"].dropna().unique()
)

st.write("Selected:", selected_code)

# =========================
# TARGET
# =========================
target_df = targets[level]

target_df = target_df.merge(codes, on="Code", how="left")

target_df = target_df[target_df["Rep Code"] == selected_code]

st.write("Target rows:", len(target_df))

# =========================
# SALES FILTER
# =========================
sales_filtered = sales[
    sales["Rep Code"].astype(str).str.strip() == str(selected_code).strip()
]

st.write("Sales rows:", len(sales_filtered))

# =========================
# IF EMPTY STOP DEBUG
# =========================
if target_df.empty and sales_filtered.empty:
    st.warning("No data for selected code")
    st.stop()

# =========================
# GROUP
# =========================
sales_agg = sales_filtered.groupby("Product Name", as_index=False).agg({
    "Sales Unit": "sum",
    "Sales Value": "sum"
})

target_agg = target_df.groupby("Old Product Name", as_index=False).agg({
    "Target (Unit)": "sum",
    "Target (Value)": "sum"
})

df = target_agg.merge(
    sales_agg,
    left_on="Old Product Name",
    right_on="Product Name",
    how="left"
)

df = df.fillna(0)

df["Achievement Unit %"] = np.where(
    df["Target (Unit)"] > 0,
    df["Sales Unit"] / df["Target (Unit)"],
    0
)

df["Achievement Value %"] = np.where(
    df["Target (Value)"] > 0,
    df["Sales Value"] / df["Target (Value)"],
    0
)

st.dataframe(df, use_container_width=True)
