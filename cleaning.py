import streamlit as st
import cleaning as cd  # 👈 هنا التعديل الأساسي

st.title("📊 KPI Target System - Final Clean Structure")

# =========================
# 📂 LOAD DATA
# =========================
final_df = cd.load_and_process_data()  # 👈 استدعاء من الملف الصح

# =========================
# 📊 KPI
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("Year Target", f"{final_df['Target (Year)'].sum():,.0f}")
c2.metric("Total Unit", f"{final_df['Target (Unit)'].sum():,.0f}")
c3.metric("Total Value", f"{final_df['Target (Value)'].sum():,.0f}")

# =========================
# 📊 FILTER
# =========================
level = st.selectbox("Select Level", ["All"] + sorted(final_df["Level"].unique()))

if level != "All":
    final_df = final_df[final_df["Level"] == level]

# =========================
# 📊 OUTPUT
# =========================
st.dataframe(final_df, use_container_width=True)
