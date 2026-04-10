import streamlit as st
import pandas as pd

st.title("Overdue Step 1")

overdue = pd.read_excel("Overdue.xlsx")

st.subheader("📄 Raw Data")
st.dataframe(overdue)
