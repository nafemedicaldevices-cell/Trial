import pandas as pd
import numpy as np
import os

# =========================
# TARGETS
# =========================
FILES = {
    "Rep": "Target Rep.xlsx",
    "Manager": "Target Manager.xlsx",
    "Area": "Target Area.xlsx",
    "Supervisor": "Target Supervisor.xlsx",
    "Evak": "Target Evak.xlsx",
}

def load_targets():

    targets = {}

    for level, file in FILES.items():

        sheets = pd.read_excel(file, sheet_name=None)

        level_data = []

        for sheet_name, df in sheets.items():

            df.columns = df.columns.str.strip()

            fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]

            df = df.melt(
                id_vars=fixed_cols,
                var_name="Code",
                value_name="Target (Year)"
            )

            df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")

            df["Target (Unit)"] = df["Target (Year)"] / 12
            df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

            months = [
                "Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"
            ]

            df_long = df.loc[df.index.repeat(12)].copy()
            df_long["Month"] = months * len(df)

            df_long["Target (Unit)"] = df["Target (Unit)"].repeat(12).values
            df_long["Target (Value)"] = df["Target (Value)"].repeat(12).values

            df_long["Code"] = df_long["Code"].astype(str).str.strip()
            df_long["Level"] = level

            level_data.append(df_long)

        targets[level] = pd.concat(level_data, ignore_index=True)

    return targets


# =========================
# HARKA
# =========================
def load_haraka():

    df = pd.read_excel("Rep Harakah.xlsx")
    df = df.replace(r'^\s*$', pd.NA, regex=True)

    first_col = df.columns[0]
    df[first_col] = df[first_col].astype(str)

    df = df[
        df[first_col].notna() &
        (df[first_col].str.strip() != "") &
        (~df[first_col].str.contains("كود الفرع", na=False)) &
        (~df[first_col].str.contains("كود المندوب", na=False))
    ]

    df.columns = [
        "Rep Code","Old Rep Name","Opening Balance","Sales Value",
        "Returns Value","Credit","Total Collection",
        "Madfoaat","Debit","End Balance","Motalbet"
    ]

    df["Rep Code"] = df["Rep Code"].astype(str).str.strip()

    for col in df.columns[2:]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


# =========================
# BUILD FINAL TABLE
# =========================
def build_sales_vs_target(rep_target, sales_df):

    rep_target = rep_target.rename(columns={
        "Code": "Rep Code",
        "Product Code": "Product Code",
        "Old Product Name": "Product Name"
    })

    rep_target["Rep Code"] = rep_target["Rep Code"].astype(str).str.strip()
    sales_df["Rep Code"] = sales_df["Rep Code"].astype(str).str.strip()

    sales_agg = sales_df.groupby("Rep Code", as_index=False).agg({
        "Sales Value": "sum"
    })

    df = rep_target.merge(sales_agg, on="Rep Code", how="left")
    df["Sales Value"] = df["Sales Value"].fillna(0)

    df["Target Unit"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Target Value"] = pd.to_numeric(df["Target (Value)"], errors="coerce").fillna(0)

    df["Sales Unit"] = df["Sales Value"] / df["Sales Price"].replace(0, np.nan)
    df["Sales Unit"] = df["Sales Unit"].fillna(0)

    df["Achievement % (Unit)"] = np.where(
        df["Target Unit"] > 0,
        (df["Sales Unit"] / df["Target Unit"]) * 100,
        0
    )

    df["Achievement % (Value)"] = np.where(
        df["Target Value"] > 0,
        (df["Sales Value"] / df["Target Value"]) * 100,
        0
    )

    return df
