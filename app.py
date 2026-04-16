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

        # ✅ NEW
        "opening": pd.read_excel("Opening.xlsx", header=None),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx"),
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

    if "Product Code" not in df.columns:
        df["Product Code"] = np.nan

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

    df = df.merge(mapping, on="Product Code", how="left")

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Value"] = df["Target (Unit)"] * df["Sales Price"]

    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    return {
        "value_table": group(df),
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
        return {"rep": pd.DataFrame()}

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    return {
        "rep": sales.groupby("Rep Code", as_index=False)[
            ["Total Sales Value", "Returns Value", "Sales After Returns"]
        ].sum()
    }


# =========================
# 🚀 OPENING PIPELINE
# =========================
def build_opening_pipeline(opening, codes):

    opening = opening.copy()

    # 🧹 rename
    opening = opening.iloc[:, :13]
    opening.columns = [
        'Branch',"Evak",'Opening Balance','Total Sales',
        'Returns','Sales Value Before Extra Discounts',
        'Cash Collection','Collection Checks',
        'Returned Chick','Collection Returned Chick',
        "Madinah",'Daienah','End Balance'
    ]

    # 🧠 extract rep
    opening['Rep Code'] = None
    mask = opening['Branch'].astype(str).str.strip() == "كود المندوب"
    opening.loc[mask, 'Rep Code'] = opening.loc[mask, 'Opening Balance']
    opening['Rep Code'] = opening['Rep Code'].ffill()

    # 🧹 filter
    opening = opening[
        opening['Branch'].notna() &
        (~opening['Branch'].astype(str).str.contains('كود المندوب|اجماليات', na=False))
    ]

    # 🔢 numeric
    num_cols = [
        'Opening Balance','Total Sales','Returns',
        'Cash Collection','Collection Checks','End Balance'
    ]

    for col in num_cols:
        opening[col] = pd.to_numeric(opening[col], errors="coerce").fillna(0)

    # ➕ calc
    opening['Total Collection'] = opening['Cash Collection'] + opening['Collection Checks']
    opening["Sales After Returns"] = opening["Total Sales"] - opening['Returns']

    # 🔗 merge
    opening['Rep Code'] = pd.to_numeric(opening['Rep Code'], errors="coerce")
    codes['Rep Code'] = pd.to_numeric(codes['Rep Code'], errors="coerce")

    opening = opening.merge(codes, on='Rep Code', how='left')

    # 📊 group
    rep = opening.groupby('Rep Code', as_index=False)[
        ['Opening Balance','Total Sales','Returns','Sales After Returns','Total Collection','End Balance']
    ].sum()

    return {
        "rep": rep,
        "full": opening
    }


# =========================
# 🎨 UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI System")

data = load_data()

# TARGET
st.header("🎯 TARGET KPI")
target_rep = build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
st.dataframe(target_rep["value_table"])

# SALES
st.header("💰 SALES KPI")
sales = build_sales_pipeline(data["sales"], data["codes"])
st.dataframe(sales["rep"])

# OPENING
st.header("💵 COLLECTION KPI")
opening = build_opening_pipeline(data["opening"], data["codes"])

st.subheader("Rep Collection")
st.dataframe(opening["rep"], use_container_width=True)

# DEBUG (احذفها بعد ما تتأكد)
st.subheader("🔍 Debug Opening Data")
st.dataframe(opening["full"])
