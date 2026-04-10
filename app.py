import streamlit as st
import pandas as pd
import data_pipeline as dp

# =========================
# TITLE
# =========================
st.title("📊 Sales Dashboard - Test Version")

# =========================
# LOAD DATA
# =========================
data = dp.load_data()

# =========================
# SHOW RAW DATA (STEP 1)
# =========================
st.subheader("📌 Raw Sales Data")
st.write(data["sales"].head())

# =========================
# TARGET PIPELINE (REP)
# =========================
st.subheader("🎯 Rep Target - Full Value")

mapping = data["mapping"]

rep = dp.build_target_pipeline(
    "Target Rep.xlsx",
    "Rep Code",
    mapping
)

st.write(rep["value_full"].head())

# =========================
# OPTIONAL DEBUG INFO
# =========================
st.subheader("📌 Data Shapes")

st.write("Sales shape:", data["sales"].shape)
st.write("Mapping shape:", data["mapping"].shape)
st.write("Codes shape:", data["codes"].shape)
