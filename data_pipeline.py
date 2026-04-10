import streamlit as st
import pandas as pd
import os

# =========================
# 📌 PAGE SETUP
# =========================
st.set_page_config(page_title="Overdue App", layout="wide")

st.title("📊 Overdue Dashboard")

# =========================
# 📂 CHECK FILES IN DIRECTORY
# =========================
st.subheader("📁 Files in Project Folder")
st.write(os.listdir())

# =========================
# 📥 LOAD DATA
# =========================
try:
    df = pd.read_excel("Overdue.xlsx")
    st.success("✅ File loaded successfully!")

    # =========================
    # 👀 SHOW DATA
    # =========================
    st.subheader("📄 Data Preview")
    st.dataframe(df)

    # =========================
    # 📊 BASIC INFO
    # =========================
    st.subheader("📊 Info")
    st.write("Rows:", df.shape[0])
    st.write("Columns:", df.shape[1])
    st.write("Columns Names:", df.columns.tolist())

except Exception as e:
    st.error("❌ Error loading file")
    st.exception(e)
