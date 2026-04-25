import streamlit as st
import pandas as pd

from cleaning import (
    load_targets,
    load_haraka,
    load_overdue,
    load_client_haraka
)

st.set_page_config(layout="wide")

st.title("📊 Sales Dashboard")

# =========================
# 📂 LOAD DATA
# =========================
@st.cache_data
def load_all():

    targets = load_targets()
    rep_haraka = load_haraka()
    client_haraka = load_client_haraka()

    # codes من client
    codes_cols = [
        "Rep Code","Rep Name",
        "Supervisor Name",
        "Manager Name",
        "Area Name"
    ]

    codes = client_haraka[codes_cols].drop_duplicates()

    overdue = load_overdue("Overdue.xlsx", codes)

    return targets, rep_haraka, client_haraka, overdue


targets, rep_haraka, client_haraka, overdue = load_all()

# =========================
# 🎯 FILTERS
# =========================
st.sidebar.header("Filters")

rep_list = sorted(client_haraka["Rep Name"].dropna().unique())
manager_list = sorted(client_haraka["Manager Name"].dropna().unique())
area_list = sorted(client_haraka["Area Name"].dropna().unique())

rep_filter = st.sidebar.multiselect("Rep", rep_list)
manager_filter = st.sidebar.multiselect("Manager", manager_list)
area_filter = st.sidebar.multiselect("Area", area_list)

df = client_haraka.copy()

if rep_filter:
    df = df[df["Rep Name"].isin(rep_filter)]

if manager_filter:
    df = df[df["Manager Name"].isin(manager_filter)]

if area_filter:
    df = df[df["Area Name"].isin(area_filter)]

# =========================
# 📊 KPIs
# =========================
total_sales = df["Sales Value"].sum()
total_collection = df["Total Collection"].sum()
total_returns = df["Returns Value"].sum()

# overdue filtered
overdue_f = overdue.copy()

if rep_filter:
    overdue_f = overdue_f[overdue_f["Rep Name"].isin(rep_filter)]

total_overdue = overdue_f["Overdue"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Sales", f"{total_sales:,.0f}")
col2.metric("💵 Collection", f"{total_collection:,.0f}")
col3.metric("🔁 Returns", f"{total_returns:,.0f}")
col4.metric("⚠️ Overdue", f"{total_overdue:,.0f}")

# =========================
# 📈 SALES BY REP
# =========================
st.subheader("Sales by Rep")

sales_rep = (
    df.groupby("Rep Name")["Sales Value"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(sales_rep)

# =========================
# 📈 COLLECTION BY REP
# =========================
st.subheader("Collection by Rep")

collection_rep = (
    df.groupby("Rep Name")["Total Collection"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(collection_rep)

# =========================
# ⚠️ OVERDUE TABLE
# =========================
st.subheader("Overdue Details")

st.dataframe(
    overdue_f.sort_values("Overdue", ascending=False),
    use_container_width=True
)

# =========================
# 📋 CLIENT TABLE
# =========================
st.subheader("Client Details")

st.dataframe(df, use_container_width=True)
