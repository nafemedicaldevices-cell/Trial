import streamlit as st
import os

# =========================
# 🔍 CHECK FILES FIRST
# =========================
st.write("📂 Project Files:", os.listdir())

# =========================
# SAFE IMPORT
# =========================
try:
    import cleaning
except Exception as e:
    st.error("❌ Error importing cleaning.py")
    st.exception(e)
    st.stop()

# =========================
# LOAD DATA
# =========================
targets = cleaning.load_targets()
haraka = cleaning.load_haraka()

st.title("📊 KPI Dashboard")

# =========================
# TABS
# =========================
tab1, tab2 = st.tabs(["Targets", "Harakah"])

# =========================
# TARGETS
# =========================
with tab1:
    st.subheader("Targets")

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
