import pandas as pd
import numpy as np

current_month = pd.Timestamp.today().month


# =========================
# LOAD DATA
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
# TARGET PIPELINE (ALL LEVELS)
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

    # clean IDs
    df[id_name] = pd.to_numeric(
        df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True),
        errors="coerce"
    )

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    mapping = mapping.drop_duplicates("Product Code")

    df = df.merge(mapping, on="Product Code", how="left")

    # numeric cleanup
    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Full Target Value"] = df["Target (Unit)"] * df["Sales Price"]

    # KPI helper
    def add(df_in, factor):
        tmp = df_in.copy()
        tmp["Target (Value)"] = (tmp["Full Target Value"] / 12) * factor
        return tmp

    df_full = add(df, 12)
    df_month = add(df, 1)
    df_quarter = add(df, 3)
    df_ytd = add(df, current_month)

    # group
    def group(d):
        return d.groupby([id_name], as_index=False)["Target (Value)"].sum()

    def group_products(d):
        cols = [id_name, "Product Code"]
        if "Product Name" in d.columns:
            cols.append("Product Name")

        return d.groupby(cols, as_index=False)["Target (Value)"].sum()

    return {
        "raw": df,
        "value_full": group(df_full),
        "value_month": group(df_month),
        "value_quarter": group(df_quarter),
        "value_uptodate": group(df_ytd),
        "products_full": group_products(df_full),
        "products_uptodate": group_products(df_ytd)
    }
