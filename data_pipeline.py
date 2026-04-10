import pandas as pd

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

import pandas as pd
import numpy as np

def build_target_pipeline(file_name, id_name, mapping):

    current_month = pd.Timestamp.today().month

    df = pd.read_excel(file_name)

    df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

    fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    df[id_name] = (
        df[id_name].astype(str).str.replace(r'[^0-9]', '', regex=True)
    )
    df[id_name] = pd.to_numeric(df[id_name], errors='coerce').astype('Int64')

    for col in ["Target (Unit)", "Sales Price", "Product Code"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True),
            errors='coerce'
        ).fillna(0)

    mapping_clean = mapping.copy()
    mapping_clean["Product Code"] = pd.to_numeric(
        mapping_clean["Product Code"].astype(str).str.replace(r'[^0-9.]','', regex=True),
        errors='coerce'
    ).fillna(0).astype(int)

    mapping_clean = mapping_clean.drop_duplicates("Product Code")

    df["Product Code"] = df["Product Code"].astype(int)

    df = df.merge(
        mapping_clean[[
            "Product Code", "Product Name", "2 Classification", "Category"
        ]],
        on="Product Code",
        how="left"
    )

    df["Full Target Value"] = df["Target (Unit)"] * df["Sales Price"]

    def add_target_value(base_df, factor):
        temp = base_df.copy()
        temp["Target (Value)"] = (temp["Full Target Value"] / 12) * factor
        return temp

    df_full = add_target_value(df, 12)
    df_month = add_target_value(df, 1)
    df_quarter = add_target_value(df, 3)
    df_ytd = add_target_value(df, current_month)

    def value(df_in):
        return df_in.groupby([id_name], as_index=False)["Target (Value)"].sum()

    def products(df_in):
        return df_in.groupby(
            [
                id_name,
                "2 Classification",
                "Category",
                "Product Code",
                "Product Name",
                "Target (Unit)",
                "Sales Price"
            ],
            as_index=False
        )["Target (Value)"].sum()

    return {
        "full": df,
        "value_full": value(df_full),
        "value_month": value(df_month),
        "value_quarter": value(df_quarter),
        "value_uptodate": value(df_ytd),

        "products_full": products(df_full),
        "products_month": products(df_month),
        "products_quarter": products(df_quarter),
        "products_uptodate": products(df_ytd),
    }
