import streamlit as st
import data_loader as dl
import data_pipeline as dp

st.title("Sales Dashboard")

data = dl.load_data()

rep = dp.build_target_pipeline(
    data["target_rep"],
    "Rep Code",
    data["mapping"]
)

st.write(rep["value_full"].head())
