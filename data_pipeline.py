import pandas as pd
import numpy as np

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
# 🚀 TARGET PIPELINE
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

    # clean ids
    df[id_name] = pd.to_numeric(
        df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True),
        errors="coerce"
    )

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    mapping = mapping.drop_duplicates("Product Code")

    df = df.merge(mapping, on="Product Code", how="left")

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Full Value"] = df["Target (Unit)"] * df["Sales Price"]

    def calc(df_in, factor):
        tmp = df_in.copy()
        tmp["Value"] = tmp["Full Value"] * (factor / 12)
        return tmp

    df_full = calc(df, 12)
    df_month = calc(df, 1)
    df_quarter = calc(df, current_quarter * 3)
    df_ytd = calc(df, current_month)

    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    def products(d):
        return d.groupby(
            [id_name, "Product Code", "Product Name"],
            as_index=False
        )[["Target (Unit)", "Value"]].sum()

    return {
        "value_table": pd.DataFrame({
            id_name: group(df_full)[id_name],
            "Full Year": group(df_full)["Value"],
            "Month": group(df_month)["Value"],
            "Quarter": group(df_quarter)["Value"],
            "YTD": group(df_ytd)["Value"],
        }),
        "products_full": products(df_full),
        "products_month": products(df_month),
        "products_quarter": products(df_quarter),
        "products_ytd": products(df_ytd),
    }


# =========================
# 📊 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    mapping = mapping.copy()
    codes = codes.copy()

    sales.columns = sales.columns.str.strip()

    num_cols = [
        'Sales Unit Before Edit',
        'Returns Unit Before Edit',
        'Sales Price',
        'Invoice Discounts',
        'Sales Value'
    ]

    for c in num_cols:
        if c in sales.columns:
            sales[c] = pd.to_numeric(sales[c], errors="coerce").fillna(0)

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]

    sales["Net Sales Value"] = sales["Total Sales Value"] - sales["Returns Value"]

    sales["Net Units"] = sales["Sales Unit Before Edit"] - sales["Returns Unit Before Edit"]

    # FIX IDS
    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="left")

    def group(df, key):
        return df.groupby([key], as_index=False)[
            ["Total Sales Value", "Returns Value", "Net Sales Value", "Net Units"]
        ].sum()

    def group_products(df, key):
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
