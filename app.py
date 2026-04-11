import streamlit as st
import pandas as pd
import numpy as np

# =========================
# 🎨 PAGE CONFIG (لازم أول سطر عرض)
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI Dashboard - SAFE VERSION")

st.write("🚀 App Started Successfully")


# =========================
# 📥 LOAD FILES SAFE
# =========================
def load_data():

    files = {
        "sales": "Sales.xlsx",
        "overdue": "Overdue.xlsx",
        "opening": "Opening.xlsx",
        "mapping": "Mapping.xlsx",
        "codes": "Code.xlsx",
        "target_rep": "Target Rep.xlsx",
        "target_manager": "Target Manager.xlsx",
        "target_area": "Target Area.xlsx",
        "target_supervisor": "Target Supervisor.xlsx",
        "target_evak": "Target Evak.xlsx",
    }

    data = {}

    for name, file in files.items():
        try:
            df = pd.read_excel(file)

            st.subheader(f"📄 {name}")
            st.write("Shape:", df.shape)
            st.write(list(df.columns))
            st.dataframe(df.head())

            data[name] = df

        except Exception as e:
            st.error(f"❌ Error loading {name}")
            st.exception(e)

    return data


# =========================
# 🚀 LOAD DATA
# =========================
data = load_data()


# =========================
# 🧪 STOP IF SALES MISSING
# =========================
if "sales" not in data:
    st.error("❌ Sales file not loaded - stopping app")
    st.stop()


# =========================
# 💰 SIMPLE SALES CHECK (NO CRASH)
# =========================
st.header("💰 Sales Quick Check")

sales = data["sales"].copy()
sales.columns = sales.columns.astype(str)

st.write("Sales Shape:", sales.shape)
st.dataframe(sales.head())


# =========================
# ⚠️ OVERDUE CHECK
# =========================
if "overdue" in data:
    st.header("⚠️ Overdue Quick Check")

    overdue = data["overdue"].copy()
    st.write(overdue.shape)
    st.dataframe(overdue.head())


# =========================
# 🏦 OPENING CHECK
# =========================
if "opening" in data:
    st.header("🏦 Opening Quick Check")

    opening = data["opening"].copy()
    st.write(opening.shape)
    st.dataframe(opening.head())


# =========================
# 🎯 TARGET CHECK
# =========================
target_keys = ["target_rep","target_manager","target_area","target_supervisor","target_evak"]

st.header("🎯 Targets Check")

for k in target_keys:
    if k in data:
        st.subheader(k)
        st.write(data[k].shape)
        st.dataframe(data[k].head())
