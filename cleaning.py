# clean_data.py
import pandas as pd
import numpy as np

files = {
    "Rep": "Target Rep.xlsx",
    "Manager": "Target Manager.xlsx",
    "Area": "Target Area.xlsx",
    "Supervisor": "Target Supervisor.xlsx",
    "Evak": "Target Evak.xlsx",
}

def load_and_process_data():

    all_data = []

    for level, file in files.items():

        df = pd.read_excel(file)
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

        df["Target (Unit") = df["Target (Year)"] / 12
        df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

        months = [
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ]

        df_long = df.loc[df.index.repeat(12)].copy()
        df_long["Month"] = np.tile(months, len(df))

        df_long["Target (Unit)"] = np.repeat(df["Target (Unit)"].values, 12)
        df_long["Target (Value)"] = np.repeat(df["Target (Value)"].values, 12)

        all_data.append(df_long)

    final_df = pd.concat(all_data, ignore_index=True)

    final_df = final_df[
        [
            "Level",
            "Code",
            "Year",
            "Month",
            "Product Code",
            "Old Product Name",
            "Sales Price",
            "Target (Year)",
            "Target (Unit)",
            "Target (Value)"
        ]
    ]

    return final_df
