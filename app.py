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

    # 🔥 MASTER CODES
    codes = pd.read_excel("Code.xlsx")
    codes.columns = codes.columns.str.strip()
    codes["Rep Code"] = codes["Rep Code"].astype(str).str.strip()

    overdue = load_overdue("Overdue.xlsx", codes)

    return targets, rep_haraka, client_haraka, overdue, codes


targets, rep_haraka, client_haraka, overdue, codes = load_all()

# =========================
# 🎯 FILTERS (FROM CODES)
# =========================
st.sidebar.header("Filters")

rep_list = sorted(codes["Rep Name"].dropna().unique())
sup_list = sorted(codes["Supervisor Name"].dropna().unique())
manager_list = sorted(codes["Manager Name"].dropna().unique())
area_list = sorted(codes["Area Name"].dropna().unique())

rep_filter = st.sidebar.multiselect("Rep", rep_list)
sup_filter = st.sidebar.multiselect("Supervisor", sup_list)
manager_filter = st.sidebar.multiselect("Manager", manager_list)
area_filter = st.sidebar.multiselect("Area", area_list)

# =========================
# 🔥 FILTER CODES FIRST
# =========================
filtered_codes = codes.copy()

if rep_filter:
    filtered_codes = filtered_codes[filtered_codes["Rep Name"].isin(rep_filter)]

if sup_filter:
    filtered_codes = filtered_codes[filtered_codes["Supervisor Name"].isin(sup_filter)]

if manager_filter:
    filtered_codes = filtered_codes[filtered_codes["Manager Name"].isin(manager_filter)]

if area_filter:
    filtered_codes = filtered_codes[filtered_codes["Area Name"].isin(area_filter)]

valid_reps = filtered_codes["Rep Code"].unique()

# =========================
# 🔗 APPLY FILTERS TO DATA
# =========================
client_haraka_f = client_haraka[
    client_haraka["Rep Code"].isin(valid_reps)
]

rep_haraka_f = rep_haraka[
    rep_haraka["Rep Code"].isin(valid_reps)
]

overdue_f = overdue[
    overdue["Rep Code"].isin(valid_reps)
]

# =========================
# 📊 KPIs
# =========================
total_sales = client_haraka_f["Sales Value"].sum()
total_collection = client_haraka_f["Total Collection"].sum()
total_returns = client_haraka_f["Returns Value"].sum()
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
    client_haraka_f
    .groupby("Rep Name")["Sales Value"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(sales_rep)

# =========================
# 📈 COLLECTION BY REP
# =========================
st.subheader("Collection by Rep")

collection_rep = (
    client_haraka_f
    .groupby("Rep Name")["Total Collection"]
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

st.dataframe(
    client_haraka_f,
    use_container_width=True
)
