import streamlit as st
import data_pipeline as dp

st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("📊 Sales Performance Dashboard")

# =========================
# LOAD DATA
# =========================
data = dp.load_data()

# =========================
# BUILD TARGETS 🔥
# =========================
rep = dp.build_target_pipeline(
    data["target_rep"], "Rep Code", data["mapping"]
)

manager = dp.build_target_pipeline(
    data["target_manager"], "Manager Code", data["mapping"]
)

area = dp.build_target_pipeline(
    data["target_area"], "Area Code", data["mapping"]
)

supervisor = dp.build_target_pipeline(
    data["target_supervisor"], "Supervisor Code", data["mapping"]
)

evak = dp.build_target_pipeline(
    data["target_evak"], "Evak Code", data["mapping"]
)

# =========================
# DISPLAY 📊
# =========================

st.subheader("👨‍💼 Rep Target")
st.dataframe(rep["value_all"])

st.subheader("🏢 Manager Target")
st.dataframe(manager["value_all"])

st.subheader("🌍 Area Target")
st.dataframe(area["value_all"])

st.subheader("🧑‍💼 Supervisor Target")
st.dataframe(supervisor["value_all"])

st.subheader("🧬 Evak Target")
st.dataframe(evak["value_all"])


# =========================
# PRODUCTS 🔥
# =========================
st.subheader("📦 Rep Products (YTD)")
st.dataframe(rep["products_uptodate"])
