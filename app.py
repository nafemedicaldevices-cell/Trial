import streamlit as st
import data_pipeline as dp

st.set_page_config(layout="wide")
st.title("📊 Sales Dashboard")

data = dp.load_data()


# =========================
# BUILD ALL LEVELS 🚀
# =========================
rep = dp.build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
manager = dp.build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])
area = dp.build_target_pipeline(data["target_area"], "Area Code", data["mapping"])
supervisor = dp.build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"])
evak = dp.build_target_pipeline(data["target_evak"], "Evak Code", data["mapping"])


# =========================
# VALUE TABLE 📊
# =========================
st.header("VALUE KPI")

st.subheader("Rep")
st.dataframe(rep["value_table"])

st.subheader("Supervisor")
st.dataframe(supervisor["value_table"])

st.subheader("Area")
st.dataframe(area["value_table"])

st.subheader("Manager")
st.dataframe(manager["value_table"])

st.subheader("Evak")
st.dataframe(evak["value_table"])


# =========================
# PRODUCTS TABLE 📦
# =========================
st.header("PRODUCTS KPI")

st.subheader("Rep Products")
st.dataframe(rep["products_ytd"])

st.subheader("Supervisor Products")
st.dataframe(supervisor["products_ytd"])

st.subheader("Area Products")
st.dataframe(area["products_ytd"])

st.subheader("Manager Products")
st.dataframe(manager["products_ytd"])

st.subheader("Evak Products")
st.dataframe(evak["products_ytd"])
