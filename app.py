import streamlit as st
import pandas as pd

from linking import build_model

# =========================
# 📌 LOAD FROM LINKING LAYER
# =========================

model = build_model()

sales = model["sales"]

# مهم جدًا لتجنب NameError + مشاكل النسخ
sales = sales.copy()


# =========================
# 🎛 FILTER ENGINE
# =========================

def filter_data(df, manager, area, supervisor, company, rep):

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

    return df


# =========================
# 🧹 CLEAN COLUMNS SAFETY
# =========================

required_cols = [
    "Manager",
    "Area",
    "Supervisor",
    "Company",
    "Old Rep Name"
]

for col in required_cols:
    if col not in sales.columns:
        sales[col] = None


# =========================
# 🎛 STREAMLIT UI
# =========================

st.set_page_config(
    page_title="Sales Dashboard",
    layout="wide"
)

st.title("📊 Sales Dashboard")


st.sidebar.header("🎛 Filters")


manager = st.sidebar.selectbox(
    "Manager",
    ["All"] + sorted(sales["Manager"].dropna().unique())
)

area = st.sidebar.selectbox(
    "Area",
    ["All"] + sorted(sales["Area"].dropna().unique())
)

supervisor = st.sidebar.selectbox(
    "Supervisor",
    ["All"] + sorted(sales["Supervisor"].dropna().unique())
)

company = st.sidebar.selectbox(
    "Company",
    ["All"] + sorted(sales["Company"].dropna().unique())
)

rep = st.sidebar.selectbox(
    "Rep Name",
    ["All"] + sorted(sales["Old Rep Name"].dropna().unique())
)


# =========================
# 🔗 APPLY FILTERS
# =========================

filtered_sales = filter_data(
    sales,
    manager,
    area,
    supervisor,
    company,
    rep
)


# =========================
# 📊 OUTPUT
# =========================

st.subheader("📌 Filtered Sales Data")

st.dataframe(
    filtered_sales,
    use_container_width=True
)


# =========================
# 📊 SIMPLE KPIs (اختياري)
# =========================

if "Net Sales" in filtered_sales.columns:

    st.metric(
        "Net Sales",
        filtered_sales["Net Sales"].sum()
    )

if "Returns Value" in filtered_sales.columns:

    st.metric(
        "Returns",
        filtered_sales["Returns Value"].sum()
    )
