import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🎯 TARGET FILES - CLEAN VIEW")

# =========================
# 📥 TARGET FILES
# =========================
files = {
    "target_rep": "Target Rep.xlsx",
    "target_manager": "Target Manager.xlsx",
    "target_area": "Target Area.xlsx",
    "target_supervisor": "Target Supervisor.xlsx",
    "target_evak": "Target Evak.xlsx",
}

data = {}

# =========================
# 📊 READ + CLEAN VIEW
# =========================
for name, file in files.items():

    st.subheader(f"🎯 {name}")

    try:
        df = pd.read_excel(file)
        data[name] = df

        # =========================
        # 🧠 SHOW BASIC INFO ONLY
        # =========================
        st.write("📌 Shape:", df.shape)

        # نفصل الأعمدة المهمة
        fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]
        target_cols = [c for c in df.columns if c not in fixed_cols]

        st.write("📦 Fixed Columns:")
        st.write(fixed_cols)

        st.write("🎯 Target Columns (Codes):")
        st.write(target_cols)

        st.write("👀 Sample Data:")
        st.dataframe(df.head())

        st.markdown("---")

    except Exception as e:
        st.error(f"❌ Error loading {name}")
        st.exception(e)


st.success("✅ Targets loaded and structured view ready")
