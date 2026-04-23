import pandas as pd
import streamlit as st

st.title("📊 Target Dashboard - Monthly Column Format")

# =========================
# 🧹 CLEAN + TRANSFORM
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
    # 📅 MONTHLY (LONG FORMAT)
    # =========================
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    df["Target (Month)"] = df["Target (Year)"] / 12

    # 🔥 تحويل من أعمدة إلى صفوف
    df_monthly = df.loc[df.index.repeat(12)].copy()

    df_monthly["Month"] = months * len(df)

    df_monthly["Monthly Target"] = df["Target (Month)"].repeat(12).values

    return df_monthly

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

    st.markdown(f"## 📌 {level} Monthly Target")

    # KPI
    c1, c2 = st.columns(2)

    c1.metric("Total Year Target", f"{df['Monthly Target'].sum() * 12:,.0f}")
    c2.metric("Monthly Target Total", f"{df['Monthly Target'].sum():,.0f}")

    # TABLE
    st.dataframe(df, use_container_width=True)

    st.divider()
    
