import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🎯 TARGET DASHBOARD")

# =========================
# 📥 LOAD TARGET FILES
# =========================
files = {
    "Rep Target": "Target Rep.xlsx",
    "Manager Target": "Target Manager.xlsx",
    "Area Target": "Target Area.xlsx",
    "Supervisor Target": "Target Supervisor.xlsx",
    "Evak Target": "Target Evak.xlsx",
}

# =========================
# 📊 DISPLAY ONLY DATA (NO INFO)
# =========================
for name, file in files.items():

    try:
        df = pd.read_excel(file)

        st.subheader(f"🎯 {name}")

        # 👇 فقط عرض الجدول
        st.dataframe(df, use_container_width=True)

        st.markdown("---")

    except Exception as e:
        st.error(f"❌ Failed to load {name}")
