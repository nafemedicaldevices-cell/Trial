import streamlit as st
import data_pipeline as dp

# =========================
# 🎨 PAGE SETUP
# =========================
st.set_page_config(layout="wide")

st.title("📊 Sales Performance Dashboard")
st.markdown("### 🚀 KPI System (Rep / Manager / Area / Supervisor / Evak)")


# =========================
# 📂 LOAD DATA
# =========================
data = dp.load_data()


# =========================
# ⚙️ BUILD PIPELINE
# =========================
rep = dp.build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
manager = dp.build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])
area = dp.build_target_pipeline(data["target_area"], "Area Code", data["mapping"])
supervisor = dp.build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"])
evak = dp.build_target_pipeline(data["target_evak"], "Evak Code", data["mapping"])


# =========================
# 📊 VALUE KPI SECTION
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
# 📦 PRODUCTS KPI SECTION
# =========================
st.header("📦 PRODUCTS KPI")

# 👨‍💼 REP
st.subheader("👨‍💼 Rep Products - Full Year 🏆")
st.dataframe(rep["products_full"], use_container_width=True)

st.subheader("👨‍💼 Rep Products - Month 📅")
st.dataframe(rep["products_month"], use_container_width=True)

st.subheader("👨‍💼 Rep Products - Quarter 📊")
st.dataframe(rep["products_quarter"], use_container_width=True)

st.subheader("👨‍💼 Rep Products - YTD 📈")
st.dataframe(rep["products_ytd"], use_container_width=True)


# 🏢 MANAGER
st.subheader("🏢 Manager Products - Full Year 🏆")
st.dataframe(manager["products_full"], use_container_width=True)

st.subheader("🏢 Manager Products - Month 📅")
st.dataframe(manager["products_month"], use_container_width=True)

st.subheader("🏢 Manager Products - Quarter 📊")
st.dataframe(manager["products_quarter"], use_container_width=True)

st.subheader("🏢 Manager Products - YTD 📈")
st.dataframe(manager["products_ytd"], use_container_width=True)


# 🌍 AREA
st.subheader("🌍 Area Products - Full Year 🏆")
st.dataframe(area["products_full"], use_container_width=True)

st.subheader("🌍 Area Products - Month 📅")
st.dataframe(area["products_month"], use_container_width=True)

st.subheader("🌍 Area Products - Quarter 📊")
st.dataframe(area["products_quarter"], use_container_width=True)

st.subheader("🌍 Area Products - YTD 📈")
st.dataframe(area["products_ytd"], use_container_width=True)


# 🧑‍💼 SUPERVISOR
st.subheader("🧑‍💼 Supervisor Products - Full Year 🏆")
st.dataframe(supervisor["products_full"], use_container_width=True)

st.subheader("🧑‍💼 Supervisor Products - Month 📅")
st.dataframe(supervisor["products_month"], use_container_width=True)

st.subheader("🧑‍💼 Supervisor Products - Quarter 📊")
st.dataframe(supervisor["products_quarter"], use_container_width=True)

st.subheader("🧑‍💼 Supervisor Products - YTD 📈")
st.dataframe(supervisor["products_ytd"], use_container_width=True)


# 🧬 EVAK
st.subheader("🧬 Evak Products - Full Year 🏆")
st.dataframe(evak["products_full"], use_container_width=True)

st.subheader("🧬 Evak Products - Month 📅")
st.dataframe(evak["products_month"], use_container_width=True)

st.subheader("🧬 Evak Products - Quarter 📊")
st.dataframe(evak["products_quarter"], use_container_width=True)

st.subheader("🧬 Evak Products - YTD 📈")
st.dataframe(evak["products_ytd"], use_container_width=True)
