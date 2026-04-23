import streamlit as st
from cleaning import load_targets, load_haraka

# =========================
# 📊 TITLE
# =========================
st.title("📊 KPI + Harakah Dashboard")

# =========================
# 📥 LOAD DATA
# =========================
targets = load_targets()
haraka = load_haraka()

# =========================
# 📌 TABS (6 TABLES)
# =========================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Rep Target",
    "Manager Target",
    "Area Target",
    "Supervisor Target",
    "Evak Target",
    "Harakah"
])

# =========================
# 📊 TARGETS
# =========================
with tab1:
    st.subheader("Rep Target")
    st.dataframe(targets[targets["Level"] == "Rep"], use_container_width=True)

with tab2:
    st.subheader("Manager Target")
    st.dataframe(targets[targets["Level"] == "Manager"], use_container_width=True)

with tab3:
    st.subheader("Area Target")
    st.dataframe(targets[targets["Level"] == "Area"], use_container_width=True)

with tab4:
    st.subheader("Supervisor Target")
    st.dataframe(targets[targets["Level"] == "Supervisor"], use_container_width=True)

with tab5:
    st.subheader("Evak Target")
    st.dataframe(targets[targets["Level"] == "Evak"], use_container_width=True)

# =========================
# 📊 HARKA TABLE
# =========================
with tab6:
    st.subheader("Rep Harakah")
    st.dataframe(haraka, use_container_width=True)
