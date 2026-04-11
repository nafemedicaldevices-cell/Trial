import streamlit as st
import data_pipeline as p   # ✅ مهم جدًا التصحيح هنا

# =========================
# 📂 LOAD DATA
# =========================
data = p.load_data()

target = p.build_target_pipeline(
    data["target_rep"],
    "Rep Code",
    data["mapping"]
)

sales = p.build_sales_pipeline(
    data["sales"],
    data["mapping"],
    data["codes"]
)

# =========================
# 🎨 UI
# =========================
st.set_page_config(layout="wide")

st.title("📊 Test Dashboard")

# =========================
# TARGET
# =========================
st.subheader("🎯 Target KPI")
st.dataframe(target["value_table"])

# =========================
# SALES
# =========================
st.subheader("💰 Sales KPI (Rep Level)")
st.dataframe(sales["rep_value"])
