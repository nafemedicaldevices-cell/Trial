import pandas as pd
import streamlit as st

# =========================
# 📌 TITLE
# =========================
st.title("📊 Target Dashboard - Monthly (Long Format)")

# =========================
# 🧹 CLEAN + TRANSFORM
# =========================
def process_df(df):

    # -------- CLEAN COLUMNS --------
    df.columns = df.columns.str.strip()

    # -------- CLEAN TEXT --------
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # -------- TARGET DETECTION --------
    target_cols = [c for c in df.columns if "target" in c.lower()]

    if len(target_cols) == 0:
        return df

    target_col = target_cols[0]

    df[target_col] = pd.to_numeric(df[target_col], errors="coerce")

    df = df.rename(columns={target_col: "Target (Year)"})

    # =========================
    # 📅 MONTHLY CALCULATION
    # =========================
    df["Target (Unit)"] = df["Target (Year)"] / 12
    df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

    # =========================
    # 📅 LONG FORMAT (MONTH COLUMN)
    # =========================
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    df_long = df.loc[df.index.repeat(12)].copy()

    df_long["Month"] = months * len(df)

    df_long["Monthly Target (Unit)"] = df["Target (Unit)"].repeat(12).values

    df_long["Monthly Target (Value)"] = df["Target (Value)"].repeat(12).values / 12

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

    st.markdown(f"## 📌 {level} Target")

    # ================= SAFE KPI =================
    c1, c2, c3 = st.columns(3)

    if "Target (Year)" in df.columns:
        c1.metric("Total Year Target", f"{df['Target (Year)'].sum():,.0f}")
    else:
        c1.metric("Total Year Target", "N/A")

    if "Monthly Target (Unit)" in df.columns:
        c2.metric("Monthly Unit Target", f"{df['Monthly Target (Unit)'].sum():,.0f}")
    else:
        c2.metric("Monthly Unit Target", "N/A")

    c3.metric("Rows", len(df))

    # ================= TABLE =================
    st.dataframe(df, use_container_width=True)

    st.divider()
