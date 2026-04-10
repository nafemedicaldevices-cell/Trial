import streamlit as st
import pandas as pd

st.title("Overdue App")

df = pd.read_excel("Overdue.xlsx")

st.dataframe(df)
