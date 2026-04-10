import pandas as pd
import numpy as np


# =========================
# 📥 LOAD DATA
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
# 🎯 TARGET PIPELINE
# =========================
def build_target_pipeline(df, key_col):

    df = df.copy()
    df.columns = df.columns.str.strip()

    if key_col in df.columns:
        df[key_col] = df[key_col].astype(str)

    # clean numeric target columns
    for c in df.columns:
        if "Target" in c:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    return df


# =========================
# 💰 SALES PIPELINE (SAFE)
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    sales.columns = sales.columns.str.strip()

    # =========================
    # 🔢 SAFE NUMERIC
    # =========================
    num_cols = [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price",
        "Invoice Discounts"
    ]

    for c in num_cols:
        if c in sales.columns:
            sales[c] = pd.to_numeric(sales[c], errors="coerce").fillna(0)
        else:
            sales[c] = 0


    # =========================
    # 💰 CALCULATIONS (SAFE)
    # =========================
    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]


    # =========================
    # 🧩 CODES
    # =========================
    if "Rep Code" in sales.columns:
        sales["Rep Code"] = sales["Rep Code"].astype(str)

    codes["Rep Code"] = codes["Rep Code"].astype(str)

    sales = sales.merge(codes, on="Rep Code", how="left")

    return sales


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
