import streamlit as st
import pandas as pd

st.title("Overdue Cleaned Data")

df = pd.read_excel("Overdue.xlsx")

# =========================
# CLEANING بسيط
# =========================
df.columns = df.columns.str.strip()   # تنظيف أسماء الأعمدة
df = df.dropna(how="all")             # حذف الصفوف الفاضية بالكامل

# =========================
# عرض النتيجة
# =========================
st.subheader("📄 Cleaned Data")
st.dataframe(df)
