import streamlit as st
from clean_data import load_and_clean

# =========================
# 📌 TITLE
# =========================
st.title("📊 KPI Target Dashboard")

# =========================
# 📂 LOAD DATA
# =========================
df = load_and_clean()

# =========================
# 📊 KPI
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("Year Target", f"{df['Target Year'].sum():,.0f}")
c2.metric("Unit Target", f"{df['Target Unit'].sum():,.0f}")
c3.metric("Value Target", f"{df['Target Value'].sum():,.0f}")

# =========================
# 📌 FILTER
# =========================
level = st.selectbox("Select Level", ["All"] + list(df["Level"].unique()))

if level != "All":
    df = df[df["Level"] == level]

# =========================
# 📊 TABLE
# =========================
st.dataframe(df, use_container_width=True)
