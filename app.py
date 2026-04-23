import pandas as pd
import streamlit as st

st.title("📊 Target System - 5 Levels")

# =========================
# 📂 LOAD ALL SHEETS
# =========================
@st.cache_data
def load_data():
    file = pd.ExcelFile("Target Rep.xlsx")

    sheets = {}

    for sheet in file.sheet_names:
        df = pd.read_excel(file, sheet_name=sheet)

        # تنظيف اسم الشيت
        level = sheet.strip().title()

        df["Level"] = level

        sheets[level] = df   # 👈 كل شيت لوحده

    return sheets

data = load_data()

# =========================
# 🧭 TABS لكل Level
# =========================
tabs = st.tabs(list(data.keys()))

for i, level in enumerate(data.keys()):
    with tabs[i]:

        df = data[level]

        st.subheader(f"📌 {level} Target Data")

        st.dataframe(df, use_container_width=True)

        # =========================
        # 📊 KPI لو فيه عمود Target
        # =========================
        target_cols = [c for c in df.columns if "target" in c.lower()]

        if target_cols:
            col = target_cols[0]

            df[col] = pd.to_numeric(df[col], errors="coerce")

            c1, c2 = st.columns(2)

            c1.metric("Total Target", f"{df[col].sum():,.0f}")
            c2.metric("Average Target", f"{df[col].mean():,.0f}")
