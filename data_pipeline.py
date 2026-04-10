import pandas as pd
import numpy as np


# =========================
# 📥 LOAD ALL SHEETS
# =========================
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx"),

        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx")
    }


# =========================
# 🧼 CLEAN COLUMNS
# =========================
def clean_cols(df):
    df = df.copy()
    df.columns = df.columns.str.strip()
    return df


# =========================
# 🎯 TARGET PIPELINE
# =========================
def build_target(df, key_col):

    df = clean_cols(df)

    if key_col in df.columns:
        df[key_col] = df[key_col].astype(str)

    for c in df.columns:
        if "Target" in c:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    return df


# =========================
# 💰 SALES PIPELINE
# =========================
def build_sales(df, mapping, codes):

    df = clean_cols(df)

    # =========================
    # SAFE NUMERIC
    # =========================
    num_cols = [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price",
        "Invoice Discounts"
    ]

    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
        else:
            df[c] = 0


    # =========================
    # CALCULATIONS
    # =========================
    df["Total Sales Value"] = df["Sales Unit Before Edit"] * df["Sales Price"]
    df["Returns Value"] = df["Returns Unit Before Edit"] * df["Sales Price"]
    df["Sales After Returns"] = df["Total Sales Value"] - df["Returns Value"]


    # =========================
    # SAFE KEYS
    # =========================
    if "Rep Code" not in df.columns:
        df["Rep Code"] = np.nan

    df["Rep Code"] = df["Rep Code"].astype(str)


    # =========================
    # MERGE CODES SAFE
    # =========================
    codes = clean_cols(codes)

    if "Rep Code" in codes.columns:
        codes["Rep Code"] = codes["Rep Code"].astype(str)
        df = df.merge(codes, on="Rep Code", how="left")


    # =========================
    # MERGE MAPPING SAFE
    # =========================
    mapping = clean_cols(mapping)

    if "Old Product Code" in df.columns and "Old Product Code" in mapping.columns:

        df["Old Product Code"] = pd.to_numeric(df["Old Product Code"], errors="coerce")

        df = df.merge(
            mapping,
            on="Old Product Code",
            how="left"
        )

    return df


# =========================
# 📊 GROUP ENGINE
# =========================
def build_groups(sales):

    def g(cols, sums):
        cols = [c for c in cols if c in sales.columns]
        sums = [c for c in sums if c in sales.columns]

        if not cols:
            return pd.DataFrame()

        return sales.groupby(cols, as_index=False)[sums].sum()


    return {
        "rep": g(["Rep Code"], ["Total Sales Value","Returns Value","Sales After Returns","Invoice Discounts"]),
        "manager": g(["Manager Code"], ["Total Sales Value","Returns Value","Sales After Returns","Invoice Discounts"]),
        "area": g(["Area Code"], ["Total Sales Value","Returns Value","Sales After Returns","Invoice Discounts"]),
        "supervisor": g(["Supervisor Code"], ["Total Sales Value","Returns Value","Sales After Returns","Invoice Discounts"]),
    }
