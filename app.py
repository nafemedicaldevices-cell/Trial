import pandas as pd
import numpy as np
import streamlit as st

# =========================
# 📅 TIME SETTINGS
# =========================
today = pd.Timestamp.today()
current_month = today.month
current_quarter = (current_month - 1) // 3 + 1


# =========================
# 📂 LOAD DATA (CACHE FIX)
# =========================
@st.cache_data
def load_data():
    return {
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),

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

    if "Sales Price" not in df.columns:
        df["Sales Price"] = 0

    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    # Melt
    fixed_cols = [c for c in ["Year", "Product Code", "Old Product Name", "Sales Price"] if c in df.columns]
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

    # mapping fix
    if "Product Name" in mapping.columns:
        df = df.merge(
            mapping[["Product Code", "Product Name"]].drop_duplicates(),
            on="Product Code",
            how="left"
        )

    df["Value"] = df["Target (Unit)"] * df["Sales Price"]

    # KPI scaling (FIXED LOGIC)
    full = df.copy()
    month = df.copy()
    quarter = df.copy()
    ytd = df.copy()

    month["Value"] *= current_month / 12
    quarter["Value"] *= current_quarter / 4
    ytd["Value"] *= current_month / 12

    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = group(full).rename(columns={"Value": "Full Year 🏆"})
    value_table = value_table.merge(group(month).rename(columns={"Value": "Month 📅"}), on=id_name, how="left")
    value_table = value_table.merge(group(quarter).rename(columns={"Value": "Quarter 📊"}), on=id_name, how="left")
    value_table = value_table.merge(group(ytd).rename(columns={"Value": "YTD 📈"}), on=id_name, how="left")

    def product_group(d):
        return d.groupby(
            [id_name, "Product Code", "Product Name"],
            as_index=False
        ).agg(
            Units=("Target (Unit)", "sum"),
            Value=("Value", "sum")
        )

    return {
        "value_table": value_table,
        "products_full": product_group(full),
        "products_month": product_group(month),
        "products_quarter": product_group(quarter),
        "products_ytd": product_group(ytd),
    }


# =========================
# 🚀 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, codes):

    sales = fix_sales_columns(sales)

    sales = sales.merge(codes, on="Rep Code", how="left")

    if sales.empty:
        st.error("❌ No matching between Sales and Codes")
        return {}

    for col in [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price"
    ]:
        sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Net Sales"] = sales["Total Sales Value"] - sales["Returns Value"]

    def group(col):
        if col not in sales.columns:
            return pd.DataFrame()

        return sales.groupby(col, as_index=False)[
            ["Total Sales Value", "Returns Value", "Net Sales"]
        ].sum()

    return {
        "rep": group("Rep Code"),
        "manager": group("Manager Code"),
        "area": group("Area Code"),
        "supervisor": group("Supervisor Code")
    }


# =========================
# 🚀 OPENING PIPELINE (SAFE)
# =========================
def build_opening_pipeline(opening, codes):

    cols = [
        'Branch',"Evak",'Opening Balance','Total Sales',
        'Returns','Sales Value Before Extra Discounts',
        'Cash Collection','Collection Checks',
        'Returned Chick','Collection Returned Chick',
        "Madinah",'Daienah','End Balance'
    ]

    opening = opening.copy()
    opening = opening.iloc[:, :len(cols)]
    opening.columns = cols

    mask = opening['Branch'].astype(str).str.contains("كود المندوب", na=False)

    opening['Rep Code'] = np.nan
    opening.loc[mask, 'Rep Code'] = opening.loc[mask, 'Opening Balance']
    opening['Rep Code'] = opening['Rep Code'].ffill()

    num_cols = [
        'Opening Balance','Total Sales','Returns',
        'Cash Collection','Collection Checks','End Balance'
    ]

    for c in num_cols:
        opening[c] = pd.to_numeric(opening[c], errors="coerce").fillna(0)

    opening["Net Sales"] = opening["Total Sales"] - opening["Returns"]
    opening["Total Collection"] = opening["Cash Collection"] + opening["Collection Checks"]

    opening = opening.merge(codes, on="Rep Code", how="left")

    def group(col):
        return opening.groupby(col, as_index=False)[
            ["Total Sales", "Returns", "Net Sales", "Total Collection"]
        ].sum()

    return {
        "rep": group("Rep Code"),
        "manager": group("Manager Code"),
        "area": group("Area Code"),
        "supervisor": group("Supervisor Code")
    }


# =========================
# 🚀 STREAMLIT UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI System")

data = load_data()

st.header("🎯 TARGET KPI")

target_rep = build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])

st.dataframe(target_rep["value_table"])
st.dataframe(target_rep["products_full"])


st.header("💰 SALES KPI")

sales = build_sales_pipeline(data["sales"], data["codes"])

st.dataframe(sales["rep"])


st.header("📦 OPENING KPI")

opening = build_opening_pipeline(data["opening"], data["codes"])

st.dataframe(opening["rep"])
