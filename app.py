import streamlit as st
import data_pipeline as dp

st.title("Target Dashboard")

# LOAD DATA
data = dp.load_data()

# BUILD ALL LEVELS
rep = dp.build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
manager = dp.build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])
area = dp.build_target_pipeline(data["target_area"], "Area Code", data["mapping"])
supervisor = dp.build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"])
evak = dp.build_target_pipeline(data["target_evak"], "Evak Code", data["mapping"])

# SELECT LEVEL
level = st.selectbox(
    "Choose Level",
    ["Rep", "Manager", "Area", "Supervisor", "Evak"]
)

data_map = {
    "Rep": rep,
    "Manager": manager,
    "Area": area,
    "Supervisor": supervisor,
    "Evak": evak
}

selected = data_map[level]

# DISPLAY
st.subheader(f"{level} Target Values")

st.write("Full Year")
st.dataframe(selected["value_full"])

st.write("Month")
st.dataframe(selected["value_month"])

st.write("Quarter")
st.dataframe(selected["value_quarter"])

st.write("Up To Date")
st.dataframe(selected["value_uptodate"])
