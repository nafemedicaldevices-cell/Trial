import pandas as pd
import streamlit as st

st.title("📊 Target Dashboard - Final Stable Version")

# =========================
# 🧹 PROCESS
# =========================
def process_df(df):

    df.columns = df.columns.str.strip()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # -------- TARGET --------
    target_cols = [c for c in df.columns if "target" in c.lower()]

    if len(target_cols) == 0:
        return df

    target_col = target_cols[0]

    df[target_col] = pd.to_numeric(df[target_col], errors="coerce")

    df = df.rename(columns={target_col: "Target (Year)"})

    # =========================
    # 📅 MONTH TABLE (FIXED METHOD)
    # =========================
    months_df = pd.DataFrame({
        "Month": [
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ]
    })

    df["key"] = 1
    months_df["key"] = 1

    df_long = df.merge(months_df, on="key").drop("key", axis=1)

    df_long["Monthly Target"] = df_long["Target (Year)"] / 12

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

    if "Month" not in df.columns:
        st.error("Month column missing!")
        st.dataframe(df)
        continue

    # KPI
    c1, c2, c3 = st.columns(3)

    c1.metric("Year Target", f"{df['Target (Year)'].sum():,.0f}")

    c2.metric("Monthly Target", f"{df['Monthly Target'].sum():,.0f}")

    c3.metric("Rows", len(df))

    # TABLE
    st.dataframe(df, use_container_width=True)

    st.divider()
