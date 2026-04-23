import pandas as pd
import numpy as np
import streamlit as st

st.title("📊 Pivot to Long - Target System")

# =========================
# 📂 UPLOAD FILE
# =========================
file = st.file_uploader("Upload Excel File", type=["xlsx"])

if file:

    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()

    st.subheader("📌 Original Data")
    st.dataframe(df)

    # =========================
    # 📌 FIXED COLUMNS
    # =========================
    fixed_cols = [
        "Year",
        "Product Code",
        "Old Product Name",
        "Sales Price"
    ]

    # =========================
    # 🔄 UNPIVOT (PIVOT → LONG)
    # =========================
    df_long = df.melt(
        id_vars=fixed_cols,
        var_name="Code",
        value_name="Target (Year)"
    )

    # =========================
    # 🧹 CLEAN
    # =========================
    df_long["Target (Year)"] = pd.to_numeric(df_long["Target (Year)"], errors="coerce")

    # =========================
    # 📅 CALCULATIONS
    # =========================
    df_long["Target (Unit)"] = df_long["Target (Year)"] / 12
    df_long["Target (Value)"] = df_long["Target (Unit)"] * df_long["Sales Price"]

    # =========================
    # 📅 MONTH GENERATION
    # =========================
    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    df_final = df_long.loc[df_long.index.repeat(12)].copy()

    df_final["Month"] = np.tile(months, len(df_long))

    df_final["Monthly Target (Unit)"] = np.repeat(df_long["Target (Unit)"].values, 12)

    df_final["Monthly Target (Value)"] = np.repeat(df_long["Target (Value)"].values, 12) / 12

    # =========================
    # 📊 OUTPUT
    # =========================
    st.subheader("📌 Final Transformed Data")
    st.dataframe(df_final, use_container_width=True)

    # =========================
    # 📊 KPI
    # =========================
    c1, c2, c3 = st.columns(3)

    c1.metric("Year Target", f"{df_final['Target (Year)'].sum():,.0f}")
    c2.metric("Monthly Target", f"{df_final['Monthly Target (Unit)'].sum():,.0f}")
    c3.metric("Rows", len(df_final))
