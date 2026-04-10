import pandas as pd
import numpy as np

# =========================
# LOAD DATA ONLY
# =========================
def load_data():

    sales = pd.read_excel("Sales.xlsx")
    overdue = pd.read_excel("Overdue.xlsx")
    extra_discounts = pd.read_excel("Extradiscounts.xlsx")
    opening = pd.read_excel("Opening.xlsx")
    opening_detail = pd.read_excel("Opening Detail.xlsx")

    target_manager = pd.read_excel("Target Manager.xlsx")
    target_area = pd.read_excel("Target Area.xlsx")
    target_rep = pd.read_excel("Target Rep.xlsx")

    mapping = pd.read_excel("Mapping.xlsx")
    codes = pd.read_excel("Code.xlsx")

    return {
        "sales": sales,
        "overdue": overdue,
        "extra_discounts": extra_discounts,
        "opening": opening,
        "opening_detail": opening_detail,
        "target_manager": target_manager,
        "target_area": target_area,
        "target_rep": target_rep,
        "mapping": mapping,
        "codes": codes
    }


def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip().str.replace(r"\s+", " ", regex=True)

    fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    df[id_name] = (
        df[id_name].astype(str)
        .str.replace(r"[^0-9]", "", regex=True)
    )

    df[id_name] = pd.to_numeric(df[id_name], errors="coerce")

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")

    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    df = df.merge(mapping, on="Product Code", how="left")

    df["Full Target Value"] = df["Target (Unit)"] * df["Sales Price"]

    return {
        "value_full": df.groupby([id_name], as_index=False)["Full Target Value"].sum(),
        "raw": df
    }
