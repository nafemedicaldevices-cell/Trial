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
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),

        "sales": pd.read_excel("Sales.xlsx", header=None),

        "mapping": pd.read_excel("Mapping.xlsx"),
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
# 🚀 TARGET PIPELINE
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()
    mapping.columns = mapping.columns.str.strip()

    if "Product Code" not in df.columns:
        df["Product Code"] = np.nan

    if "Sales Price" not in df.columns:
        df["Sales Price"] = 0

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    mapping = mapping.drop_duplicates("Product Code")

    fixed_cols = [c for c in ["Year", "Product Code", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    df[id_name] = pd.to_numeric(
        df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True),
        errors="coerce"
    )

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Value"] = df["Target (Unit)"] * df["Sales Price"]

    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    return {
        "value_table": group(df).rename(columns={"Value": "Full Year 🏆"})
    }


# =========================
# 🚀 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, codes):

    sales = fix_sales_columns(sales)

    sales.columns = sales.columns.str.strip()
    codes.columns = codes.columns.str.strip()

    for col in [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price",
        "Invoice Discounts"
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
            ["Total Sales Value", "Returns Value", "Sales After Returns"]
        ].sum()

    return {
        "rep": group(sales, "Rep Code"),
        "manager": group(sales, "Manager Code"),
        "area": group(sales, "Area Code"),
        "supervisor": group(sales, "Supervisor Code")
    }


# =========================
# 🚀 OPENING PIPELINE
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

    for col in [
        'Opening Balance','Total Sales','Returns',
        'Cash Collection','Collection Checks'
    ]:
        opening[col] = pd.to_numeric(opening[col], errors="coerce").fillna(0)

    opening['Total Collection'] = opening['Cash Collection'] + opening['Collection Checks']
    opening["Sales After Returns"] = opening["Total Sales"] - opening['Returns']

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    opening = opening.merge(codes, on='Rep Code', how='left')

    def group(df, col):
        return df.groupby(col, as_index=False)[
            ["Total Sales","Returns","Sales After Returns","Total Collection"]
        ].sum()

    return {
        "rep": group(opening,"Rep Code"),
        "manager": group(opening,"Manager Code"),
        "area": group(opening,"Area Code"),
        "supervisor": group(opening,"Supervisor Code")
    }


# =========================
# 🚀 OVERDUE PIPELINE
# =========================
def build_overdue_pipeline(overdue, codes):

    overdue.columns = [
        "Client Name","Client Code","30 Days","60 Days","90 Days",
        "120 Days","150 Days","More Than 150 Days","Balance"
    ]

    overdue["Rep Code"] = overdue["Client Code"].ffill()
    overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce")

    overdue["Overdue Value"] = (
        overdue["120 Days"] +
        overdue["150 Days"] +
        overdue["More Than 150 Days"]
    )

    overdue = overdue.merge(codes, on="Rep Code", how="left")

    def group(df, col):
        return df.groupby(col, as_index=False)[["Overdue Value"]].sum()

    return {
        "rep": group(overdue,"Rep Code"),
        "manager": group(overdue,"Manager Code"),
        "area": group(overdue,"Area Code"),
        "supervisor": group(overdue,"Supervisor Code")
    }


# =========================
# 🎨 UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI Dashboard")

data = load_data()

sales = build_sales_pipeline(data["sales"], data["codes"])
opening = build_opening_pipeline(data["opening"], data["codes"])
overdue = build_overdue_pipeline(data["overdue"], data["codes"])

target_rep = build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
target_manager = build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])
target_area = build_target_pipeline(data["target_area"], "Area Code", data["mapping"])
target_supervisor = build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"])

codes = data["codes"].copy()
codes.columns = codes.columns.str.strip()


# =========================
# 🎛️ FILTER
# =========================
st.sidebar.header("Filters")

filter_type = st.sidebar.radio("Filter By", ["Rep","Supervisor","Area","Manager"])

name_map = {
    "Rep": "Rep Name",
    "Supervisor": "Supervisor Name",
    "Area": "Area Name",
    "Manager": "Manager Name"
}

code_map = {
    "Rep": "Rep Code",
    "Supervisor": "Supervisor Code",
    "Area": "Area Code",
    "Manager": "Manager Code"
}

options = codes[name_map[filter_type]].dropna().unique()
selected_name = st.sidebar.selectbox("Select", options)

selected_code = codes.loc[
    codes[name_map[filter_type]] == selected_name,
    code_map[filter_type]
].iloc[0]


# =========================
# 📊 KPI CALCULATION
# =========================
target_df = target_rep["value_table"] if filter_type == "Rep" else \
            target_supervisor["value_table"] if filter_type == "Supervisor" else \
            target_area["value_table"] if filter_type == "Area" else \
            target_manager["value_table"]

sales_df = sales[filter_type.lower()]

total_target = target_df["Full Year 🏆"].sum()
total_sales = sales_df["Sales After Returns"].sum()

achievement = (total_sales / total_target * 100) if total_target else 0

month_factor = current_month / 12
quarter_factor = current_quarter / 4


# =========================
# 🧾 KPI CARDS (PRO STYLE)
# =========================
def kpi_card(title, sales_val, target_val):
    ach = (sales_val / target_val * 100) if target_val else 0

    st.markdown(f"""
    <div style="
        padding:20px;
        border-radius:15px;
        background:#0f172a;
        color:white;
        text-align:center;
        box-shadow:0 6px 15px rgba(0,0,0,0.4);
    ">
        <h4 style="color:#94a3b8;margin:0;">{title}</h4>
        <h2 style="color:#22c55e;margin:8px 0;">
            {sales_val:,.0f} / {target_val:,.0f}
        </h2>
        <h3 style="color:#38bdf8;margin:0;">
            {ach:.1f}%
        </h3>
    </div>
    """, unsafe_allow_html=True)


col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_card("🎯 YEAR", total_sales, total_target)

with col2:
    kpi_card("📊 QUARTER", total_sales * quarter_factor, total_target * quarter_factor)

with col3:
    kpi_card("📅 MONTH", total_sales * month_factor, total_target * month_factor)

with col4:
    kpi_card("📈 YTD", total_sales * month_factor, total_target * month_factor)


# =========================
# 📊 TABLES
# =========================
def filter_df(df_dict):
    df = df_dict[filter_type.lower()]
    return df[df[code_map[filter_type]] == selected_code]

st.header("💰 SALES")
st.dataframe(filter_df(sales))

st.header("📦 OPENING")
st.dataframe(filter_df(opening))

st.header("⏳ OVERDUE")
st.dataframe(filter_df(overdue))
