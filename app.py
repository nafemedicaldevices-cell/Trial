import streamlit as st
import pandas as pd

# =========================
# 📌 LOAD DATA (بعد الربط)
# =========================

sales = sales.copy()

# تأكد إن الأعمدة موجودة
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
# 🎛 FILTER FUNCTION (CORE)
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
# 🎛 STREAMLIT FILTERS
# =========================

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
# 📊 SHOW RESULT
# =========================

st.subheader("📌 Filtered Data")

st.dataframe(filtered_sales, use_container_width=True)
