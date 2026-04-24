import streamlit as st
import pandas as pd

# =========================
# 📥 LOAD CLEAN DATA
# =========================

sales = pd.read_excel("Sales.xlsx")
codes = pd.read_excel("Code.xlsx")

sales.columns = sales.columns.str.strip()
codes.columns = codes.columns.str.strip()

# =========================
# 🔗 MERGE FOR FILTERS
# =========================

sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

sales = sales.merge(codes, on="Rep Code", how="left")

# =========================
# 🎛 STREAMLIT
# =========================

st.title("📊 Sales Dashboard")

st.sidebar.header("🎛 Filters")


def options(col):
    if col in sales.columns:
        return ["All"] + sorted(sales[col].dropna().unique())
    return ["All"]


manager = st.sidebar.selectbox("Manager", options("Manager"))
area = st.sidebar.selectbox("Area", options("Area"))
supervisor = st.sidebar.selectbox("Supervisor", options("Supervisor"))
company = st.sidebar.selectbox("Company", options("Company"))
rep = st.sidebar.selectbox("Rep Name", options("Old Rep Name"))

# =========================
# 🔗 APPLY FILTERS
# =========================

df = sales.copy()

if manager != "All":
    df = df[df["Manager"] == manager]

if area != "All":
    df = df[df["Area"] == area]

if supervisor != "All":
    df = df[df["Supervisor"] == supervisor]

if company != "All":
    df = df[df["Company"] == company]

if rep != "All":
    df = df[df["Old Rep Name"] == rep]

# =========================
# 📊 OUTPUT
# =========================

st.dataframe(df, use_container_width=True)
