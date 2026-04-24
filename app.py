import streamlit as st
from cleaning import load_targets, load_haraka, load_client_haraka

st.set_page_config(layout="wide")

# =========================
# 📊 TITLE
# =========================
st.title("📊 KPI + Harakah System")

# =========================
# 📥 LOAD DATA
# =========================
@st.cache_data
def load_all_data():
    targets = load_targets()
    rep_haraka = load_haraka()
    client_haraka = load_client_haraka()
    return targets, rep_haraka, client_haraka

targets, rep_haraka, client_haraka = load_all_data()

# =========================
# 📌 TABS
# =========================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Rep Target",
    "Manager Target",
    "Area Target",
    "Supervisor Target",
    "Evak Target",
    "Rep Harakah",
    "Client Harakah"
])

# =========================
# 📊 TARGETS
# =========================
with tab1:
    st.dataframe(targets[targets["Level"] == "Rep"], use_container_width=True)

with tab2:
    st.dataframe(targets[targets["Level"] == "Manager"], use_container_width=True)

with tab3:
    st.dataframe(targets[targets["Level"] == "Area"], use_container_width=True)

with tab4:
    st.dataframe(targets[targets["Level"] == "Supervisor"], use_container_width=True)

with tab5:
    st.dataframe(targets[targets["Level"] == "Evak"], use_container_width=True)

# =========================
# 📊 REP HARKA
# =========================
with tab6:
    st.subheader("Rep Harakah")
    st.dataframe(rep_haraka, use_container_width=True)

# =========================
# 📊 CLIENT HARKA
# =========================
with tab7:
    st.subheader("Client Harakah")
    st.dataframe(client_haraka, use_container_width=True)
