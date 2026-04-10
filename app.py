import streamlit as st
import data_pipeline as dp

st.title("Dashboard")

data = dp.load_data()

rep_target = dp.build_target_pipeline(
    data["target_rep"],
    "Rep Code",
    data["mapping"]
)

st.write(rep_target["value_full"].head())
