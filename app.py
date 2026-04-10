import streamlit as st
import data_pipeline as dp

data = dp.load_data()

st.title("Test Load Data")

st.write(data["sales"].head())
