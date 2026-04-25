import streamlit as st
import pandas as pd
import numpy as np

from cleaning import (
    load_targets,
    load_haraka,
    load_overdue,
    load_client_haraka
)

st.set_page_config(page_title="Sales Dashboard", layout="wide")

# =========================
# LOAD DATA
# =========================
targets = load_targets()

rep_target = targets["Rep"]   # مثال
haraka = load_haraka()

# =========================
# CLEAN TARGET (REP LEVEL)
# =========================
rep_target = rep_target.rename(columns={
    "Code": "Rep Code",
    "Product Code": "Product Code",
    "Old Product Name": "Product Name"
})

rep_target["Rep Code"] = rep_target["Rep Code"].astype(str).str.strip()

# =========================
# LOAD SALES (FROM HARKA)
# =========================
sales = haraka.copy()

sales["Rep Code"] = sales["Rep Code"].astype(str).str.strip()

# إجمالي المبيعات (تعديل حسب منطقك)
sales_agg = sales.groupby("Rep Code", as_index=False).agg({
    "Sales Value": "sum"
})

# =========================
# MERGE TARGET + SALES
# =========================
df = rep_target.merge(
    sales_agg,
    on="Rep Code",
    how="left"
)

df["Sales Value"] = df["Sales Value"].fillna(0)

# =========================
# KPI CALCULATION
# =========================
df["Target Unit"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)

df["Sales Unit"] = df["Sales Value"] / df["Sales Price"].replace(0, np.nan)
df["Sales Unit"] = df["Sales Unit"].fillna(0)

df["Target Value"] = pd.to_numeric(df["Target (Value)"], errors="coerce").fillna(0)

df["Achievement % (Unit)"] = np.where(
    df["Target Unit"] > 0,
    (df["Sales Unit"] / df["Target Unit"]) * 100,
    0
)

df["Achievement % (Value)"] = np.where(
    df["Target Value"] > 0,
    (df["Sales Value"] / df["Target Value"]) * 100,
    0
)

# =========================
# FILTERS
# =========================
st.sidebar.header("Filters")

area = st.sidebar.selectbox(
    "Area",
    ["All"] + sorted(df.get("Area Name", pd.Series([])).dropna().unique().tolist())
)

rep = st.sidebar.selectbox(
    "Rep Code",
    ["All"] + sorted(df["Rep Code"].dropna().unique().tolist())
)

if area != "All":
    df = df[df["Area Name"] == area]

if rep != "All":
    df = df[df["Rep Code"] == rep]

# =========================
# FINAL TABLE
# =========================
final_table = df[[
    "Product Code",
    "Product Name",
    "Target Unit",
    "Achievement % (Unit)",
    "Sales Unit",
    "Target Value",
    "Sales Value",
    "Achievement % (Value)"
]].copy()

final_table = final_table.sort_values("Achievement % (Value)", ascending=False)

# =========================
# UI
# =========================
st.title("📊 Sales vs Target Dashboard")

st.dataframe(final_table, use_container_width=True)
