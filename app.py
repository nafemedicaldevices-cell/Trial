import streamlit as st
import pipeline as pl

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
st.subheader("📄 Data with Renamed Columns")
st.dataframe(df)

# =========================
# 📊 INFO
# =========================
st.write("Rows:", df.shape[0])
st.write("Columns:", df.shape[1])
st.write(df.columns.tolist())
