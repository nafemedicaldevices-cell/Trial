import pandas as pd
import numpy as np

# =========================
# 📅 TIME SETTINGS
# =========================
current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1
past_quarters = max(current_quarter - 1, 0)


# =========================
# 📂 LOAD DATA
# =========================
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx"),
        "target_rep": pd.read_excel("Target Rep.xlsx"),
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

    full = df.copy()
    full["Value"] = full["Full Value"]

    month = df.copy()
    month["Value"] = full["Full Value"] * (current_month / 12)

    quarter = df.copy()
    quarter["Value"] = full["Full Value"] * (past_quarters / 4)

    ytd = df.copy()
    ytd["Value"] = full["Full Value"] * (current_month / 12)

    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = group(full).rename(columns={"Value": "Full Year 🏆"})
    value_table["Month 📅"] = group(month)["Value"]
    value_table["Quarter 📊"] = group(quarter)["Value"]
    value_table["YTD 📈"] = group(ytd)["Value"]

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
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    sales.columns = sales.columns.str.strip()

    expected_cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]

    if len(sales.columns) == len(expected_cols):
        sales.columns = expected_cols

    sales = sales[sales['Date'].notna()].copy()

    num_cols = [
        'Sales Unit Before Edit',
        'Returns Unit Before Edit',
        'Sales Price',
        'Invoice Discounts',
        'Sales Value'
    ]

    for col in num_cols:
        if col in sales.columns:
            sales[col] = pd.to_numeric(sales[col], errors='coerce').fillna(0)

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce").astype("Int64")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce").astype("Int64")

    sales = sales.merge(mapping, on="Old Product Code", how="left")
    sales = sales.merge(codes, on="Rep Code", how="left")

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    sales["Net Sales Unit"] = (
        (sales["Sales Unit Before Edit"] - sales["Returns Unit Before Edit"])
        * sales["Next Factor"]
    )

    def safe_group(df, group_cols, sum_cols):
        group_cols = [c for c in group_cols if c in df.columns]
        sum_cols = [c for c in sum_cols if c in df.columns]
        return df.groupby(group_cols, as_index=False)[sum_cols].sum()

    return {
        "rep_value": safe_group(sales, ["Rep Code"], ["Total Sales Value","Returns Value","Sales After Returns"]),
        "manager_value": safe_group(sales, ["Manager Code"], ["Total Sales Value","Returns Value","Sales After Returns"]),
        "area_value": safe_group(sales, ["Area Code"], ["Total Sales Value","Returns Value","Sales After Returns"]),
        "rep_products": safe_group(sales, ["Rep Code","Product Code","Product Name"], ["Sales Value","Net Sales Unit"]),
    }
