import pandas as pd
import numpy as np

def clean_target_file(file, level):

    df = pd.read_excel(file, sheet_name=0)
    df.columns = df.columns.str.strip()

    fixed_cols = [
        "Year",
        "Product Code",
        "Old Product Name",
        "Sales Price"
    ]

    df = df.melt(
        id_vars=fixed_cols,
        var_name="Code",
        value_name="Target (Year)"
    )

    df["Level"] = level
    df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")

    df["Target (Unit)"] = df["Target (Year)"] / 12
    df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    df_long = df.loc[df.index.repeat(12)].copy()
    df_long["Month"] = np.tile(months, len(df))

    df_long["Target (Unit)"] = np.repeat(df["Target (Unit)"].values, 12)
    df_long["Target (Value)"] = np.repeat(df["Target (Value)"].values, 12)

    return df_long
