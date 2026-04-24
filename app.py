import streamlit as st
import pandas as pd
from linking import build_model

# =========================
# 📌 LOAD DATA
# =========================

model = build_model()
sales = model["sales"].copy()

# =========================
# 🧹 ENSURE CODE DATA EXISTS
# =========================

codes = pd.read_excel("Code.xlsx")
codes.columns = codes.columns.str.strip()

if "Manager" not in sales.columns:
    sales = sales.merge(codes, on="Rep Code", how="left")


# =========================
# 🎛 STREAMLIT SETUP
# =========================

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales Dashboard")


# =========================
# 🧠 SAFE OPTIONS FUNCTION
# =========================

def options(col):
    if col in sales.columns:
        return ["All"] + sorted(sales[col].dropna().unique())
    return ["All"]


# =========================
# 🎛 FILTERS
# =========================

st.sidebar.header("🎛 Filters")

manager = st.sidebar.selectbox("Manager", options("Manager"))
area = st.sidebar.selectbox("Area", options("Area"))
supervisor = st.sidebar.selectbox("Supervisor", options("Supervisor"))
company = st.sidebar.selectbox("Company", options("Company"))
rep = st.sidebar.selectbox("Rep Name", options("Old Rep Name"))


# =========================
# 🔗 APPLY FILTERS
# =========================

filtered = sales.copy()

if manager != "All":
    filtered = filtered[filtered["Manager"] == manager]

if area != "All":
    filtered = filtered[filtered["Area"] == area]

if supervisor != "All":
    filtered = filtered[filtered["Supervisor"] == supervisor]

if company != "All":
    filtered = filtered[filtered["Company"] == company]

if rep != "All":
    filtered = filtered[filtered["Old Rep Name"] == rep]


# =========================
# 📊 OUTPUT
# =========================

st.subheader("📌 Filtered Data")

st.dataframe(filtered, use_container_width=True)


# =========================
# 📊 KPI SIMPLE
# =========================

if "Net Sales" in filtered.columns:
    st.metric("Net Sales", filtered["Net Sales"].sum())
