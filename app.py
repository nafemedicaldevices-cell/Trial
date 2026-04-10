import streamlit as st
import data_pipeline as dp

data = dp.load_data()

rep = dp.build_target_pipeline(
    data["target_rep"],
    "Rep Code",
    data["mapping"]
)

st.write(rep["value_full"])
