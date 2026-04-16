import pandas as pd
import numpy as np
import streamlit as st

# =========================
# 📅 SETTINGS
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI Dashboard")


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
    }


data = load_data()
codes = data["codes"]


# =========================
# 🧠 SALES PIPELINE
# =========================
def sales_pipeline(sales, codes):

    cols = [
        'Date','Warehouse','Client Code','Client Name','Notes','MF','Doc',
        'Rep Code','Sales Unit','Return Unit','Price','Discount','Sales Value'
    ]

    sales = sales.iloc[:, :len(cols)].copy()
    sales.columns = cols

    for c in ["Sales Unit", "Return Unit", "Price"]:
        sales[c] = pd.to_numeric(sales[c], errors="coerce").fillna(0)

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="inner")

    sales["Sales Value"] = sales["Sales Unit"] * sales["Price"]
    sales["Return Value"] = sales["Return Unit"] * sales["Price"]
    sales["Net Sales"] = sales["Sales Value"] - sales["Return Value"]

    return sales


# =========================
# 📦 OPENING PIPELINE
# =========================
def opening_pipeline(opening, codes):

    opening.columns = [
        'Branch','Evak','Opening','Sales','Returns',
        'Extra','Cash','Checks','Return Chick','Return Cash',
        'A','B','End'
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
# ⏳ OVERDUE PIPELINE
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
        overdue[c] = pd.to_numeric(overdue[c], errors="coerce").fillna(0)

    overdue["Overdue"] = overdue["120"] + overdue["150"] + overdue["150+"]

    overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    overdue = overdue.merge(codes, on="Rep Code", how="left")

    return overdue


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


filtered = filter_codes(codes)
rep_codes = filtered["Rep Code"].unique()


# =========================
# 🚀 BUILD DATA
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
# 📊 TABLES
# =========================
st.subheader("💰 Sales Data")
st.dataframe(sales)

st.subheader("📦 Opening Data")
st.dataframe(opening)

st.subheader("⏳ Overdue Data")
st.dataframe(overdue)


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

st.dataframe(compare)
