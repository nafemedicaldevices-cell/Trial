import pandas as pd
import numpy as np
import streamlit as st

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
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
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

    for col in [
        "Sales Unit Before Edit","Returns Unit Before Edit",
        "Sales Price","Invoice Discounts"
    ]:
        sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="inner")

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    def group(df, col):
        return df.groupby(col, as_index=False)[
            ["Total Sales Value","Returns Value","Sales After Returns"]
        ].sum()

    return {
        "rep": group(sales,"Rep Name"),
        "manager": group(sales,"Manager Name"),
        "area": group(sales,"Area Name"),
        "supervisor": group(sales,"Supervisor Name"),
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

    for col in ['Opening Balance','Total Sales','Returns','Cash Collection','Collection Checks']:
        opening[col] = pd.to_numeric(opening[col], errors='coerce').fillna(0)

    opening['Total Collection'] = opening['Cash Collection'] + opening['Collection Checks']
    opening["Sales After Returns"] = opening["Total Sales"] - opening['Returns']

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    opening = opening.merge(codes, on='Rep Code', how='left')

    def group(df, col):
        return df.groupby(col, as_index=False)[
            ["Total Sales","Returns","Sales After Returns","Total Collection"]
        ].sum()

    return {
        "rep": group(opening,"Rep Name"),
        "manager": group(opening,"Manager Name"),
        "area": group(opening,"Area Name"),
        "supervisor": group(opening,"Supervisor Name"),
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
        overdue['120 Days'] +
        overdue['150 Days'] +
        overdue['More Than 150 Days']
    )

    overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce")
    overdue = overdue.merge(codes, on='Rep Code', how='left')

    def group(df, col):
        return df.groupby(col, as_index=False)[["Overdue Value"]].sum()

    return {
        "rep": group(overdue,"Rep Name"),
        "manager": group(overdue,"Manager Name"),
        "area": group(overdue,"Area Name"),
        "supervisor": group(overdue,"Supervisor Name"),
    }


# =========================
# 🎛️ FILTER
# =========================
def apply_filter(data, filter_type, value):

    key_map = {
        "Rep": "rep",
        "Supervisor": "supervisor",
        "Area": "area",
        "Manager": "manager"
    }

    col_map = {
        "Rep": "Rep Name",
        "Supervisor": "Supervisor Name",
        "Area": "Area Name",
        "Manager": "Manager Name"
    }

    df = data[key_map[filter_type]]
    return df[df[col_map[filter_type]] == value]


# =========================
# 🎨 UI STYLE (KPI CARDS)
# =========================
st.set_page_config(layout="wide")

st.markdown("""
<style>
.kpi-card {
    background: #0f172a;
    padding: 18px;
    border-radius: 16px;
    color: white;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    text-align: center;
}
.kpi-title {
    font-size: 14px;
    opacity: 0.8;
}
.kpi-value {
    font-size: 26px;
    font-weight: bold;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# 🎯 KPI CARDS FUNCTION
# =========================
def kpi_cards(sales_df):

    total_sales = sales_df["rep"]["Total Sales Value"].sum()
    returns = sales_df["rep"]["Returns Value"].sum()
    net_sales = sales_df["rep"]["Sales After Returns"].sum()

    target = total_sales * 1.2  # مثال target (عدله حسب بياناتك)
    achievement = (net_sales / target) * 100 if target > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Sales</div>
            <div class="kpi-value">{total_sales:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Returns</div>
            <div class="kpi-value">{returns:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Net Sales</div>
            <div class="kpi-value">{net_sales:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Target Achievement %</div>
            <div class="kpi-value">{achievement:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)


# =========================
# 🎨 UI
# =========================
st.title("📊 KPI Dashboard")

data = load_data()

sales = build_sales_pipeline(data["sales"], data["codes"])
opening = build_opening_pipeline(data["opening"], data["codes"])
overdue = build_overdue_pipeline(data["overdue"], data["codes"])


# =========================
# 🎛️ FILTER UI
# =========================
st.sidebar.header("Filters")

filter_type = st.sidebar.radio(
    "Filter By",
    ["Rep","Supervisor","Area","Manager"]
)

options = sales[filter_type.lower()][f"{filter_type} Name"].dropna().unique()
selected_value = st.sidebar.selectbox("Select", options)


# =========================
# 📊 KPI SECTION (NEW)
# =========================
st.header("📌 KPI Summary")
kpi_cards(sales)


# =========================
# 📊 OUTPUT TABLES
# =========================
st.header("💰 SALES")
st.dataframe(apply_filter(sales, filter_type, selected_value))

st.header("📦 OPENING")
st.dataframe(apply_filter(opening, filter_type, selected_value))

st.header("⏳ OVERDUE")
st.dataframe(apply_filter(overdue, filter_type, selected_value))
