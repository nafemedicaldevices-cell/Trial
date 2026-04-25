import streamlit as st
import pandas as pd

st.title("📊 Sales vs Target Dashboard")

# =========================
# 📂 LOAD SALES (DIRECT)
# =========================
sales = pd.read_excel("Sales.xlsx")
sales.columns = sales.columns.str.strip()

# auto numeric
for col in sales.columns:
    if sales[col].dtype == "object":
        continue
    sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

# detect rep column
rep_col = [c for c in sales.columns if "rep" in c.lower() or "مندوب" in c]

if not rep_col:
    st.error("❌ Rep column not found")
    st.stop()

sales["Rep Code"] = sales[rep_col[0]].astype(str).str.strip()

# =========================
# 💰 NET SALES
# =========================
sales["Net Sales"] = (
    sales.get("Sales Value", 0)
    - sales.get("Returns Value", 0)
    - sales.get("Invoice Discounts", 0)
)

net_sales = sales.groupby("Rep Code", as_index=False)["Net Sales"].sum()

# =========================
# 📂 LOAD TARGETS
# =========================
targets = pd.read_excel("Target Rep.xlsx", sheet_name=0)
targets.columns = targets.columns.str.strip()

targets = targets.melt(
    id_vars=["Year", "Product Code", "Old Product Name", "Sales Price"],
    var_name="Code",
    value_name="Target"
)

targets["Target"] = pd.to_numeric(targets["Target"], errors="coerce")
targets["Target"] = targets["Target"] / 12

target_sum = targets.groupby("Code", as_index=False)["Target"].sum()

# =========================
# 🔗 MERGE
# =========================
df = target_sum.merge(
    net_sales,
    left_on="Code",
    right_on="Rep Code",
    how="left"
)

df["Net Sales"] = df["Net Sales"].fillna(0)

df["Achievement %"] = (df["Net Sales"] / df["Target"]) * 100
df["Achievement %"] = df["Achievement %"].fillna(0)

# =========================
# 📊 KPI
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("🎯 Target", f"{df['Target'].sum():,.0f}")
col2.metric("💰 Net Sales", f"{df['Net Sales'].sum():,.0f}")
col3.metric("📈 Achievement %", f"{(df['Net Sales'].sum()/df['Target'].sum()*100):.2f}%")

st.dataframe(df)
