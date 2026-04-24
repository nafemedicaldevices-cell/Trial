import streamlit as st
import pandas as pd

from cleaning import (
    load_targets,
    load_haraka,
    load_overdue,
    load_client_harakah
)

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("📊 Main Dashboard")

# =====================================================
# LOAD DATA
# =====================================================
targets = load_targets()
haraka = load_haraka()
overdue = load_overdue(pd.DataFrame())  # لو عندك codes مرريه هنا
client = load_client_harakah()

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Targets",
    "📈 Harakah",
    "⏳ Overdue",
    "👤 Client Harakah"
])

# ================= TARGETS =================
with tab1:
    st.dataframe(targets, use_container_width=True)

# ================= HARKAH =================
with tab2:
    st.dataframe(haraka, use_container_width=True)

# ================= OVERDUE =================
with tab3:
    st.dataframe(overdue, use_container_width=True)

# ================= CLIENT HARKAH =================
with tab4:
    st.dataframe(client, use_container_width=True)

    st.subheader("📊 KPIs")
    c1, c2, c3 = st.columns(3)

    c1.metric("Sales", client["Sales Value"].sum())
    c2.metric("Returns", client["Returns Value"].sum())
    c3.metric("Net", client["Sales Value"].sum() - client["Returns Value"].sum())
