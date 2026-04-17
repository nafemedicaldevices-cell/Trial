import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

# =========================
# 📅 TIME SETTINGS
# =========================
current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1

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
    expected_cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit','Returns Unit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]
    sales = sales.iloc[:, :len(expected_cols)].copy()
    sales.columns = expected_cols
    return sales

# =========================
# 💰 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, codes):
    sales = fix_sales_columns(sales)
    num_cols = ["Sales Unit","Returns Unit","Sales Price","Invoice Discounts"]
    for col in num_cols:
        sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)
    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")
    sales = sales.merge(codes, on="Rep Code", how="inner")
    sales["Total Sales Value"]    = sales["Sales Unit"] * sales["Sales Price"]
    sales["Returns Value"]        = sales["Returns Unit"] * sales["Sales Price"]
    sales["Sales After Returns"]  = sales["Total Sales Value"] - sales["Returns Value"]
    def group(df, col):
        return df.groupby(col, as_index=False)[
            ["Total Sales Value","Returns Value","Sales After Returns","Invoice Discounts"]
        ].sum()
    return {
        "rep":        group(sales, "Rep Name"),
        "manager":    group(sales, "Manager Name"),
        "area":       group(sales, "Area Name"),
        "supervisor": group(sales, "Supervisor Name"),
        "_raw":       sales,
    }

# =========================
# 📦 OPENING PIPELINE
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
    opening = opening[
        opening['Branch'].notna() &
        (~opening['Branch'].astype(str).str.contains('كود|اجماليات', na=False))
    ]
    for col in ['Total Sales','Returns','Cash Collection','Collection Checks']:
        opening[col] = pd.to_numeric(opening[col], errors='coerce').fillna(0)
    opening['Total Collection']   = opening['Cash Collection'] + opening['Collection Checks']
    opening["Sales After Returns"] = opening["Total Sales"] - opening['Returns']
    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    opening = opening.merge(codes, on='Rep Code', how='left')
    def group(df, col):
        return df.groupby(col, as_index=False)[["Sales After Returns"]].sum()
    return {
        "rep":        group(opening, "Rep Name"),
        "manager":    group(opening, "Manager Name"),
        "area":       group(opening, "Area Name"),
        "supervisor": group(opening, "Supervisor Name"),
    }

# =========================
# ⏳ OVERDUE PIPELINE
# =========================
def build_overdue_pipeline(overdue, codes):
    overdue.columns = [
        "Client Name","Client Code","30 Days","60 Days","90 Days",
        "120 Days","150 Days","More Than 150 Days","Balance"
    ]
    overdue['Rep Code'] = overdue['Client Code'].ffill()
    overdue['Overdue Value'] = (
        overdue['120 Days'] + overdue['150 Days'] + overdue['More Than 150 Days']
    )
    overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce")
    overdue = overdue.merge(codes, on='Rep Code', how='left')
    def group(df, col):
        return df.groupby(col, as_index=False)[["Overdue Value"]].sum()
    return {
        "rep":        group(overdue, "Rep Name"),
        "manager":    group(overdue, "Manager Name"),
        "area":       group(overdue, "Area Name"),
        "supervisor": group(overdue, "Supervisor Name"),
    }

