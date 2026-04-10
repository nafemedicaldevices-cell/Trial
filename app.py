import streamlit as st
import data_pipeline as dp

st.title("📊 Sales Dashboard")

# LOAD DATA
data = dp.load_data()

# BUILD TARGET
rep_target = dp.build_target_pipeline(
    data["target_rep"],
    "Rep Code",
    data["mapping"]
)

# SHOW RESULT
st.subheader("Rep Target Value")
st.write(rep_target["value_full"])
