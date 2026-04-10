import streamlit as st
import data_pipeline as dp

data = dp.load_data()

st.title("📊 Sales KPI Dashboard")


# =========================
# FUNCTION TO BUILD SUMMARY
# =========================
def build_summary(df, id_col, mapping):

    base = dp.build_target_pipeline(df, id_col, mapping)

    summary = base["value_full"].rename(columns={"Target (Value)": "Full Year"})

    summary = summary.merge(
        base["value_uptodate"].rename(columns={"Target (Value)": "Up To Date"}),
        on=id_col,
        how="left"
    )

    summary = summary.merge(
        base["value_quarter"].rename(columns={"Target (Value)": "Quarter"}),
        on=id_col,
        how="left"
    )

    summary = summary.merge(
        base["value_month"].rename(columns={"Target (Value)": "Month"}),
        on=id_col,
        how="left"
    )

    return summary


# =========================
# REP
# =========================
st.subheader("👤 Rep")
rep_summary = build_summary(data["target_rep"], "Rep Code", data["mapping"])
st.dataframe(rep_summary)


# =========================
# MANAGER
# =========================
st.subheader("👔 Manager")
manager_summary = build_summary(data["target_manager"], "Manager Code", data["mapping"])
st.dataframe(manager_summary)


# =========================
# AREA
# =========================
st.subheader("🌍 Area")
area_summary = build_summary(data["target_area"], "Area Code", data["mapping"])
st.dataframe(area_summary)


# =========================
# SUPERVISOR
# =========================
st.subheader("🧑‍💼 Supervisor")
supervisor_summary = build_summary(data["target_supervisor"], "Supervisor Code", data["mapping"])
st.dataframe(supervisor_summary)


# =========================
# EVAK
# =========================
st.subheader("📦 Evak")
evak_summary = build_summary(data["target_evak"], "Evak Code", data["mapping"])
st.dataframe(evak_summary)
