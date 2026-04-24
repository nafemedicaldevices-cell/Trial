import streamlit as st
from cleaning import load_targets, load_haraka, load_client_haraka

st.set_page_config(layout="wide")

# =========================
# 📊 TITLE
# =========================
st.title("📊 KPI + Harakah System")

# =========================
# ⚡ LOAD DATA
# =========================
@st.cache_data
def load_all():
    return load_targets(), load_haraka(), load_client_haraka()

targets, rep_haraka, client_haraka = load_all()

# =========================
# 📌 TABS
# =========================
tab1, tab2, tab3 = st.tabs([
    "Targets",
    "Rep Harakah",
    "Client Harakah"
])

# =========================
# 📊 TARGETS
# =========================
with tab1:
    st.dataframe(targets, use_container_width=True)

# =========================
# 📊 REP HARKA
# =========================
with tab2:
    st.subheader("Rep Harakah")
    st.dataframe(rep_haraka, use_container_width=True)

# =========================
# 📊 CLIENT HARKA
# =========================
with tab3:
    st.subheader("Client Harakah")
    st.dataframe(client_haraka, use_container_width=True)
