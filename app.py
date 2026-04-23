import pandas as pd
import streamlit as st

# =========================
# 📌 TITLE
# =========================
st.title("📊 Target Dashboard - Multi Files")

# =========================
# 📂 LOAD DATA (5 FILES)
# =========================
@st.cache_data
def load_data():

    data = {
        "Rep": pd.read_excel("Target Rep.xlsx"),
        "Manager": pd.read_excel("Target Manager.xlsx"),
        "Area": pd.read_excel("Target Area.xlsx"),
        "Supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "Evak": pd.read_excel("Target Evak.xlsx"),
    }

    return data

data = load_data()

# =========================
# 🔍 SHOW LOADED FILES
# =========================
st.success(f"Loaded {len(data)} Files")

# =========================
# 📊 DISPLAY EACH FILE
# =========================
for level, df in data.items():

    st.markdown(f"## 📌 {level}")

    st.dataframe(df, use_container_width=True)

    # =========================
    # 📊 SIMPLE KPI (لو فيه Target column)
    # =========================
    target_cols = [c for c in df.columns if "target" in c.lower()]

    if target_cols:
        col = target_cols[0]

        df[col] = pd.to_numeric(df[col], errors="coerce")

        c1, c2, c3 = st.columns(3)

        c1.metric("Total", f"{df[col].sum():,.0f}")
        c2.metric("Average", f"{df[col].mean():,.0f}")
        c3.metric("Rows", len(df))

    st.divider()
