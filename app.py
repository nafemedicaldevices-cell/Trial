import pandas as pd
import numpy as np
import streamlit as st

# =========================
# 🎯 PAGE CONFIG
# =========================
st.set_page_config(page_title="KPI Dashboard", layout="wide")

# =========================
# 📅 TIME SETTINGS
# =========================
today = pd.Timestamp.today()
current_month = today.month
current_quarter = (current_month - 1) // 3 + 1

# =========================
# 🎨 CSS STYLE (KPI CARDS)
# =========================
st.markdown("""
<style>
.kpi-card {
    background: #ffffff;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
    text-align: center;
}
.kpi-title {
    font-size: 16px;
    color: #666;
}
.kpi-value {
    font-size: 28px;
    font-weight: bold;
    color: #1f77b4;
}
.kpi-sub {
    font-size: 13px;
    color: #999;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 📂 LOAD DATA
# =========================
@st.cache_data
def load_data():
    sales = pd.read_excel("Sales.xlsx")
    return sales

df = load_data()

# =========================
# 🔎 FILTERS
# =========================
st.sidebar.header("Filters")

rep_filter = st.sidebar.selectbox("Sales Rep", ["All"] + list(df["Rep"].dropna().unique()))
customer_filter = st.sidebar.selectbox("Customer", ["All"] + list(df["Customer"].dropna().unique()))
month_filter = st.sidebar.selectbox("Month", ["All"] + sorted(df["Month"].dropna().unique()))

filtered = df.copy()

if rep_filter != "All":
    filtered = filtered[filtered["Rep"] == rep_filter]

if customer_filter != "All":
    filtered = filtered[filtered["Customer"] == customer_filter]

if month_filter != "All":
    filtered = filtered[filtered["Month"] == month_filter]

# =========================
# 📊 KPI CALCULATIONS
# =========================
target = filtered["Target"].sum()
sales = filtered["Sales"].sum()
achievement = (sales / target * 100) if target != 0 else 0

# time splits (لو عندك عمود Date)
if "Date" in filtered.columns:
    filtered["Date"] = pd.to_datetime(filtered["Date"])
    yearly = filtered["Sales"].sum()
    quarterly = filtered[filtered["Date"].dt.quarter == current_quarter]["Sales"].sum()
    monthly = filtered[filtered["Date"].dt.month == current_month]["Sales"].sum()
else:
    yearly = quarterly = monthly = sales

uptodate = sales

# =========================
# 📦 KPI CARDS UI
# =========================
col1, col2, col3, col4 = st.columns(4)

def kpi(col, title, value, sub):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value:,.0f}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

kpi(col1, "Year Sales", yearly, "Total Year Performance")
kpi(col2, "Quarter Sales", quarterly, f"Q{current_quarter}")
kpi(col3, "Month Sales", monthly, f"Month {current_month}")
kpi(col4, "Up To Date", uptodate, f"Achievement {achievement:.1f}%")

# =========================
# 📋 DATA PREVIEW
# =========================
st.markdown("### 📊 Data Preview")
st.dataframe(filtered)
