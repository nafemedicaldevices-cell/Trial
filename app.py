import streamlit as st
import data_pipeline as dp

data = dp.load_data()

st.title("Test Load Data")

st.write(data["sales"].head())


import pandas as pd
import data_pipeline as dp

mapping = pd.read_excel("Mapping.xlsx")

rep = dp.build_target_pipeline("Target Rep.xlsx", "Rep Code", mapping)

print(rep["value_full"].head())
