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
# 🎯 TARGET PIPELINE
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

    df[id_name] = pd.to_numeric(df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True), errors="coerce")

    if "Product Name" in mapping.columns:
        df = df.merge(mapping[["Product Code", "Product Name"]], on="Product Code", how="left")

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
    }


# =========================
# 💰 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, codes):

    sales = sales.iloc[:, :10].copy()
    sales.columns = [
        'Date','Warehouse','Client Code','Client Name','Notes',
        'MF','Doc','Rep Code','Units','Price'
    ]

    for c in ["Units","Price"]:
        sales[c] = pd.to_numeric(sales[c], errors="coerce").fillna(0)

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="inner")

    if sales.empty:
        return {k: pd.DataFrame() for k in ["rep","manager","area","supervisor"]}

    sales["Value"] = sales["Units"] * sales["Price"]

    def group(df, col):
        return df.groupby(col, as_index=False)["Value"].sum() if col in df.columns else pd.DataFrame()

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

    opening = opening.copy()
    codes = codes.copy()

    opening.columns = [
        'Branch','A','Opening','Sales','Returns','B',
        'Cash','Check','C','Collection','D','E','End'
    ]

    opening["Rep Code"] = None
    mask = opening["Branch"].astype(str).str.strip() == "كود المندوب"
    opening.loc[mask, "Rep Code"] = opening.loc[mask, "Opening"]
    opening["Rep Code"] = opening["Rep Code"].ffill()

    opening = opening[opening["Branch"].notna()].copy()

    for c in ["Opening","Sales","Returns","Cash","Check","End"]:
        opening[c] = pd.to_numeric(opening[c], errors="coerce").fillna(0)

    opening["Total Collection"] = opening["Cash"] + opening["Check"]
    opening["Sales After Returns"] = opening["Sales"] - opening["Returns"]

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    opening = opening.merge(codes, on="Rep Code", how="left")

    def group(df, col):
        return df.groupby(col, as_index=False)[
            ["Sales","Returns","Sales After Returns","Total Collection"]
        ].sum() if col in df.columns else pd.DataFrame()

    return {
        "rep": group(opening, "Rep Code"),
        "manager": group(opening, "Manager Code"),
        "area": group(opening, "Area Code"),
        "supervisor": group(opening, "Supervisor Code")
    }


# =========================
# 📦 OPENING DETAIL PIPELINE
# =========================
def build_opening_detail_pipeline(opening_detail, codes):

    opening_detail = opening_detail.copy()
    codes = codes.copy()

    opening_detail.columns = [
        'Client Code','Client Name','Opening','Sales','Returns',
        'A','Collection','B','C','End','D'
    ]

    opening_detail["Rep Code"] = None
    mask = opening_detail["Client Code"].astype(str).str.contains("كود")
    opening_detail.loc[mask, "Rep Code"] = opening_detail.loc[mask, "Opening"]
    opening_detail["Rep Code"] = opening_detail["Rep Code"].ffill()

    opening_detail = opening_detail[opening_detail["Client Code"].notna()].copy()

    for c in ["Opening","Sales","Returns","Collection","End"]:
        opening_detail[c] = pd.to_numeric(opening_detail[c], errors="coerce").fillna(0)

    opening_detail["Sales After Returns"] = opening_detail["Sales"] - opening_detail["Returns"]

    opening_detail = opening_detail.merge(codes, on="Rep Code", how="left")

    def group(df, col):
        return df.groupby(col, as_index=False)[
            ["Sales","Returns","Sales After Returns","Collection"]
        ].sum() if col in df.columns else pd.DataFrame()

    return {
        "rep": group(opening_detail, "Rep Code"),
        "manager": group(opening_detail, "Manager Code"),
        "area": group(opening_detail, "Area Code"),
        "supervisor": group(opening_detail, "Supervisor Code")
    }


# =========================
# ⏳ OVERDUE PIPELINE
# =========================
def build_overdue_pipeline(overdue, codes):

    overdue = overdue.copy()
    codes = codes.copy()

    overdue.columns = [
        "Client Name","Client Code","30","60","90","120","150","150+","Balance"
    ]

    overdue["Rep Code"] = None
    mask = overdue["Client Name"].astype(str).str.contains("كود")
    overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"]
    overdue["Rep Code"] = overdue["Rep Code"].ffill()

    for c in overdue.columns:
        if c not in ["Client Name"]:
            overdue[c] = pd.to_numeric(overdue[c], errors="coerce").fillna(0)

    overdue["Overdue Value"] = overdue["120"] + overdue["150"] + overdue["150+"]

    overdue = overdue.merge(codes, on="Rep Code", how="left")

    def group(df, col):
        return df.groupby(col, as_index=False)[["Overdue Value","Balance"]].sum()

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
st.title("📊 Unified KPI System")

data = load_data()


# =========================
# 🎯 TARGET
# =========================
st.header("🎯 TARGET KPI")

target = build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])

st.dataframe(target["value_table"])


# =========================
# 📦 PRODUCTS
# =========================
st.header("📦 PRODUCTS")
st.dataframe(target["products_full"])


# =========================
# 💰 SALES
# =========================
st.header("💰 SALES KPI")

sales = build_sales_pipeline(data["sales"], data["codes"])
st.dataframe(sales["rep"])


# =========================
# 📦 OPENING
# =========================
st.header("📦 OPENING KPI")

opening = build_opening_pipeline(data["opening"], data["codes"])
st.dataframe(opening["rep"])


# =========================
# 📦 OPENING DETAIL
# =========================
st.header("📦 OPENING DETAIL KPI")

opening_detail = build_opening_detail_pipeline(data["opening_detail"], data["codes"])
st.dataframe(opening_detail["rep"])


# =========================
# ⏳ OVERDUE
# =========================
st.header("⏳ OVERDUE KPI")

overdue = build_overdue_pipeline(data["overdue"], data["codes"])
st.dataframe(overdue["rep"])
