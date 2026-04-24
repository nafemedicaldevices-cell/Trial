import streamlit as st

from cleaning import (
    load_client_haraka,
    load_targets,
    load_haraka,
    load_overdue
)

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("📊 Sales Dashboard")

# =========================
# LOAD DATA
# =========================
client = load_client_haraka()
targets = load_targets()
haraka = load_haraka()
overdue = load_overdue()

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs([
    "Client",
    "Targets",
    "Haraka",
    "Overdue"
])

with tab1:
    st.dataframe(client, use_container_width=True)
    st.metric("Sales", f"{client['Sales Value'].sum():,.0f}")

with tab2:
    st.dataframe(targets, use_container_width=True)

with tab3:
    st.dataframe(haraka, use_container_width=True)

with tab4:
    st.dataframe(overdue, use_container_width=True)
    st.metric("Overdue", f"{overdue['Overdue'].sum():,.0f}")
