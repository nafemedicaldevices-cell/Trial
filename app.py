import pandas as pd
import streamlit as st

st.title("📊 Target Dashboard - Stable Monthly Version")

# =========================
# 🧹 PROCESS FUNCTION
# =========================
def process_df(df):

    # -------- CLEAN --------
    df.columns = df.columns.str.strip()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # -------- FIND TARGET --------
    target_cols = [c for c in df.columns if "target" in c.lower()]

    if len(target_cols) == 0:
        return df

    target_col = target_cols[0]

    df[target_col] = pd.to_numeric(df[target_col], errors="coerce")

    df = df.rename(columns={target_col: "Target (Year)"})

    # =========================
    # 📅 SAFE MONTH GENERATION
    # =========================
    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    # 🔥 build list of rows manually (guaranteed working)
    result = []

    for i in range(len(df)):

        base_row = df.iloc[i]

        monthly_value = base_row["Target (Year)"] / 12

        for m in months:

            new_row = base_row.copy()
            new_row["Month"] = m
            new_row["Monthly Target"] = monthly_value

            result.append(new_row)

    return pd.DataFrame(result)

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

    # safety check
    if "Month" not in df.columns:
        st.error("Month column not created")
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
