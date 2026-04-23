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

    if "Sales Price" not in df.columns:
        df["Sales Price"] = 0

    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

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

    df["Value"] = df["Target (Unit)"] * df["Sales Price"]

    return df


# =========================
# 🚀 SALES PIPELINE (FIXED)
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
        if col in sales.columns:
            sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    # 🔥 FIX: بدل inner -> left عشان مايضيعش داتا
    sales = sales.merge(codes, on="Rep Code", how="left")

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

    def group(df, col):
        if col not in df.columns:
            return pd.DataFrame()

        return df.groupby(col, as_index=False)[
            ["Total Sales", "Returns", "Sales After Returns", "Total Collection"]
        ].sum()

    return {
        "rep": group(opening, "Rep Code"),
        "manager": group(opening, "Manager Code"),
        "area": group(opening, "Area Code"),
        "supervisor": group(opening, "Supervisor Code")
    }


# =========================
# 🚀 OVERDUE PIPELINE (FIXED)
# =========================
def build_overdue_pipeline(overdue, codes):

    overdue = overdue.copy()
    codes = codes.copy()

    overdue.columns = [
        "Client Name", "Client Code", "30 Days", "60 Days", "90 Days", "120 Days",
        "150 Days", "More Than 150 Days", "Balance"
    ]

    overdue["Rep Code"] = np.nan

    mask = overdue["Client Name"].astype(str).str.strip() == "كود المندوب"

    overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"]
    overdue["Rep Code"] = overdue["Rep Code"].ffill()

    num_cols = [
        '30 Days','60 Days','90 Days','120 Days',
        '150 Days','More Than 150 Days'
    ]

    for col in num_cols:
        overdue[col] = pd.to_numeric(overdue[col], errors="coerce").fillna(0)

    overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce")

    overdue["Overdue Value"] = overdue["120 Days"] + overdue["150 Days"] + overdue["More Than 150 Days"]

    overdue["Total Balance"] = overdue[num_cols].sum(axis=1)

    overdue = overdue.merge(codes, on="Rep Code", how="left")

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
# 🎨 STREAMLIT UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI System (Fixed)")

data = load_data()

# TARGET
st.header("🎯 TARGET")
st.dataframe(build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"]))

# SALES
st.header("💰 SALES")
sales = build_sales_pipeline(data["sales"], data["codes"])
st.dataframe(sales["rep"])
st.dataframe(sales["manager"])
st.dataframe(sales["area"])
st.dataframe(sales["supervisor"])

# OPENING
st.header("📦 OPENING")
opening = build_opening_pipeline(data["opening"], data["codes"])
st.dataframe(opening["rep"])

# OVERDUE
st.header("⏳ OVERDUE")
overdue = build_overdue_pipeline(data["overdue"], data["codes"])
st.dataframe(overdue["rep"])
