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
# 🧠 FIX SALES COLUMNS
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

    full = df.copy()
    month = df.copy()
    quarter = df.copy()
    ytd = df.copy()

    month["Value"] = month["Value"] * (current_month / 12)
    quarter["Value"] = quarter["Value"] * (current_quarter / 4)
    ytd["Value"] = ytd["Value"] * (current_month / 12)

    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = group(full).rename(columns={"Value": "Full Year 🏆"})
    value_table = value_table.merge(group(month).rename(columns={"Value": "Month 📅"}), on=id_name, how="left")
    value_table = value_table.merge(group(quarter).rename(columns={"Value": "Quarter 📊"}), on=id_name, how="left")
    value_table = value_table.merge(group(ytd).rename(columns={"Value": "YTD 📈"}), on=id_name, how="left")

    def product_group(d):
        if "Product Code" not in d.columns:
            d["Product Code"] = np.nan
        if "Product Name" not in d.columns:
            d["Product Name"] = "Unknown"

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

    if sales.empty:
        st.error("❌ مفيش تطابق بين Sales و Code")
        return {"rep": pd.DataFrame(), "manager": pd.DataFrame(),
                "area": pd.DataFrame(), "supervisor": pd.DataFrame()}

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    def group(df, col):
        if col not in df.columns:
            return pd.DataFrame()

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

    num_cols = [
        'Opening Balance','Total Sales','Returns',
        'Cash Collection','Collection Checks','End Balance'
    ]

    for col in num_cols:
        opening[col] = pd.to_numeric(opening[col], errors='coerce').fillna(0)

    opening['Total Collection'] = opening['Cash Collection'] + opening['Collection Checks']
    opening["Sales After Returns"] = opening["Total Sales"] - opening['Returns']

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    opening = opening.merge(codes, on='Rep Code', how='left')

    opening.rename(columns={
        "Total Sales": "Total Sales Value",
        "Returns": "Returns Value"
    }, inplace=True)

    def group(df, col):
        return df.groupby(col, as_index=False)[
            ["Total Sales Value", "Returns Value", "Sales After Returns", "Total Collection"]
        ].sum()

    return {
        "rep": group(opening, "Rep Code"),
        "manager": group(opening, "Manager Code"),
        "area": group(opening, "Area Code"),
        "supervisor": group(opening, "Supervisor Code")
    }


# =========================
# 🚀 OVERDUE PIPELINE
# =========================
def build_overdue_pipeline(overdue, codes):

    overdue = overdue.copy()
    codes = codes.copy()

    overdue.columns = [
        "Client Name", "Client Code", "30 Days", "60 Days", "90 Days", "120 Days",
        "150 Days", "More Than 150 Days", "Balance"
    ]

    overdue['Rep Code'] = None
    overdue['Old Rep Name'] = None

    mask = overdue['Client Name'].astype(str).str.strip() == "كود المندوب"

    overdue.loc[mask, 'Rep Code'] = overdue.loc[mask, 'Client Code']
    overdue.loc[mask, 'Old Rep Name'] = overdue.loc[mask, '30 Days']

    overdue[['Rep Code', 'Old Rep Name']] = overdue[['Rep Code', 'Old Rep Name']].ffill()

    overdue = overdue[
        overdue['Client Name'].notna() &
        (overdue['Client Name'].astype(str).str.strip() != '') &
        (~overdue['Client Name'].astype(str).str.contains(
            'اجمالــــــي التقرير|اجمالى الفرع/المندوب|كود الفرع|كود المندوب|اسم العميل',
            na=False
        ))
    ].copy()

    num_cols = [
        '30 Days','60 Days','90 Days','120 Days',
        '150 Days','More Than 150 Days','Client Code','Rep Code'
    ]

    for col in num_cols:
        overdue[col] = pd.to_numeric(overdue[col], errors='coerce').fillna(0)

    overdue['Rep Code'] = overdue['Rep Code'].astype(int)

    overdue['Overdue Value'] = (
        overdue['120 Days'] +
        overdue['150 Days'] +
        overdue['More Than 150 Days']
    )

    overdue['Total Balance'] = overdue[
        ['30 Days','60 Days','90 Days','120 Days','150 Days','More Than 150 Days']
    ].sum(axis=1)

    overdue = overdue.merge(
        codes[['Rep Code',"Rep Name","Area Name",'Area Code',
               "Manager Name","Manager Code","Supervisor Code"]],
        on='Rep Code',
        how='left'
    )

    def group(df, col):
        if col not in df.columns:
            return pd.DataFrame()

        return df.groupby(col, as_index=False)[
            ["Overdue Value", "Total Balance"]
        ].sum()

    return {
        "rep": group(overdue, "Rep Code"),
        "manager": group(overdue, "Manager Code"),
        "area": group(overdue, "Area Code"),
        "supervisor": group(overdue, "Supervisor Code")
    }


# =========================
# 🚀 OPENING DETAIL PIPELINE (FIXED)
# =========================
def build_opening_detail_pipeline(opening_detail):

    df = opening_detail.copy()

    expected_cols = [
        'Branch',"Evak",'Opening Balance','Total Sales',
        'Returned Sales','Sales Value Before Extra Discounts',
        'Cash Collection',"Blank1",'Collection Checks',
        "Blank2",'Returned Chick','Collection Returned Chick',
        "Madinah",'Daienah','End Balance'
    ]

    df = df.iloc[:, :len(expected_cols)].copy()
    df.columns = expected_cols

    df['Client Code'] = None
    df['Client Name'] = None

    mask = df['Branch'].astype(str).str.strip() == "كود العميل"
    df.loc[mask, 'Client Code'] = df.loc[mask, 'Evak']
    df.loc[mask, 'Client Name'] = df.loc[mask, 'Opening Balance']

    df[['Client Code', 'Client Name']] = df[['Client Code', 'Client Name']].ffill()

    df = df[
        df['Branch'].notna() &
        (df['Branch'].astype(str).str.strip() != '') &
        (~df['Branch'].astype(str).str.contains(
            'نسبة العميل|كود العميل|اجماليات|كود الفرع',
            na=False
        ))
    ].copy()

    num_cols = [
        'Opening Balance','Total Sales','Returned Sales','Sales Value Before Extra Discounts',
        'Cash Collection','Collection Checks','Returned Chick','Collection Returned Chick',
        'Madinah','Daienah','End Balance'
    ]

    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['Client Code'] = df['Client Code'].astype(str)
    df['Client Name'] = df['Client Name'].astype(str).str.strip()

    def group(d, col):
        return d.groupby(col, as_index=False)[
            [
                'Opening Balance',
                'Total Sales',
                'Returned Sales',
                'Cash Collection',
                'Collection Checks',
                'End Balance'
            ]
        ].sum()

    return {
        "client": group(df, "Client Code"),
        "client_name": group(df, "Client Name"),
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

opening_detail = data["opening_detail"]

opening_detail_result = build_opening_detail_pipeline(opening_detail)

st.dataframe(opening_detail_result["client"])
st.dataframe(opening_detail_result["client_name"])


# =========================
# ⏳ OVERDUE
# =========================
st.header("⏳ OVERDUE KPI")

overdue = build_overdue_pipeline(data["overdue"], data["codes"])

st.dataframe(overdue["rep"])
st.dataframe(overdue["manager"])
st.dataframe(overdue["area"])
st.dataframe(overdue["supervisor"])
