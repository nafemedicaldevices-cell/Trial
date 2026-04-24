import streamlit as st
import cleaning

st.set_page_config(layout="wide")

st.title("📊 KPI Dashboard")

# =========================
# LOAD DATA SAFELY
# =========================
targets = cleaning.load_targets()
haraka = cleaning.load_haraka()
sales = cleaning.load_sales()

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["Targets", "Harakah", "Sales"])

# =========================
# TARGETS
# =========================
with tab1:
    st.subheader("Targets")

    if targets.empty:
        st.warning("No Targets Found")
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

    if haraka.empty:
        st.warning("No Harakah Data")
    else:
        st.dataframe(haraka, use_container_width=True)

# =========================
# SALES
# =========================
with tab3:
    st.subheader("Sales")

    if sales.empty:
        st.warning("No Sales Data")
    else:
        st.dataframe(sales, use_container_width=True)
