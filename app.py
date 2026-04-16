import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# =========================
# 📅 TIME SETTINGS
# =========================
current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1


# =========================
# 📂 LOAD DATA
# =========================
def load_data():
    return {
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "sales": pd.read_excel("Sales.xlsx", header=None),
        "codes": pd.read_excel("Code.xlsx"),
        "opening": pd.read_excel("Opening.xlsx", header=None),
        "overdue": pd.read_excel("Overdue.xlsx", header=None),
        "mapping": pd.read_excel("Mapping.xlsx"),
    }


# =========================
# 🧠 SALES FIX
# =========================
def fix_sales(sales):
    cols = [
        'Date','Warehouse','Client Code','Client Name','Notes','MF','Doc',
        'Rep Code','Sales Unit','Return Unit','Price','Discount','Sales Value'
    ]
    sales = sales.iloc[:, :len(cols)].copy()
    sales.columns = cols
    return sales


# =========================
# 🚀 SALES PIPELINE
# =========================
def sales_pipeline(sales, codes):

    sales = fix_sales(sales)

    for c in ["Sales Unit","Return Unit","Price"]:
        sales[c] = pd.to_numeric(sales[c], errors="coerce").fillna(0)

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="inner")

    sales["Sales Value"] = sales["Sales Unit"] * sales["Price"]
    sales["Return Value"] = sales["Return Unit"] * sales["Price"]
    sales["Net Sales"] = sales["Sales Value"] - sales["Return Value"]

    return sales


# =========================
# 🚀 OPENING PIPELINE
# =========================
def opening_pipeline(opening, codes):

    opening.columns = [
        'Branch','Evak','Opening','Sales','Returns',
        'Extra','Cash','Checks','Return Chick','Return Cash',
        'Area1','Area2','End Balance'
    ]

    opening["Rep Code"] = None
    mask = opening["Branch"].astype(str).str.contains("كود")
    opening.loc[mask, "Rep Code"] = opening.loc[mask, "Opening"]
    opening["Rep Code"] = opening["Rep Code"].ffill()

    opening = opening[~opening["Branch"].astype(str).str.contains("اجمالي|كود", na=False)]

    for c in ["Sales","Returns","Cash","Checks"]:
        opening[c] = pd.to_numeric(opening[c], errors="coerce").fillna(0)

    opening["Net Sales"] = opening["Sales"] - opening["Returns"]
    opening["Collection"] = opening["Cash"] + opening["Checks"]

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    opening = opening.merge(codes, on="Rep Code", how="left")

    return opening


# =========================
# 🚀 OVERDUE PIPELINE
# =========================
def overdue_pipeline(overdue, codes):

    overdue.columns = [
        "Client","Client Code","30","60","90","120","150","150+","Balance"
    ]

    overdue["Rep Code"] = None
    mask = overdue["Client"].astype(str).str.contains("كود")
    overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"]
    overdue["Rep Code"] = overdue["Rep Code"].ffill()

    overdue = overdue[~overdue["Client"].astype(str).str.contains("اجمالي", na=False)]

    for c in overdue.columns:
        if overdue[c].dtype != "object":
            overdue[c] = pd.to_numeric(overdue[c], errors="coerce").fillna(0)

    overdue["Overdue"] = overdue["120"] + overdue["150"] + overdue["150+"]

    overdue = overdue.merge(codes, on="Rep Code", how="left")

    return overdue


# =========================
# 🎨 STREAMLIT UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI Dashboard")

data = load_data()
codes = data["codes"]

# =========================
# 🎛️ FILTERS
# =========================
st.sidebar.header("🔎 Filters")

rep = st.sidebar.selectbox("Rep Name", ["All"] + list(codes["Rep Name"].dropna().unique()))
manager = st.sidebar.selectbox("Manager Name", ["All"] + list(codes["Manager Name"].dropna().unique()))
area = st.sidebar.selectbox("Area Name", ["All"] + list(codes["Area Name"].dropna().unique()))


def filter_codes(df):
    temp = df.copy()
    if rep != "All":
        temp = temp[temp["Rep Name"] == rep]
    if manager != "All":
        temp = temp[temp["Manager Name"] == manager]
    if area != "All":
        temp = temp[temp["Area Name"] == area]
    return temp


filtered_codes = filter_codes(codes)
rep_codes = filtered_codes["Rep Code"].unique()


# =========================
# 📦 BUILD DATA
# =========================
sales = sales_pipeline(data["sales"], codes)
opening = opening_pipeline(data["opening"], codes)
overdue = overdue_pipeline(data["overdue"], codes)


sales = sales[sales["Rep Code"].isin(rep_codes)]
opening = opening[opening["Rep Code"].isin(rep_codes)]
overdue = overdue[overdue["Rep Code"].isin(rep_codes)]


# =========================
# 🎴 KPI CARDS
# =========================
st.header("📊 KPI Overview")

c1, c2, c3 = st.columns(3)

c1.metric("💰 Sales", round(sales["Net Sales"].sum()))
c2.metric("📦 Opening", round(opening["Net Sales"].sum()))
c3.metric("⏳ Overdue", round(overdue["Overdue"].sum()))


# =========================
# 📊 CHARTS
# =========================

st.subheader("💰 Sales by Rep")
fig1 = px.bar(sales, x="Rep Code", y="Net Sales")
st.plotly_chart(fig1, use_container_width=True)


st.subheader("📦 Opening Performance")
fig2 = px.bar(opening, x="Rep Code", y="Net Sales")
st.plotly_chart(fig2, use_container_width=True)


st.subheader("⏳ Overdue Analysis")
fig3 = px.bar(overdue, x="Rep Code", y="Overdue")
st.plotly_chart(fig3, use_container_width=True)


# =========================
# 🎯 TARGET VS SALES
# =========================
st.subheader("🎯 Target vs Sales")

target = data["target_rep"]
target["Rep Code"] = pd.to_numeric(target["Rep Code"], errors="coerce")

compare = target.merge(
    sales.groupby("Rep Code", as_index=False)["Net Sales"].sum(),
    on="Rep Code",
    how="left"
)

fig4 = px.scatter(
    compare,
    x="Target",
    y="Net Sales",
    text="Rep Code"
)

st.plotly_chart(fig4, use_container_width=True)
