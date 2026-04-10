import streamlit as st
import data_pipeline as dp

st.set_page_config(layout="wide")

st.title("📊 Sales Performance Dashboard")


# =========================
# LOAD DATA
# =========================
data = dp.load_data()


# =========================
# BUILD PIPELINE
# =========================
rep = dp.build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
manager = dp.build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])
area = dp.build_target_pipeline(data["target_area"], "Area Code", data["mapping"])
supervisor = dp.build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"])
evak = dp.build_target_pipeline(data["target_evak"], "Evak Code", data["mapping"])


# =========================
# VALUE KPI
# =========================
st.header("📊 VALUE KPI")

st.subheader("Rep")
st.dataframe(rep["value_table"])

st.subheader("Manager")
st.dataframe(manager["value_table"])

st.subheader("Area")
st.dataframe(area["value_table"])

st.subheader("Supervisor")
st.dataframe(supervisor["value_table"])

st.subheader("Evak")
st.dataframe(evak["value_table"])


# =========================
# PRODUCTS KPI
# =========================
st.header("📦 PRODUCTS KPI")

st.subheader("Rep")
st.dataframe(rep["products_full"])
st.dataframe(rep["products_month"])
st.dataframe(rep["products_quarter"])
st.dataframe(rep["products_ytd"])

st.subheader("Manager")
st.dataframe(manager["products_full"])
st.dataframe(manager["products_month"])
st.dataframe(manager["products_quarter"])
st.dataframe(manager["products_ytd"])

st.subheader("Area")
st.dataframe(area["products_full"])
st.dataframe(area["products_month"])
st.dataframe(area["products_quarter"])
st.dataframe(area["products_ytd"])

st.subheader("Supervisor")
st.dataframe(supervisor["products_full"])
st.dataframe(supervisor["products_month"])
st.dataframe(supervisor["products_quarter"])
st.dataframe(supervisor["products_ytd"])

st.subheader("Evak")
st.dataframe(evak["products_full"])
st.dataframe(evak["products_month"])
st.dataframe(evak["products_quarter"])
st.dataframe(evak["products_ytd"])
