import streamlit as st
from cleaning import load_targets, load_haraka, load_client_haraka

# =========================
# 📊 TITLE
# =========================
st.title("📊 KPI + Harakah System")

# =========================
# ⚡ CACHE DATA
# =========================
@st.cache_data
def get_data():
    targets = load_targets()
    rep_haraka = load_haraka()
    client_haraka = load_client_haraka()
    return targets, rep_haraka, client_haraka

targets, rep_haraka, client_haraka = get_data()

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
# 📊 TARGET FILTER
# =========================
def show_target(level):
    df = targets[targets["Level"] == level]
    st.dataframe(df, use_container_width=True)

# =========================
# 📊 TARGETS
# =========================
with tab1:
    show_target("Rep")

with tab2:
    show_target("Manager")

with tab3:
    show_target("Area")

with tab4:
    show_target("Supervisor")

with tab5:
    show_target("Evak")

# =========================
# 📊 REP HARKA
# =========================
with tab6:
    st.subheader("Rep Harakah")

    if rep_haraka is not None and not rep_haraka.empty:
        st.dataframe(rep_haraka, use_container_width=True)
    else:
        st.warning("No Rep Harakah data found")

# =========================
# 📊 CLIENT HARKA
# =========================
with tab7:
    st.subheader("Client Harakah")

    if client_haraka is not None and not client_haraka.empty:
        st.dataframe(client_haraka, use_container_width=True)
    else:
        st.warning("No Client Harakah data found")
