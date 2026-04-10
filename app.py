import streamlit as st
import pipeline as pl

# =========================
# 🎨 PAGE SETUP
# =========================
st.set_page_config(page_title="Overdue Dashboard", layout="wide")

st.title("📊 Overdue Dashboard")

# =========================
# 📥 LOAD + CLEAN
# =========================
df = pl.load_data("Overdue.xlsx")
df = pl.clean_data(df)

# =========================
# 📄 SHOW DATA
# =========================
st.subheader("📄 Cleaned Data")
st.dataframe(df)

# =========================
# 📊 BASIC INFO
# =========================
st.subheader("📊 Info")

st.write("Rows:", df.shape[0])
st.write("Columns:", df.shape[1])

st.write("Columns List:")
st.write(df.columns.tolist())
