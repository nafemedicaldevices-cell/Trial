import streamlit as st
import pandas as pd
import numpy as np

# =========================
# 📦 IMPORT YOUR FUNCTIONS
# =========================
# المفروض تكون في ملف cleaning.py أو نفس الملف
from cleaning import load_targets, load_haraka, load_client_haraka, load_overdue

# =========================
# ⚡ LOAD DATA (IMPORTANT FIX)
# =========================
@st.cache_data
def load_all_data():

    targets_dict = load_targets()

    sales_dict = load_client_haraka()  # أو sales function عندك

    codes_df = load_haraka()["cleaned_rep_haraka"]

    return targets_dict, sales_dict, codes_df


targets_dict, sales_dict, codes_df = load_all_data()

# =========================
# 🎛️ UI
# =========================
st.title("📊 Sales vs Target Dashboard")

# =========================
# FILTERS
# =========================
target_sheet = st.selectbox(
    "Select Target Sheet",
    list(targets_dict.keys())
)

selected_code = st.selectbox(
    "Select Rep Code",
    codes_df["Rep Code"].dropna().unique()
)

sales_sheet = st.selectbox(
    "Select Sales Sheet",
    list(sales_dict.keys())
)

# =========================
# GET DATA
# =========================
target_df = targets_dict[target_sheet]
sales_df = sales_dict[sales_sheet]

# =========================
# FILTER TARGET
# =========================
target_df = target_df.merge(
    codes_df,
    on="Code",
    how="left"
)

target_df = target_df[
    target_df["Rep Code"].astype(str).str.strip()
    == str(selected_code).strip()
]

# =========================
# FILTER SALES
# =========================
sales_df = sales_df[
    sales_df["Rep Code"].astype(str).str.strip()
    == str(selected_code).strip()
]

# =========================
# AGG SALES
# =========================
sales_agg = sales_df.groupby(
    "Product Name",
    as_index=False
).agg({
    "Sales Unit": "sum",
    "Sales Value": "sum"
})

# =========================
# AGG TARGET
# =========================
target_agg = target_df.groupby(
    "Old Product Name",
    as_index=False
).agg({
    "Target (Unit)": "sum",
    "Target (Value)": "sum"
})

# =========================
# MERGE
# =========================
df = target_agg.merge(
    sales_agg,
    left_on="Old Product Name",
    right_on="Product Name",
    how="left"
)

df = df.fillna(0)

# =========================
# ACHIEVEMENT %
# =========================
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

# =========================
# FINAL TABLE
# =========================
final_df = df[[
    "Old Product Name",
    "Target (Unit)",
    "Sales Unit",
    "Achievement Unit %",
    "Target (Value)",
    "Sales Value",
    "Achievement Value %"
]]

final_df.columns = [
    "Product Name",
    "Target Unit",
    "Sales Unit",
    "Achievement Unit %",
    "Target Value",
    "Sales Value",
    "Achievement Value %"
]

# =========================
# DISPLAY
# =========================
st.dataframe(final_df, use_container_width=True)
