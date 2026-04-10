import pandas as pd
import numpy as np

# =========================
# 📂 LOAD DATA
# =========================
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx"),
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),
        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx")
    }


# =========================
# 🎯 TARGET PIPELINE (VALUE ONLY)
# =========================
def build_target(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()

    fixed_cols = [c for c in ["Year", "Product Code", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target Units"
    )

    df[id_name] = pd.to_numeric(df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True), errors="coerce")
    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")

    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")
    mapping = mapping.drop_duplicates("Product Code")

    df = df.merge(mapping, on="Product Code", how="left")

    df["Target Units"] = pd.to_numeric(df["Target Units"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Target Value"] = df["Target Units"] * df["Sales Price"]

    return df.groupby([id_name], as_index=False)["Target Value"].sum()


# =========================
# 💰 SALES PIPELINE
# =========================
def build_sales(df):

    df = df.copy()
    df.columns = df.columns.str.strip()

    for c in [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price",
        "Invoice Discounts"
    ]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["Total Sales Value"] = df["Sales Unit Before Edit"] * df["Sales Price"]
    df["Returns Value"] = df["Returns Unit Before Edit"] * df["Sales Price"]
    df["Sales After Returns"] = df["Total Sales Value"] - df["Returns Value"]

    return df


# =========================
# 📊 FINAL VALUE TABLE (MERGED)
# =========================
def build_kpi(data):

    sales = build_sales(data["sales"])

    def group_sales(col):
        return sales.groupby(col, as_index=False).agg({
            "Total Sales Value": "sum",
            "Returns Value": "sum",
            "Sales After Returns": "sum",
            "Invoice Discounts": "sum"
        })

    def build_level(df_target, key):
        target = build_target(df_target, key, data["mapping"])

        sales_value = group_sales(key)

        return target.merge(sales_value, on=key, how="left").fillna(0)

    return {
        "rep": build_level(data["target_rep"], "Rep Code"),
        "manager": build_level(data["target_manager"], "Manager Code"),
        "area": build_level(data["target_area"], "Area Code"),
        "supervisor": build_level(data["target_supervisor"], "Supervisor Code"),
        "evak": build_level(data["target_evak"], "Evak Code"),
    }
