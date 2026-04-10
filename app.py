import streamlit as st
import data_pipeline as dp


# =========================
# 🎨 CONFIG
# =========================
st.set_page_config(layout="wide")
st.title("📊 Sales Performance Dashboard")


# =========================
# 📥 LOAD DATA
# =========================
data = dp.load_data()


# =========================
# 🚀 PIPELINES
# =========================
sales = dp.build_sales_pipeline(
    data["sales"],
    data["mapping"],
    data["codes"]
)

rep_target = dp.build_target_pipeline(data["target_rep"], "Rep Code")
manager_target = dp.build_target_pipeline(data["target_manager"], "Manager Code")
area_target = dp.build_target_pipeline(data["target_area"], "Area Code")
supervisor_target = dp.build_target_pipeline(data["target_supervisor"], "Supervisor Code")


# =========================
# 🔗 MERGE SALES + TARGET
# =========================
rep = sales["rep_value"].merge(rep_target, on="Rep Code", how="left")
manager = sales["manager_value"].merge(manager_target, on="Manager Code", how="left")
area = sales["area_value"].merge(area_target, on="Area Code", how="left")
supervisor = sales["supervisor_value"].merge(supervisor_target, on="Supervisor Code", how="left")


# =========================
# 📊 ACHIEVEMENT
# =========================
def add_achievement(df, target_col):

    if target_col not in df.columns:
        df[target_col] = 0

    df[target_col] = df[target_col].fillna(0)

    df["Achievement %"] = 0

    mask = df[target_col] > 0

    df.loc[mask, "Achievement %"] = (
        df.loc[mask, "Total Sales Value"] / df.loc[mask, target_col]
    ) * 100

    return df


rep = add_achievement(rep, "Target Value")
manager = add_achievement(manager, "Target Value")
area = add_achievement(area, "Target Value")
supervisor = add_achievement(supervisor, "Target Value")


# =========================
# 📊 DASHBOARD
# =========================
st.header("🔥 SALES vs TARGET")

st.subheader("👨‍💼 Rep")
st.dataframe(rep, use_container_width=True)

st.subheader("🏢 Manager")
st.dataframe(manager, use_container_width=True)

st.subheader("🌍 Area")
st.dataframe(area, use_container_width=True)

st.subheader("🧑‍💼 Supervisor")
st.dataframe(supervisor, use_container_width=True)
