import pandas as pd
import numpy as np
import streamlit as st

st.title("📊 KPI Target System - Unit & Value")

# =========================
# 📂 FILES
# =========================
files = {
    "Rep": "Target Rep.xlsx",
    "Manager": "Target Manager.xlsx",
    "Area": "Target Area.xlsx",
    "Supervisor": "Target Supervisor.xlsx",
    "Evak": "Target Evak.xlsx",
}

all_data = []

# =========================
# 🔄 PROCESS FILES
# =========================
for level, file in files.items():

    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()

    fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]

    value_cols = [c for c in df.columns if c not in fixed_cols]

    # 🔄 UNPIVOT
    df = df.melt(
        id_vars=fixed_cols,
        var_name="Code",
        value_name="Target (Year)"
    )

    df["Level"] = level

    # 🧹 CLEAN
    df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")

    # =========================
    # 📊 CALCULATIONS
    # =========================
    df["Target Unit"] = df["Target (Year)"] / 12
    df["Target Value"] = df["Target Unit"] * df["Sales Price"]

    # =========================
    # 📅 MONTHS
    # =========================
    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    df_long = df.loc[df.index.repeat(12)].copy()

    df_long["Month"] = np.tile(months, len(df))

    df_long["Target Unit"] = np.repeat(df["Target Unit"].values, 12)

    df_long["Target Value"] = np.repeat(df["Target Value"].values, 12)

    all_data.append(df_long)

# =========================
# 📊 FINAL DATA
# =========================
final_df = pd.concat(all_data, ignore_index=True)

# =========================
# 📊 KPI
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("Year Target", f"{final_df['Target (Year)'].sum():,.0f}")
c2.metric("Total Unit", f"{final_df['Target Unit'].sum():,.0f}")
c3.metric("Total Value", f"{final_df['Target Value'].sum():,.0f}")

# =========================
# 📊 FILTER
# =========================
level = st.selectbox("Select Level", ["All"] + list(files.keys()))

if level != "All":
    final_df = final_df[final_df["Level"] == level]

# =========================
# 📊 TABLE
# =========================
st.dataframe(final_df, use_container_width=True)
