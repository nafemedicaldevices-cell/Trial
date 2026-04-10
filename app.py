import streamlit as st
import data_pipeline as dp

st.title("Target Dashboard")

# LOAD
data = dp.load_data()

# BUILD
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

# =========================
# SUMMARY
# =========================
st.subheader(f"{level} Target Summary")
st.dataframe(selected["final"])

# =========================
# PRODUCTS
# =========================
st.subheader(f"{level} Products")

st.write("Full Year")
st.dataframe(selected["products_full"])

st.write("Month")
st.dataframe(selected["products_month"])

st.write("Quarter")
st.dataframe(selected["products_quarter"])

st.write("YTD")
st.dataframe(selected["products_uptodate"])
