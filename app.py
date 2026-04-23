import pandas as pd
import streamlit as st

st.title("📊 Target Dashboard - All Levels")

# =========================
# 📂 LOAD ALL SHEETS
# =========================
@st.cache_data
def load_data():
    file = pd.ExcelFile("Target Rep.xlsx")

    df_list = []

    for sheet in file.sheet_names:
        df = pd.read_excel(file, sheet_name=sheet)

        # تنظيف اسم الشيت (مهم جدًا)
        level = sheet.strip().title()

        df["Level"] = level

        df_list.append(df)

    return pd.concat(df_list, ignore_index=True)

df = load_data()

# =========================
# 🔍 CHECK LEVELS
# =========================
st.write("📌 Levels Found:")
st.write(df["Level"].value_counts())

# =========================
# 🎛️ FILTERS
# =========================
levels = st.multiselect("Select Level", df["Level"].unique(), default=df["Level"].unique())

filtered_df = df[df["Level"].isin(levels)]

# =========================
# 📊 SHOW TABLE
# =========================
st.subheader("📋 Full Data (All Levels)")
st.dataframe(filtered_df, use_container_width=True)