# =========================
# 🌳 SALES FLOW SVG
# =========================
def sales_flow_svg(total_sales, returns, inv_disc, extra_disc, net_sales):
    def fmt(v):
        if abs(v) >= 1_000_000:
            return f"{v/1_000_000:.2f}M"
        elif abs(v) >= 1_000:
            return f"{v/1_000:.1f}K"
        return f"{v:,.0f}"

    total_disc = inv_disc + extra_disc
    after_ret  = total_sales - returns

    svg = f"""
    <div style="direction:rtl; font-family: 'Segoe UI', sans-serif;">
    <svg width="100%" viewBox="0 0 680 680" role="img" xmlns="http://www.w3.org/2000/svg">
      <title>مخطط تدفق المبيعات</title>
      <defs>
        <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M2 1L8 5L2 9" fill="none" stroke="#185FA5" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
        <marker id="arr-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M2 1L8 5L2 9" fill="none" stroke="#A32D2D" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
        <marker id="arr-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M2 1L8 5L2 9" fill="none" stroke="#3B6D11" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
      </defs>

      <!-- ===== BOX 1: إجمالي المبيعات ===== -->
      <rect x="190" y="30" width="300" height="72" rx="12"
            fill="#E6F1FB" stroke="#185FA5" stroke-width="1"/>
      <text x="340" y="62" text-anchor="middle" font-size="15"
            font-weight="600" fill="#0C447C">إجمالي المبيعات</text>
      <text x="340" y="86" text-anchor="middle" font-size="13"
            fill="#185FA5">{fmt(total_sales)}</text>

      <!-- سهم رئيسي 1 -->
      <line x1="340" y1="102" x2="340" y2="146"
            stroke="#185FA5" stroke-width="3"
            marker-end="url(#arr-blue)"/>

      <!-- نقطة تفرع 1 -->
      <circle cx="340" cy="160" r="6" fill="#185FA5"/>

      <!-- فرع المرتجعات -->
      <line x1="346" y1="160" x2="476" y2="160"
            stroke="#A32D2D" stroke-width="1.5" stroke-dasharray="5 3"
            marker-end="url(#arr-red)"/>
      <rect x="478" y="136" width="172" height="52" rx="8"
            fill="#FCEBEB" stroke="#A32D2D" stroke-width="1"/>
      <text x="564" y="157" text-anchor="middle" font-size="13"
            font-weight="600" fill="#791F1F">مرتجعات البيع</text>
      <text x="564" y="176" text-anchor="middle" font-size="12"
            fill="#A32D2D">- {fmt(returns)}</text>

      <!-- سهم رئيسي 2 -->
      <line x1="340" y1="166" x2="340" y2="246"
            stroke="#185FA5" stroke-width="3"
            marker-end="url(#arr-blue)"/>

      <!-- ===== BOX 2: بعد المرتجعات ===== -->
      <rect x="190" y="248" width="300" height="72" rx="12"
            fill="#E6F1FB" stroke="#185FA5" stroke-width="1"/>
      <text x="340" y="280" text-anchor="middle" font-size="15"
            font-weight="600" fill="#0C447C">بعد المرتجعات</text>
      <text x="340" y="304" text-anchor="middle" font-size="13"
            fill="#185FA5">{fmt(after_ret)}</text>

      <!-- سهم رئيسي 3 -->
      <line x1="340" y1="320" x2="340" y2="364"
            stroke="#185FA5" stroke-width="3"
            marker-end="url(#arr-blue)"/>

      <!-- نقطة تفرع 2 -->
      <circle cx="340" cy="378" r="6" fill="#185FA5"/>

      <!-- فرع خصومات عادية -->
      <line x1="346" y1="378" x2="476" y2="378"
            stroke="#A32D2D" stroke-width="1.5" stroke-dasharray="5 3"
            marker-end="url(#arr-red)"/>
      <rect x="478" y="354" width="172" height="52" rx="8"
            fill="#FCEBEB" stroke="#A32D2D" stroke-width="1"/>
      <text x="564" y="375" text-anchor="middle" font-size="13"
            font-weight="600" fill="#791F1F">خصومات عادية</text>
      <text x="564" y="394" text-anchor="middle" font-size="12"
            fill="#A32D2D">- {fmt(inv_disc)}</text>

      <!-- سهم رئيسي 4 -->
      <line x1="340" y1="384" x2="340" y2="464"
            stroke="#185FA5" stroke-width="3"
            marker-end="url(#arr-blue)"/>

      <!-- نقطة تفرع 3 -->
      <circle cx="340" cy="478" r="6" fill="#185FA5"/>

      <!-- فرع خصومات إضافية -->
      <line x1="346" y1="478" x2="476" y2="478"
            stroke="#A32D2D" stroke-width="1.5" stroke-dasharray="5 3"
            marker-end="url(#arr-red)"/>
      <rect x="478" y="454" width="172" height="52" rx="8"
            fill="#FCEBEB" stroke="#A32D2D" stroke-width="1"/>
      <text x="564" y="475" text-anchor="middle" font-size="13"
            font-weight="600" fill="#791F1F">خصومات إضافية</text>
      <text x="564" y="494" text-anchor="middle" font-size="12"
            fill="#A32D2D">- {fmt(extra_disc)}</text>

      <!-- سهم رئيسي 5 -->
      <line x1="340" y1="484" x2="340" y2="564"
            stroke="#3B6D11" stroke-width="3"
            marker-end="url(#arr-green)"/>

      <!-- ===== BOX 3: صافي المبيعات ===== -->
      <rect x="170" y="566" width="340" height="80" rx="14"
            fill="#EAF3DE" stroke="#3B6D11" stroke-width="1.5"/>
      <text x="340" y="598" text-anchor="middle" font-size="16"
            font-weight="700" fill="#27500A">صافي المبيعات النهائي</text>
      <text x="340" y="624" text-anchor="middle" font-size="14"
            font-weight="600" fill="#3B6D11">{fmt(net_sales)}</text>

    </svg>
    </div>
    """
    return svg

