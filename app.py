import streamlit as st
from linking import build_model

# =========================
# 📌 LOAD DATA
# =========================

model = build_model()
sales = model["sales"].copy()

# =========================
# 🎛 STREAMLIT SETUP
# =========================

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("📊 Sales Dashboard")

st.sidebar.header("🎛 Filters")

# =========================
# 🎯 FILTER OPTIONS
# =========================

def safe_list(col):
    if col in sales.columns:
        return ["All"] + sorted(sales[col].dropna().unique())
    return ["All"]

manager = st.sidebar.selectbox(
    "Manager",
    safe_list("Manager")
)

supervisor = st.sidebar.selectbox(
    "Supervisor",
    safe_list("Supervisor")
)

area = st.sidebar.selectbox(
    "Area",
    safe_list("Area")
)

company = st.sidebar.selectbox(
    "Company",
    safe_list("Company")
)

rep = st.sidebar.selectbox(
    "Rep Name",
    safe_list("Old Rep Name")
)

# =========================
# 🔗 APPLY FILTERS
# =========================

filtered = sales.copy()

if manager != "All":
    filtered = filtered[filtered["Manager"] == manager]

if supervisor != "All":
    filtered = filtered[filtered["Supervisor"] == supervisor]

if area != "All":
    filtered = filtered[filtered["Area"] == area]

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
# 📊 QUICK KPI
# =========================

if "Net Sales" in filtered.columns:
    st.metric("Net Sales", filtered["Net Sales"].sum())
