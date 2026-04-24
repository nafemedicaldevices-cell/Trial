import streamlit as st
import pandas as pd

from cleaning import load_targets, load_haraka, load_sales

st.set_page_config(layout="wide")

st.title("📊 KPI Dashboard")

# =========================
# LOAD DATA
# =========================
targets = load_targets()
haraka = load_haraka()

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["Targets", "Harakah", "Sales"])

# =========================
# TARGETS (5 SHEETS EFFECT)
# =========================
with tab1:
    st.subheader("Targets (All Levels)")

    if targets.empty:
        st.error("❌ No Targets Loaded - Check Excel Files")
    else:
        st.success("✅ Targets Loaded Successfully")

        # عرض كل Level لوحده (ده الحل اللي انت عايزه)
        levels = ["Rep", "Manager", "Area", "Supervisor", "Evak"]

        for lvl in levels:
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
# SALES (UPLOAD)
# =========================
with tab3:
    st.subheader("Sales Data")

    uploaded_file = st.file_uploader("📂 Upload Sales Excel", type=["xlsx"])

    if uploaded_file is not None:

        sales_df = pd.read_excel(uploaded_file)
        sales = load_sales(sales_df)

        st.success("✅ Sales Loaded")

        st.dataframe(sales, use_container_width=True)

    else:
        st.info("⬆️ Upload Sales file to display data")
