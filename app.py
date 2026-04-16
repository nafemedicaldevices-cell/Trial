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

        "sales": pd.read_excel("Sales.xlsx", header=None),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx"),

        "opening": pd.read_excel("Opening.xlsx", header=None),
        "opening_detail": pd.read_excel("Opening Detail.xlsx", header=None),
        "overdue": pd.read_excel("Overdue.xlsx", header=None),
    }


# =========================
# 🧠 SALES FIX
# =========================
def fix_sales_columns(sales):
    cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]
    sales = sales.iloc[:, :len(cols)].copy()
    sales.columns = cols
    return sales


# =========================
# 🚀 TARGET PIPELINE
# =========================
def build_target_pipeline(df, id_name):

    df = df.copy()

    df.columns = df.columns.str.strip()

    if "Sales Price" not in df.columns:
        df["Sales Price"] = 0

    fixed_cols = [c for c in ["Year", "Product Code", "Old Product Name", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Value"] = df["Target (Unit)"] * df["Sales Price"]

    def g(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    full = g(df).rename(columns={"Value": "Full Year 🏆"})

    return full


# =========================
# 🚀 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, codes):

    sales = fix_sales_columns(sales)

    for c in ["Sales Unit Before Edit", "Returns Unit Before Edit", "Sales Price"]:
        sales[c] = pd.to_numeric(sales[c], errors="coerce").fillna(0)

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="inner")

    if sales.empty:
        return {"rep": pd.DataFrame()}

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    def g(df, col):
        return df.groupby(col, as_index=False)[
            ["Total Sales Value", "Returns Value", "Sales After Returns"]
        ].sum()

    return {
        "rep": g(sales, "Rep Code"),
        "manager": g(sales, "Manager Code"),
        "area": g(sales, "Area Code"),
        "supervisor": g(sales, "Supervisor Code")
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

    opening["Rep Code"] = None
    mask = opening["Branch"].astype(str).str.strip() == "كود المندوب"
    opening.loc[mask, "Rep Code"] = opening.loc[mask, "Opening Balance"]
    opening["Rep Code"] = opening["Rep Code"].ffill()

    opening = opening[~opening["Branch"].astype(str).str.contains("كود|اجماليات", na=False)]

    num_cols = [
        "Opening Balance","Total Sales","Returns",
        "Cash Collection","Collection Checks","End Balance"
    ]

    for c in num_cols:
        opening[c] = pd.to_numeric(opening[c], errors="coerce").fillna(0)

    opening["Total Collection"] = opening["Cash Collection"] + opening["Collection Checks"]

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    opening = opening.merge(codes, on="Rep Code", how="left")

    def g(df, col):
        return df.groupby(col, as_index=False)[
            ["Total Sales", "Returns", "Cash Collection", "Collection Checks", "End Balance"]
        ].sum()

    return {
        "rep": g(opening, "Rep Code"),
        "manager": g(opening, "Manager Code"),
        "area": g(opening, "Area Code"),
        "supervisor": g(opening, "Supervisor Code")
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

    df["Client Code"] = None
    df["Client Name"] = None

    mask = df["Branch"].astype(str).str.strip() == "كود العميل"
    df.loc[mask, "Client Code"] = df.loc[mask, "Evak"]
    df.loc[mask, "Client Name"] = df.loc[mask, "Opening Balance"]

    df[["Client Code","Client Name"]] = df[["Client Code","Client Name"]].ffill()

    df = df[~df["Branch"].astype(str).str.contains("كود|اجماليات", na=False)]

    num_cols = [
        "Opening Balance","Total Sales","Returned Sales",
        "Cash Collection","Collection Checks","End Balance"
    ]

    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    def g(d, col):
        return d.groupby(col, as_index=False)[
            ["Opening Balance","Total Sales","Returned Sales","Cash Collection","Collection Checks","End Balance"]
        ].sum()

    return {
        "client": g(df, "Client Code"),
        "client_name": g(df, "Client Name")
    }


# =========================
# 🚀 OVERDUE PIPELINE
# =========================
def build_overdue_pipeline(overdue, codes):

    overdue.columns = [
        "Client Name","Client Code","30","60","90","120","150","150+","Balance"
    ]

    overdue["Rep Code"] = None

    mask = overdue["Client Name"].astype(str).str.strip() == "كود المندوب"
    overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"]
    overdue["Rep Code"] = overdue["Rep Code"].ffill()

    num_cols = ["30","60","90","120","150","150+","Client Code","Rep Code"]

    for c in num_cols:
        overdue[c] = pd.to_numeric(overdue[c], errors="coerce").fillna(0)

    overdue["Overdue Value"] = overdue["120"] + overdue["150"] + overdue["150+"]

    overdue["Total Balance"] = overdue[["30","60","90","120","150","150+"]].sum(axis=1)

    overdue = overdue.merge(codes, on="Rep Code", how="left")

    def g(df, col):
        return df.groupby(col, as_index=False)[["Overdue Value","Total Balance"]].sum()

    return {
        "rep": g(overdue, "Rep Code"),
        "manager": g(overdue, "Manager Code"),
        "area": g(overdue, "Area Code"),
        "supervisor": g(overdue, "Supervisor Code")
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

st.dataframe(build_target_pipeline(data["target_rep"], "Rep Code"))
st.dataframe(build_target_pipeline(data["target_manager"], "Manager Code"))
st.dataframe(build_target_pipeline(data["target_area"], "Area Code"))
st.dataframe(build_target_pipeline(data["target_supervisor"], "Supervisor Code"))


# =========================
# 📦 SALES
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
od = build_opening_detail_pipeline(data["opening_detail"])
st.dataframe(od["client"])
st.dataframe(od["client_name"])


# =========================
# ⏳ OVERDUE
# =========================
st.header("⏳ OVERDUE KPI")
overdue = build_overdue_pipeline(data["overdue"], data["codes"])
st.dataframe(overdue["rep"])
st.dataframe(overdue["manager"])
st.dataframe(overdue["area"])
st.dataframe(overdue["supervisor"])
