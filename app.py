import pandas as pd
import streamlit as st

st.title("📊 Target Dashboard")

# =========================
# 📂 LOAD ALL SHEETS
# =========================
@st.cache_data
def load_data():
    file = pd.ExcelFile("Target Rep.xlsx")

    sheets = {}

    for sheet in file.sheet_names:
        df = pd.read_excel(file, sheet_name=sheet)

        # تنظيف الاسم
        level = sheet.strip().title()

        sheets[level] = df

    return sheets

data = load_data()

# =========================
# 📌 DISPLAY EACH SHEET SEPARATELY
# =========================
for level, df in data.items():

    st.markdown(f"## 📌 {level} Target")   # 👈 العنوان فوق كل جدول

    st.dataframe(df, use_container_width=True)

    st.divider()
