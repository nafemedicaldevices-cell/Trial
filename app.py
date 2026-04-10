import streamlit as st
import data_pipeline as dp

data = dp.load_data()

st.title("📊 Sales Dashboard")


# =========================
# REP
# =========================
rep = dp.build_target_pipeline(
    data["target_rep"],
    "Rep Code",
    data["mapping"]
)

st.subheader("Rep KPI")
st.write(rep["value_full"])


# =========================
# MANAGER
# =========================
manager = dp.build_target_pipeline(
    data["target_manager"],
    "Manager Code",
    data["mapping"]
)

st.subheader("Manager KPI")
st.write(manager["value_full"])


# =========================
# AREA
# =========================
area = dp.build_target_pipeline(
    data["target_area"],
    "Area Code",
    data["mapping"]
)

st.subheader("Area KPI")
st.write(area["value_full"])


# =========================
# SUPERVISOR
# =========================
supervisor = dp.build_target_pipeline(
    data["target_supervisor"],
    "Supervisor Code",
    data["mapping"]
)

st.subheader("Supervisor KPI")
st.write(supervisor["value_full"])


# =========================
# EVAK
# =========================
evak = dp.build_target_pipeline(
    data["target_evak"],
    "Evak Code",
    data["mapping"]
)

st.subheader("Evak KPI")
st.write(evak["value_full"])
