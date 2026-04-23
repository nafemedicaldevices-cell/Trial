import pandas as pd
import numpy as np
import streamlit as st

st.title("📊 Target Dashboard - Monthly Fixed Version")

# =========================
# 🧹 CLEAN + TRANSFORM
# =========================
def process_df(df):

    # -------- CLEAN --------
    df.columns = df.columns.str.strip()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # -------- TARGET DETECTION --------
    target_cols = [c for c in df.columns if "target" in c.lower()]

    if len(target_cols) == 0:
        return df

    target_col = target_cols[0]

    df[target_col] = pd.to_numeric(df[target_col], errors="coerce")

    df = df.rename(columns={target_col: "Target (Year)"})

    # -------- CALC --------
    df["Target (Unit)"] = df["Target (Year)"] / 12
    df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

    # =========================
    # 📅 MONTH CREATION (FIXED)
    # =========================
    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    n = len(df)

    if n == 0:
        return df

    # 🔥 SAFE LONG FORMAT BUILD
    df_expanded = pd.concat([df] * 12, ignore_index=True)

    df_expanded["Month"] = months * n

    df_expanded["Monthly Target (Unit)"] = df_expanded["Target (Unit)"] / 12
    df_expanded["Monthly Target (Value)"] = df_expanded["Target (Value)"] / 12

    return df_expanded

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

    # ================= SAFE CHECK =================
    if "Month" not in df.columns:
        st.error(f"Month column not created in {level}")
        st.dataframe(df)
        continue

    # ================= KPI =================
    c1, c2, c3 = st.columns(3)

    c1.metric("Year Target", f"{df['Target (Year)'].sum():,.0f}" if "Target (Year)" in df.columns else "N/A")

    c2.metric("Monthly Total", f"{df['Monthly Target (Unit)'].sum():,.0f}" if "Monthly Target (Unit)" in df.columns else "N/A")

    c3.metric("Rows", len(df))

    # ================= TABLE =================
    st.dataframe(df, use_container_width=True)

    st.divider()
