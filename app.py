import pandas as pd
import numpy as np
import streamlit as st

st.title("📊 Target Dashboard - Monthly Correct Version")

# =========================
# 🧹 PROCESS FUNCTION
# =========================
def process_df(df):

    df.columns = df.columns.str.strip()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    target_cols = [c for c in df.columns if "target" in c.lower()]

    if len(target_cols) == 0:
        return df

    target_col = target_cols[0]

    df[target_col] = pd.to_numeric(df[target_col], errors="coerce")

    df = df.rename(columns={target_col: "Target (Year)"})

    # =========================
    # 📅 CALCULATION
    # =========================
    df["Target (Unit)"] = df["Target (Year)"] / 12
    df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

    # =========================
    # 📅 MONTH LONG FORMAT (FIXED)
    # =========================
    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    n = len(df)

    df_long = df.loc[df.index.repeat(12)].copy()

    # 🔥 FIXED MONTH ASSIGNMENT
    df_long["Month"] = np.tile(months, n)

    df_long["Monthly Target (Unit)"] = np.repeat(df["Target (Unit)"].values, 12)
    df_long["Monthly Target (Value)"] = np.repeat(df["Target (Value)"].values, 12) / 12

    return df_long

# =========================
# 📂 LOAD FILES
# =========================
@st.cache_data
def load_data():

    files = {
        "Rep": "Target Rep.xlsx",
        "Manager": "Target Manager.xlsx",
        "Area": "Target Area.xlsx",
        "Supervisor": "Target Supervisor.xlsx",
        "Evak": "Target Evak.xlsx",
    }

    data = {}

    for name, file in files.items():

        df = pd.read_excel(file)

        df = process_df(df)

        df["Level"] = name

        data[name] = df

    return data

data = load_data()

# =========================
# 📊 DISPLAY
# =========================
for level, df in data.items():

    st.markdown(f"## 📌 {level}")

    # SAFE CHECK
    if "Month" not in df.columns:
        st.error("Month column not created!")
        st.stop()

    # KPI
    c1, c2, c3 = st.columns(3)

    c1.metric("Year Target", f"{df['Target (Year)'].sum():,.0f}")
    c2.metric("Monthly Unit", f"{df['Monthly Target (Unit)'].sum():,.0f}" if "Monthly Target (Unit)" in df.columns else "N/A")
    c3.metric("Rows", len(df))

    # TABLE
    st.dataframe(df, use_container_width=True)

    st.divider()
