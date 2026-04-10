import streamlit as st
import data_pipeline as dp

data = dp.load_data()

rep = dp.build_target_pipeline(
    data["target_rep"],
    "Rep Code",
    data["mapping"]
)

st.title("📊 Sales Dashboard - Rep Summary")


# =========================
# MERGE ALL KPIs IN ONE TABLE
# =========================
rep_summary = rep["value_full"].rename(
    columns={"Target (Value)": "Full Year"}
)

rep_summary = rep_summary.merge(
    rep["value_uptodate"].rename(columns={"Target (Value)": "Up To Date"}),
    on="Rep Code",
    how="left"
)

rep_summary = rep_summary.merge(
    rep["value_quarter"].rename(columns={"Target (Value)": "Quarter"}),
    on="Rep Code",
    how="left"
)

rep_summary = rep_summary.merge(
    rep["value_month"].rename(columns={"Target (Value)": "Month"}),
    on="Rep Code",
    how="left"
)


# =========================
# FINAL OUTPUT
# =========================
st.subheader("👤 Rep KPI Summary Table")

st.dataframe(rep_summary)
