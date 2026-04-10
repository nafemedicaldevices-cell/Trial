import streamlit as st
import data_pipeline as dp

# =========================
# 🎨 PAGE CONFIG
# =========================
st.set_page_config(layout="wide")

st.title("📊 Sales Performance Dashboard")
st.markdown("### 🚀 KPI System (Rep / Manager / Area / Supervisor / Evak)")


# =========================
# 📂 LOAD DATA
# =========================
data = dp.load_data()


# =========================
# ⚙️ PIPELINES
# =========================
rep = dp.build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
manager = dp.build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])
area = dp.build_target_pipeline(data["target_area"], "Area Code", data["mapping"])
supervisor = dp.build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"])
evak = dp.build_target_pipeline(data["target_evak"], "Evak Code", data["mapping"])


# =========================
# 📊 VALUE KPI
# =========================
st.header("📊 VALUE KPI")

st.subheader("👨‍💼 Rep")
st.dataframe(rep["value_table"], use_container_width=True)

st.subheader("🏢 Manager")
st.dataframe(manager["value_table"], use_container_width=True)

st.subheader("🌍 Area")
st.dataframe(area["value_table"], use_container_width=True)

st.subheader("🧑‍💼 Supervisor")
st.dataframe(supervisor["value_table"], use_container_width=True)

st.subheader("🧬 Evak")
st.dataframe(evak["value_table"], use_container_width=True)


# =========================
# 📦 PRODUCTS KPI
# =========================
st.header("📦 PRODUCTS KPI")

st.subheader("👨‍💼 Rep Products 🏆📅📊📈")
st.dataframe(rep["products_full"], use_container_width=True)
st.dataframe(rep["products_month"], use_container_width=True)
st.dataframe(rep["products_quarter"], use_container_width=True)
st.dataframe(rep["products_ytd"], use_container_width=True)

st.subheader("🏢 Manager Products 🏆📅📊📈")
st.dataframe(manager["products_full"], use_container_width=True)
st.dataframe(manager["products_month"], use_container_width=True)
st.dataframe(manager["products_quarter"], use_container_width=True)
st.dataframe(manager["products_ytd"], use_container_width=True)

st.subheader("🌍 Area Products 🏆📅📊📈")
st.dataframe(area["products_full"], use_container_width=True)
st.dataframe(area["products_month"], use_container_width=True)
st.dataframe(area["products_quarter"], use_container_width=True)
st.dataframe(area["products_ytd"], use_container_width=True)

st.subheader("🧑‍💼 Supervisor Products 🏆📅📊📈")
st.dataframe(supervisor["products_full"], use_container_width=True)
st.dataframe(supervisor["products_month"], use_container_width=True)
st.dataframe(supervisor["products_quarter"], use_container_width=True)
st.dataframe(supervisor["products_ytd"], use_container_width=True)

st.subheader("🧬 Evak Products 🏆📅📊📈")
st.dataframe(evak["products_full"], use_container_width=True)
st.dataframe(evak["products_month"], use_container_width=True)
st.dataframe(evak["products_quarter"], use_container_width=True)
st.dataframe(evak["products_ytd"], use_container_width=True)

