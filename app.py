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
        "opening_detail": pd.read_excel("Opening Detail.xlsx", header=None),
    }


# =========================
# 🧠 SALES FIX
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
# 🎯 TARGET PIPELINE (FIXED PRODUCTS)
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()
    mapping.columns = mapping.columns.str.strip()

    if "Product Code" not in df.columns:
        df["Product Code"] = np.nan
    if "Product Name" not in df.columns:
        df["Product Name"] = np.nan
    if "Sales Price" not in df.columns:
        df["Sales Price"] = 0

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    mapping = mapping.drop_duplicates("Product Code")

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

    if "Product Name" in mapping.columns:
        df = df.merge(
            mapping[["Product Code", "Product Name"]],
            on="Product Code",
            how="left"
        )

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Value"] = df["Target (Unit)"] * df["Sales Price"]

    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    full = df.copy()
    month = df.copy()
    quarter = df.copy()
    ytd = df.copy()

    month["Value"] *= (current_month / 12)
    quarter["Value"] *= (current_quarter / 4)
    ytd["Value"] *= (current_month / 12)

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
# 💰 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, codes):

    sales = fix_sales_columns(sales)

    sales.columns = sales.columns.str.strip()
    codes.columns = codes.columns.str.strip()

    for col in ["Sales Unit Before Edit", "Returns Unit Before Edit", "Sales Price", "Invoice Discounts"]:
        sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="inner")

    if sales.empty:
        return {k: pd.DataFrame() for k in ["rep","manager","area","supervisor"]}

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    def group(df, col):
        return df.groupby(col, as_index=False)[
            ["Total Sales Value", "Returns Value", "Sales After Returns"]
        ].sum() if col in df.columns else pd.DataFrame()

    return {
        "rep": group(sales, "Rep Code"),
        "manager": group(sales, "Manager Code"),
        "area": group(sales, "Area Code"),
        "supervisor": group(sales, "Supervisor Code")
    }


# =========================
# 📦 OPENING PIPELINE
# =========================
def build_opening_pipeline(opening, codes):

    opening.columns = [
        'Branch',"Evak",'Opening Balance','Total Sales',
        'Returns','Sales Value Before Extra Discounts',
        'Cash Collection','Collection Checks',
        'Returned Chick','Collection Returned Chick',
        "Madinah",'Daienah','End Balance'
    ]

    opening["Rep Code"] = None
    mask = opening['Branch'].astype(str).str.strip() == "كود المندوب"
    opening.loc[mask, 'Rep Code'] = opening.loc[mask, 'Opening Balance']
    opening["Rep Code"] = opening["Rep Code"].ffill()

    opening = opening[
        opening['Branch'].notna() &
        (~opening['Branch'].astype(str).str.contains('كود|اجماليات', na=False))
    ]

    num_cols = ['Opening Balance','Total Sales','Returns','Cash Collection','Collection Checks','End Balance']
    for col in num_cols:
        opening[col] = pd.to_numeric(opening[col], errors="coerce").fillna(0)

    opening["Total Collection"] = opening["Cash Collection"] + opening["Collection Checks"]
    opening["Sales After Returns"] = opening["Total Sales"] - opening["Returns"]

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    opening = opening.merge(codes, on="Rep Code", how="left")

    def group(df, col):
        return df.groupby(col, as_index=False)[
            ["Total Sales Value", "Returns Value", "Sales After Returns", "Total Collection"]
        ].sum() if col in df.columns else pd.DataFrame()

    return {
        "rep": group(opening, "Rep Code"),
        "manager": group(opening, "Manager Code"),
        "area": group(opening, "Area Code"),
        "supervisor": group(opening, "Supervisor Code")
    }


