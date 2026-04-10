import streamlit as st
import data_pipeline as dp

st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("📊 Sales Performance Dashboard")


# =========================
# LOAD DATA 📂
# =========================
data = dp.load_data()


# =========================
# BUILD TARGETS 🚀
# =========================
rep = dp.build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
manager = dp.build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])
area = dp.build_target_pipeline(data["target_area"], "Area Code", data["mapping"])
supervisor = dp.build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"])
evak = dp.build_target_pipeline(data["target_evak"], "Evak Code", data["mapping"])


# =========================
# VALUE KPI 📊
# =========================
st.header("💰 VALUE KPI")

st.subheader("Rep")
st.dataframe(rep["value_uptodate"])

st.subheader("Manager")
st.dataframe(manager["value_uptodate"])

st.subheader("Area")
st.dataframe(area["value_uptodate"])

st.subheader("Supervisor")
st.dataframe(supervisor["value_uptodate"])

st.subheader("Evak")
st.dataframe(evak["value_uptodate"])


# =========================
# PRODUCTS KPI 📦🔥
# =========================
st.header("📦 PRODUCTS KPI")

st.subheader("Rep Products (YTD)")
st.dataframe(rep["products_uptodate"])

st.subheader("Manager Products (YTD)")
st.dataframe(manager["products_uptodate"])

st.subheader("Area Products (YTD)")
st.dataframe(area["products_uptodate"])

st.subheader("Supervisor Products (YTD)")
st.dataframe(supervisor["products_uptodate"])

st.subheader("Evak Products (YTD)")
st.dataframe(evak["products_uptodate"])
