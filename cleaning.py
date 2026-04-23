import pandas as pd
import numpy as np

FILES = {
    "Rep": "Target Rep.xlsx",
    "Manager": "Target Manager.xlsx",
    "Area": "Target Area.xlsx",
    "Supervisor": "Target Supervisor.xlsx",
    "Evak": "Target Evak.xlsx",
}

def load_and_process_data():

    all_data = []

    for level, file in FILES.items():

        df = pd.read_excel(file, sheet_name=0)
        df.columns = df.columns.str.strip()

        # =========================
        # 🔥 CASE 1: Rep (Rep Harakah مختلف)
        # =========================
        if level == "Rep":

            df = df.iloc[2:].reset_index(drop=True)
            df = df.dropna(how="all")

            if "Rep Code" in df.columns:
                df = df[df["Rep Code"].notna()]

            df["Level"] = level

            # لازم يكون فيه Target (Year)
            if "Target (Year)" not in df.columns:
                continue

        # =========================
        # 🔥 CASE 2: باقي الملفات
        # =========================
        else:

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

        # =========================
        # 🧹 CLEAN
        # =========================
        df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")

        # =========================
        # 📊 CALCULATIONS
        # =========================
        df["Target (Unit)"] = df["Target (Year)"] / 12
        df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

        # =========================
        # 📅 MONTHS
        # =========================
        months = [
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ]

        df_long = df.loc[df.index.repeat(12)].copy()
        df_long["Month"] = np.tile(months, len(df))

        df_long["Target (Unit)"] = np.repeat(df["Target (Unit)"].values, 12)
        df_long["Target (Value)"] = np.repeat(df["Target (Value)"].values, 12)

        all_data.append(df_long)

    return pd.concat(all_data, ignore_index=True)
