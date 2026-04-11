import streamlit as st
import pandas as pd

# LOAD DATA
opening = pd.read_excel("Opening.xlsx")
codes = pd.read_excel("Code.xlsx")
st.title("Opening Dashboard")

st.write("Data Preview 👇")
st.dataframe(opening.head())
