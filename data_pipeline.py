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

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx")
    }


# =========================
# 💰 SALES CLEAN ONLY
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    sales.columns = sales.columns.str.strip()

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
    # CALCULATIONS
    # =========================
    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    sales["Net Sales Unit"] = (
        sales["Sales Unit Before Edit"] - sales["Returns Unit Before Edit"]
    )

    # SAFE KEY
    if "Rep Code" not in sales.columns:
        sales["Rep Code"] = np.nan

    sales["Rep Code"] = sales["Rep Code"].astype(str)

    return sales


# =========================
# 🎯 TARGET CLEAN ONLY
# =========================
def build_target_pipeline(target_df, key_col):

    df = target_df.copy()
    df.columns = df.columns.str.strip()

    if key_col in df.columns:
        df[key_col] = df[key_col].astype(str)

    num_cols = [c for c in df.columns if "Target" in c]

    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    return df
