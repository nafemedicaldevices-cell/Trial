import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📂 STEP 1 - Read All Files (NO PROCESSING)")

# =========================
# 📥 FILES LIST
# =========================
files = {
    "sales": "Sales.xlsx",
    "overdue": "Overdue.xlsx",
    "opening": "Opening.xlsx",

    "target_rep": "Target Rep.xlsx",
    "target_manager": "Target Manager.xlsx",
    "target_area": "Target Area.xlsx",
    "target_supervisor": "Target Supervisor.xlsx",
    "target_evak": "Target Evak.xlsx",

    "mapping": "Mapping.xlsx",
    "codes": "Code.xlsx"
}

data = {}

# =========================
# 📊 READ ONLY (NO TRANSFORM)
# =========================
for name, file in files.items():

    st.subheader(f"📄 {name}")

    try:
        df = pd.read_excel(file)

        data[name] = df

        st.write("Shape:", df.shape)
        st.write("Columns:")
        st.write(list(df.columns))

        st.write("Sample:")
        st.dataframe(df.head())

        st.markdown("---")

    except Exception as e:
        st.error(f"❌ Failed to load {name}")
        st.exception(e)


# =========================
# 🧠 FINAL CHECK SUMMARY
# =========================
st.success("✅ All files read attempt finished")
st.write("Loaded files:", list(data.keys()))
