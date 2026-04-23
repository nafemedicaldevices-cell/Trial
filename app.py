import streamlit as st
from cleaning import load_and_process_data

st.title("📊 KPI Target System - Final Clean Structure")

final_df = load_and_process_data()

c1, c2, c3 = st.columns(3)

c1.metric("Year Target", f"{final_df['Target (Year)'].sum():,.0f}")
c2.metric("Total Unit", f"{final_df['Target (Unit)'].sum():,.0f}")
c3.metric("Total Value", f"{final_df['Target (Value)'].sum():,.0f}")

level = st.selectbox("Select Level", ["All"] + final_df["Level"].unique().tolist())

if level != "All":
    final_df = final_df[final_df["Level"] == level]

st.dataframe(final_df, use_container_width=True)
