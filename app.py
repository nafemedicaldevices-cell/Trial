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
# 🎯 TARGET PIPELINE
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    if "Product Code" not in df.columns:
        df["Product Code"] = np.nan
    if "Product Name" not in df.columns:
        df["Product Name"] = np.nan
    if "Sales Price" not in df.columns:
        df["Sales Price"] = 0

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    mapping = mapping.drop_duplicates("Product Code")

    fixed_cols = [c for c in ["Year","Product Code","Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    df[id_name] = pd.to_numeric(df[id_name], errors="coerce")

    df = df.merge(
        mapping[["Product Code","Product Name"]],
        on="Product Code",
        how="left"
    )

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Value"] = df["Target (Unit)"] * df["Sales Price"]

    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = group(df)

    return {
        "value_table": value_table
    }


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
        "rep": group(sales,"Rep Code"),
        "manager": group(sales,"Manager Code"),
        "area": group(sales,"Area Code"),
        "supervisor": group(sales,"Supervisor Code"),
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
        "rep": group(opening,"Rep Code"),
        "manager": group(opening,"Manager Code"),
        "area": group(opening,"Area Code"),
        "supervisor": group(opening,"Supervisor Code"),
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
    overdue['Overdue Value'] = overdue['120 Days'] + overdue['150 Days'] + overdue['More Than 150 Days']

    overdue = overdue.merge(codes, on='Rep Code', how='left')

    def group(df, col):
        return df.groupby(col, as_index=False)[["Overdue Value"]].sum()

    return {
        "rep": group(overdue,"Rep Code"),
        "manager": group(overdue,"Manager Code"),
        "area": group(overdue,"Area Code"),
        "supervisor": group(overdue,"Supervisor Code"),
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
        "Rep": "Rep Code",
        "Supervisor": "Supervisor Code",
        "Area": "Area Code",
        "Manager": "Manager Code"
    }

    df = data[key_map[filter_type]]

    return df[df[col_map[filter_type]] == value]


# =========================
# 🎨 UI
# =========================
st.set_page_config(layout="wide")
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

options = sales[filter_type.lower()][f"{filter_type} Code"].dropna().unique()

selected_value = st.sidebar.selectbox("Select", options)

# =========================
# 📊 OUTPUT
# =========================
st.header("💰 SALES")
st.dataframe(apply_filter(sales, filter_type, selected_value))

st.header("📦 OPENING")
st.dataframe(apply_filter(opening, filter_type, selected_value))

st.header("⏳ OVERDUE")
st.dataframe(apply_filter(overdue, filter_type, selected_value))
