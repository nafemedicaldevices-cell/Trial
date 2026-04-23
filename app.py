import pandas as pd
import streamlit as st

# =========================
# 📌 TITLE
# =========================
st.title("📊 Target Dashboard - Cleaned Data")

# =========================
# 🧹 CLEANING FUNCTION
# =========================
def clean_df(df):

    # إزالة مسافات من أسماء الأعمدة
    df.columns = df.columns.str.strip()

    # تنظيف النصوص
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # تحويل أي Target لأرقام
    for col in df.columns:
        if "target" in col.lower():
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

# =========================
# 📂 LOAD DATA
# =========================
@st.cache_data
def load_data():

    data = {
        "Rep": clean_df(pd.read_excel("Target Rep.xlsx")),
        "Manager": clean_df(pd.read_excel("Target Manager.xlsx")),
        "Area": clean_df(pd.read_excel("Target Area.xlsx")),
        "Supervisor": clean_df(pd.read_excel("Target Supervisor.xlsx")),
        "Evak": clean_df(pd.read_excel("Target Evak.xlsx")),
    }

    return data

data = load_data()

# =========================
# 📊 DISPLAY
# =========================
for level, df in data.items():

    st.markdown(f"## 📌 {level}")

    # =========================
    # 📊 KPI
    # =========================
    target_cols = [c for c in df.columns if "target" in c.lower()]

    if target_cols:
        col = target_cols[0]

        c1, c2, c3 = st.columns(3)

        c1.metric("Total Target", f"{df[col].sum():,.0f}")
        c2.metric("Avg Target", f"{df[col].mean():,.0f}")
        c3.metric("Rows", len(df))

    # =========================
    # 📋 TABLE
    # =========================
    st.dataframe(df, use_container_width=True)

    st.divider()
