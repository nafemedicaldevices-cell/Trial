import pandas as pd
import numpy as np
import streamlit as st

# =========================
# ⚠️ SAFE IMPORT (plotly fallback)
# =========================
try:
    import plotly.graph_objects as go
    PLOTLY_OK = True
except:
    PLOTLY_OK = False

# =========================
# 📂 LOAD DATA
# =========================
@st.cache_data
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx", header=None),
        "codes": pd.read_excel("Code.xlsx"),
        "opening": pd.read_excel("Opening.xlsx", header=None),
        "overdue": pd.read_excel("Overdue.xlsx", header=None),
    }

# =========================
# 🧠 FIX SALES
# =========================
def fix_sales_columns(sales):
    cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit','Returns Unit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]
    sales = sales.iloc[:, :len(cols)].copy()
    sales.columns = cols
    return sales

# =========================
# 💰 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, codes):

    sales = fix_sales_columns(sales)

    for c in ["Sales Unit","Returns Unit","Sales Price","Invoice Discounts"]:
        sales[c] = pd.to_numeric(sales[c], errors="coerce").fillna(0)

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="inner")

    sales["Total Sales Value"] = sales["Sales Unit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    return sales

# =========================
# 📦 OPENING
# =========================
def build_opening_pipeline(opening, codes):

    opening = opening.iloc[:, :13]

    opening.columns = [
        'Branch',"Evak",'Opening Balance','Total Sales',
        'Returns','Sales Value Before Extra Discounts',
        'Cash Collection','Collection Checks',
        'Returned Chick','Collection Returned Chick',
        "Madinah",'Daienah','End Balance'
    ]

    opening['Rep Code'] = None
    mask = opening['Branch'].astype(str).str.strip() == "كود المندوب"
    opening.loc[mask, 'Rep Code'] = opening.loc[mask, 'Opening Balance']
    opening['Rep Code'] = opening['Rep Code'].ffill()

    for c in ['Total Sales','Returns','Cash Collection','Collection Checks']:
        opening[c] = pd.to_numeric(opening[c], errors='coerce').fillna(0)

    opening['Total Collection'] = opening['Cash Collection'] + opening['Collection Checks']
    opening["Sales After Returns"] = opening["Total Sales"] - opening['Returns']

    return opening

# =========================
# 🚀 UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 KPI Dashboard (Stable Version)")

data = load_data()

sales = build_sales_pipeline(data["sales"], data["codes"])
opening = build_opening_pipeline(data["opening"], data["codes"])
overdue = data["overdue"]

# =========================
# 🎛️ FILTER (SIMPLE SAFE)
# =========================
rep_list = sales["Rep Name"].dropna().unique() if "Rep Name" in sales.columns else []

selected_rep = st.sidebar.selectbox("Select Rep", rep_list)

filtered_sales = sales[sales["Rep Name"] == selected_rep] if "Rep Name" in sales.columns else sales
filtered_opening = opening.copy()

# =========================
# 📊 KPI
# =========================
actual = filtered_sales["Sales After Returns"].sum()
target = 1000000
pct = (actual / target * 100) if target else 0

st.markdown(f"""
### 📊 Sales: {actual:,.0f} | 🎯 Target: {target:,.0f} | 📈 {pct:.1f}%
""")

# =========================
# 💰 FLOW DATA
# =========================
total_sales = filtered_sales["Sales After Returns"].sum()
returns = filtered_sales["Returns Value"].sum()
discounts = filtered_sales["Invoice Discounts"].sum()

net_after_returns = total_sales - returns
net_sales = net_after_returns - discounts

# =========================
# 📊 WATERFALL (SAFE)
# =========================
st.header("💰 Sales Flow")

if PLOTLY_OK:

    fig = go.Figure(go.Waterfall(
        name="Flow",
        orientation="v",
        measure=["absolute","relative","relative","total"],
        x=["Total Sales","Returns","Discounts","Net Sales"],
        y=[total_sales,-returns,-discounts,net_sales],
        connector={"line":{"color":"gray"}}
    ))

    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Plotly not installed - showing simple flow")

    st.markdown(f"""
    💰 Total Sales → {total_sales:,.0f}  
    ↳ ↩ Returns → {returns:,.0f}  
    ↳ 🎯 Discounts → {discounts:,.0f}  
    ↳ 💵 Net Sales → {net_sales:,.0f}
    """)

# =========================
# 📋 TABLES
# =========================
st.header("📋 Sales Data")
st.dataframe(filtered_sales)

st.header("📦 Opening Data")
st.dataframe(filtered_opening)
