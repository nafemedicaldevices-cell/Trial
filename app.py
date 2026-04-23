import pandas as pd
import streamlit as st

# =========================
# 📌 TITLE
# =========================
st.title("📊 Target Dashboard - Full ETL")

# =========================
# 🧹 CLEAN + UNPIVOT FUNCTION
# =========================
def process_df(df):

    # -------- CLEANING --------
    df.columns = df.columns.str.strip()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # -------- DETECT FIXED COLS --------
    fixed_cols = [c for c in df.columns if c.lower() in [
        "year", "product code", "old product name", "sales price"
    ]]

    # -------- DETECT TARGET COLUMNS (UNPIVOT) --------
    value_cols = [c for c in df.columns if c not in fixed_cols]

    # لو مفيش حاجة تتعمل لها unpivot
    if len(value_cols) == 0:
        return df

    df_melted = df.melt(
        id_vars=fixed_cols,
        value_vars=value_cols,
        var_name="Code",
        value_name="Target (Year)"
    )

    # -------- CLEAN NUMERIC --------
    df_melted["Target (Year)"] = pd.to_numeric(df_melted["Target (Year)"], errors="coerce")

    # -------- CALCULATIONS --------
    df_melted["Target (Unit)"] = df_melted["Target (Year)"] / 12

    if "Sales Price" in df_melted.columns:
        df_melted["Target (Value)"] = df_melted["Target (Unit)"] * df_melted["Sales Price"]

    return df_melted

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

    # ================= KPI =================
    num_cols = df.select_dtypes(include="number").columns

    if len(num_cols) > 0:

        target_col = num_cols[0]

        c1, c2, c3 = st.columns(3)

        c1.metric("Total Target", f"{df[target_col].sum():,.0f}")
        c2.metric("Avg Target", f"{df[target_col].mean():,.0f}")
        c3.metric("Rows", len(df))

    # ================= TABLE =================
    st.dataframe(df, use_container_width=True)

    st.divider()
