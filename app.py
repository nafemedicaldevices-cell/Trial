import streamlit as st

from cleaning import load_targets, load_haraka, load_sales

st.set_page_config(layout="wide")

st.title("📊 KPI Dashboard")

# =========================
# LOAD DATA
# =========================
targets = load_targets()
haraka = load_haraka()
sales = load_sales()

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["Targets", "Harakah", "Sales"])

# =========================
# TARGETS (5 LEVELS)
# =========================
with tab1:
    st.subheader("Targets")

    if targets.empty:
        st.error("❌ No Targets Loaded")
    else:
        for lvl in ["Rep","Manager","Area","Supervisor","Evak"]:
            st.markdown(f"### 📌 {lvl}")
            st.dataframe(
                targets[targets["Level"] == lvl],
                use_container_width=True
            )

# =========================
# HARKA
# =========================
with tab2:
    st.subheader("Harakah")
    st.dataframe(haraka, use_container_width=True)

# =========================
# SALES
# =========================
with tab3:
    st.subheader("Sales")
    st.dataframe(sales, use_container_width=True)
