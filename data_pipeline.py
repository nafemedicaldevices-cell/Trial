import pandas as pd
import numpy as np

# =========================
# 📂 LOAD DATA
# =========================
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx"),
        "overdue": pd.read_excel("Overdue.xlsx"),
        "extra_discounts": pd.read_excel("Extradiscounts.xlsx"),
        "opening": pd.read_excel("Opening.xlsx"),
        "opening_detail": pd.read_excel("Opening Detail.xlsx"),

        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx")
    }


# =========================
# 🎯 TARGET PIPELINE
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()

    fixed_cols = [c for c in ["Year", "Product Code", "Old Product Name", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    df[id_name] = pd.to_numeric(df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True), errors="coerce")
    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    mapping = mapping.drop_duplicates("Product Code")

    df = df.merge(mapping, on="Product Code", how="left")

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Full Value"] = df["Target (Unit)"] * df["Sales Price"]

    def group(d):
        return d.groupby([id_name], as_index=False)["Full Value"].sum()

    return {
        "value_table": group(df),
        "products_full": df.groupby(
            [id_name, "Product Code", "Product Name"],
            as_index=False
        )["Full Value"].sum()
    }


# =========================
# 💰 SALES PIPELINE (FIXED)
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    mapping = mapping.copy()
    codes = codes.copy()

    sales.columns = sales.columns.str.strip()

    # 🔢 numeric fix
    for c in [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price"
    ]:
        if c in sales.columns:
            sales[c] = pd.to_numeric(sales[c], errors="coerce").fillna(0)

    # 💰 KPIs
    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Net Sales Value"] = sales["Total Sales Value"] - sales["Returns Value"]
    sales["Net Units"] = sales["Sales Unit Before Edit"] - sales["Returns Unit Before Edit"]

    # 🔑 FIX IDS
    if "Rep Code" in sales.columns:
        sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")

    if "Manager Code" in sales.columns:
        sales["Manager Code"] = pd.to_numeric(sales["Manager Code"], errors="coerce")

    if "Area Code" in sales.columns:
        sales["Area Code"] = pd.to_numeric(sales["Area Code"], errors="coerce")

    if "Supervisor Code" in sales.columns:
        sales["Supervisor Code"] = pd.to_numeric(sales["Supervisor Code"], errors="coerce")

    # 🔗 merge codes
    if "Rep Code" in sales.columns:
        codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")
        sales = sales.merge(codes, on="Rep Code", how="left")

    # =========================
    # 📊 GROUP FUNCTION
    # =========================
    def group(df, key):
        if key not in df.columns:
            return pd.DataFrame()
        return df.groupby([key], as_index=False)[
            ["Total Sales Value", "Returns Value", "Net Sales Value", "Net Units"]
        ].sum()

    def group_products(df, key):
        if key not in df.columns:
            return pd.DataFrame()
        return df.groupby(
            [key, "Product Code", "Product Name"],
            as_index=False
        )[["Net Sales Value", "Net Units"]].sum()

    return {
        "rep_value": group(sales, "Rep Code"),
        "manager_value": group(sales, "Manager Code"),
        "area_value": group(sales, "Area Code"),
        "supervisor_value": group(sales, "Supervisor Code"),

        "rep_products": group_products(sales, "Rep Code"),
        "manager_products": group_products(sales, "Manager Code"),
        "area_products": group_products(sales, "Area Code"),

        "raw": sales
    }