# =========================
# 📦 OPENING DETAIL PIPELINE (NEW)
# =========================
def build_opening_detail_pipeline(opening_detail, codes):

    opening_detail = opening_detail.copy()
    codes = codes.copy()

    opening_detail.columns = [
        'Client Code',"Client Name",'Opening Balance',
        'Net Sales Before Extra Discounts', 'Returns',
        'Tasweyat Madinah', 'Total Collection',"Madfoaat",
        'Tasweyat Dainah', "End Balance",
        'Motalbet El Fatrah'
    ]

    opening_detail["Rep Code"] = None
    opening_detail["Old Rep Name"] = None

    mask = opening_detail['Client Code'].astype(str).str.strip() == "كود الفرع"

    opening_detail.loc[mask, 'Rep Code'] = opening_detail.loc[mask, 'Returns']
    opening_detail.loc[mask, 'Old Rep Name'] = opening_detail.loc[mask, 'Tasweyat Madinah']

    opening_detail[['Rep Code', 'Old Rep Name']] = opening_detail[['Rep Code', 'Old Rep Name']].ffill()

    opening_detail = opening_detail[
        opening_detail['Client Code'].notna() &
        (~opening_detail['Client Code'].astype(str).str.contains("كود الفرع|كود العميل", na=False))
    ]

    num_cols = [
        'Opening Balance','Net Sales Before Extra Discounts','Returns',
        'Tasweyat Madinah','Total Collection','Madfoaat',
        'Tasweyat Dainah','End Balance','Motalbet El Fatrah'
    ]

    for col in num_cols:
        if col in opening_detail.columns:
            opening_detail[col] = pd.to_numeric(opening_detail[col], errors="coerce").fillna(0)

    opening_detail["Sales After Returns"] = (
        opening_detail["Net Sales Before Extra Discounts"] - opening_detail["Returns"]
    )

    opening_detail["Rep Code"] = pd.to_numeric(opening_detail["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    opening_detail = opening_detail.merge(
        codes[['Rep Code',"Rep Name","Area Name","Area Code","Manager Name","Manager Code","Supervisor Code"]],
        on="Rep Code",
        how="left"
    )

    def group(df, col):
        return df.groupby(col, as_index=False)[
            ["Net Sales Before Extra Discounts","Returns","Sales After Returns","Total Collection"]
        ].sum() if col in df.columns else pd.DataFrame()

    return {
        "rep": group(opening_detail, "Rep Code"),
        "manager": group(opening_detail, "Manager Code"),
        "area": group(opening_detail, "Area Code"),
        "supervisor": group(opening_detail, "Supervisor Code")
    }


# =========================
# 🎨 STREAMLIT UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI System")

data = load_data()

# =========================
# 🎯 TARGET
# =========================
st.header("🎯 TARGET KPI")

target_rep = build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
target_manager = build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])
target_area = build_target_pipeline(data["target_area"], "Area Code", data["mapping"])
target_supervisor = build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"])

st.dataframe(target_rep["value_table"])
st.dataframe(target_manager["value_table"])
st.dataframe(target_area["value_table"])
st.dataframe(target_supervisor["value_table"])


# =========================
# 📦 PRODUCTS
# =========================
st.header("📦 PRODUCTS")

st.dataframe(target_rep["products_full"])
st.dataframe(target_manager["products_full"])
st.dataframe(target_area["products_full"])
st.dataframe(target_supervisor["products_full"])


# =========================
# 💰 SALES
# =========================
st.header("💰 SALES KPI")

sales = build_sales_pipeline(data["sales"], data["codes"])

st.dataframe(sales["rep"])
st.dataframe(sales["manager"])
st.dataframe(sales["area"])
st.dataframe(sales["supervisor"])


# =========================
# 📦 OPENING
# =========================
st.header("📦 OPENING KPI")

opening = build_opening_pipeline(data["opening"], data["codes"])

st.dataframe(opening["rep"])
st.dataframe(opening["manager"])
st.dataframe(opening["area"])
st.dataframe(opening["supervisor"])


# =========================
# 📦 OPENING DETAIL
# =========================
st.header("📦 OPENING DETAIL KPI")

opening_detail = build_opening_detail_pipeline(data["opening_detail"], data["codes"])

st.dataframe(opening_detail["rep"])
st.dataframe(opening_detail["manager"])
st.dataframe(opening_detail["area"])
st.dataframe(opening_detail["supervisor"])


# =========================
# ⏳ OVERDUE
# =========================
st.header("⏳ OVERDUE KPI")

overdue = build_overdue_pipeline(data["overdue"], data["codes"])

st.dataframe(overdue["rep"])
st.dataframe(overdue["manager"])
st.dataframe(overdue["area"])
st.dataframe(overdue["supervisor"])
