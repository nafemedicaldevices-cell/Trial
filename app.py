import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🎯 STEP 1 - TARGET FILES ONLY")

# =========================
# 📥 TARGET FILES ONLY
# =========================
target_files = {
    "target_rep": "Target Rep.xlsx",
    "target_manager": "Target Manager.xlsx",
    "target_area": "Target Area.xlsx",
    "target_supervisor": "Target Supervisor.xlsx",
    "target_evak": "Target Evak.xlsx",
}

data = {}

# =========================
# 📊 READ ONLY TARGETS
# =========================
for name, file in target_files.items():

    st.subheader(f"🎯 {name}")

    try:
        df = pd.read_excel(file)

        data[name] = df

        st.write("Shape:", df.shape)
        st.write("Columns:")
        st.write(list(df.columns))

        st.write("Preview:")
        st.dataframe(df.head())

        st.markdown("---")

    except Exception as e:
        st.error(f"❌ Error loading {name}")
        st.exception(e)


# =========================
# 🧠 SUMMARY
# =========================
st.success("✅ Target files loaded check completed")
st.write("Loaded targets:", list(data.keys()))