# =========================
# 🎨 KPI CARD
# =========================
def kpi_card(title, actual, target):
    pct = (actual / target * 100) if target else 0
    color = "#27ae60" if pct >= 100 else "#f39c12" if pct >= 70 else "#e74c3c"
    bar_w = min(pct, 100)
    return f"""
    <div style="
        background:white; padding:18px; border-radius:14px;
        box-shadow:0px 2px 10px rgba(0,0,0,0.08);
        text-align:center; border-left:6px solid {color};
    ">
        <div style="font-size:14px;color:#666;font-weight:600">{title}</div>
        <div style="font-size:24px;font-weight:bold;color:#1f77b4;margin-top:8px">
            {actual:,.0f}
        </div>
        <div style="font-size:12px;color:#999;margin-top:4px">Target: {target:,.0f}</div>
        <div style="background:#eee;border-radius:99px;height:6px;margin:8px 0;">
          <div style="background:{color};width:{bar_w:.1f}%;height:6px;border-radius:99px;"></div>
        </div>
        <div style="font-size:15px;font-weight:bold;color:{color}">{pct:.1f}%</div>
    </div>
    """

# =========================
# 🚀 UI
# =========================
st.set_page_config(layout="wide", page_title="KPI Dashboard")
st.title("📊 KPI Dashboard")

data = load_data()

sales   = build_sales_pipeline(data["sales"],   data["codes"])
opening = build_opening_pipeline(data["opening"], data["codes"])
overdue = build_overdue_pipeline(data["overdue"], data["codes"])

# =========================
# 🎛️ FILTER
# =========================
st.sidebar.header("Filters")

filter_type = st.sidebar.radio("Filter By", ["Rep", "Supervisor", "Area", "Manager"])

col_map = {
    "Rep":        "Rep Name",
    "Supervisor": "Supervisor Name",
    "Area":       "Area Name",
    "Manager":    "Manager Name",
}

key_map = {
    "Rep":        "rep",
    "Supervisor": "supervisor",
    "Area":       "area",
    "Manager":    "manager",
}

options = sales[key_map[filter_type]][col_map[filter_type]].dropna().unique()
selected_value = st.sidebar.selectbox("Select", options)

def apply_filter(data_dict, key, col, value):
    df = data_dict[key]
    if col in df.columns:
        return df[df[col] == value]
    return df

filtered_sales   = apply_filter(sales,   key_map[filter_type], col_map[filter_type], selected_value)
filtered_opening = apply_filter(opening, key_map[filter_type], col_map[filter_type], selected_value)
filtered_overdue = apply_filter(overdue, key_map[filter_type], col_map[filter_type], selected_value)

# =========================
# 🎯 KPI TARGETS
# =========================
actual_year      = filtered_sales["Sales After Returns"].sum()
actual_month     = actual_year * 0.1
actual_quarter   = actual_year * 0.3
actual_uptodate  = actual_year * 0.7

target_year      = 1_000_000
target_month     = 90_000
target_quarter   = 250_000
target_uptodate  = 700_000

# =========================
# 📊 KPI SECTION
# =========================
st.subheader("🎯 Target Performance")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card("📅 Year Sales",    actual_year,     target_year),     unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("📆 Month Sales",   actual_month,    target_month),    unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("📊 Quarter Sales", actual_quarter,  target_quarter),  unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("⏳ Up To Date",    actual_uptodate, target_uptodate), unsafe_allow_html=True)

# =========================
# 🌳 SALES FLOW DIAGRAM
# =========================
st.header("🌳 Sales Flow Analysis")

total_sales  = filtered_sales["Total Sales Value"].sum()    if "Total Sales Value"   in filtered_sales.columns else filtered_sales["Sales After Returns"].sum()
returns      = filtered_sales["Returns Value"].sum()         if "Returns Value"        in filtered_sales.columns else 0
inv_disc     = filtered_sales["Invoice Discounts"].sum()     if "Invoice Discounts"    in filtered_sales.columns else 0
extra_disc   = 0
net_sales    = total_sales - returns - inv_disc - extra_disc

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown(sales_flow_svg(total_sales, returns, inv_disc, extra_disc, net_sales),
                unsafe_allow_html=True)

with col_right:
    st.markdown("#### تفاصيل القيم")
    st.markdown(f"""
    | البند | القيمة |
    |---|---|
    | إجمالي المبيعات | {total_sales:,.0f} |
    | مرتجعات البيع | {returns:,.0f} |
    | بعد المرتجعات | {total_sales - returns:,.0f} |
    | خصومات عادية | {inv_disc:,.0f} |
    | خصومات إضافية | {extra_disc:,.0f} |
    | **صافي المبيعات** | **{net_sales:,.0f}** |
    """)

# =========================
# 📋 TABLES
# =========================
st.header("💰 Sales Data")
st.dataframe(filtered_sales)

st.header("📦 Opening Data")
st.dataframe(filtered_opening)

st.header("⏳ Overdue Data")
st.dataframe(filtered_overdue)
