import streamlit as st
import pipeline as pl

# =========================
# 🎨 PAGE
# =========================
st.title("📊 Overdue Dashboard")

# =========================
# 📥 LOAD + CLEAN
# =========================
df = pl.load_data()
df = pl.clean_data(df)

# =========================
# 📄 SHOW DATA
# =========================
st.subheader("📄 Cleaned Data")
st.dataframe(df)

# =========================
# 📊 QUICK INFO
# =========================
st.write("Rows:", df.shape[0])
st.write("Columns:", df.shape[1])
