import pandas as pd
import streamlit as st

# =========================
# 📌 TITLE
# =========================
st.title("📊 Target Dashboard - Full Monthly Distribution")

# =========================
# 🧹 CLEAN + TRANSFORM FUNCTION
# =========================
def process_df(df):

    # -------- CLEAN COLUMNS --------
    df.columns = df.columns.str.strip()

    # -------- CLEAN TEXT --------
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # -------- FIND TARGET COLUMN --------
    target_cols = [c for c in df.columns if "target" in c.lower()]

    if len(target_cols) == 0:
        return df

    target_col = target_cols[0]

    # convert to numeric
    df[target_col] = pd.to_numeric(df[target_col], errors="coerce")

    # standard name
    df = df.rename(columns={target_col: "Target (Year)"})

    # =========================
    # 📅 MONTHLY DISTRIBUTION
    # =========================
    df["Target (Month)"] = df["Target (Year)"] / 12

    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    for m in months:
        df[m] = df["Target (Month)"]

    return df

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
# 📊 DISPLAY ALL LEVELS
# =========================
for level, df in data.items():

    st.markdown(f"## 📌 {level} Target")

    # ================= SAFE CHECK =================
    if "Target (Year)" not in df.columns:

        st.warning(f"⚠️ No Target column in {level}")
        st.dataframe(df, use_container_width=True)
        st.divider()
        continue

    # ================= KPI =================
    c1, c2, c3 = st.columns(3)

    c1.metric("Total Year Target", f"{df['Target (Year)'].sum():,.0f}")

    c2.metric("Monthly Target", f"{df['Target (Month)'].sum():,.0f}")

    c3.metric("Rows", len(df))

    # ================= SHOW TABLE =================
    st.dataframe(df, use_container_width=True)

    st.divider()
