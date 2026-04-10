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
# 💰 SALES CLEAN ONLY (NO MERGE, NO RENAMING)
# =========================
def build_sales_pipeline(sales):

    df = sales.copy()
    df.columns = df.columns.str.strip()

    # =========================
    # 🔢 NUMERIC CLEAN ONLY
    # =========================
    num_cols = [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price",
        "Invoice Discounts",
        "Sales Value"
    ]

    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # =========================
    # 💰 CALCULATIONS ONLY
    # =========================
    if "Sales Unit Before Edit" in df.columns and "Sales Price" in df.columns:
        df["Total Sales Value"] = df["Sales Unit Before Edit"] * df["Sales Price"]

    if "Returns Unit Before Edit" in df.columns and "Sales Price" in df.columns:
        df["Returns Value"] = df["Returns Unit Before Edit"] * df["Sales Price"]

    if "Total Sales Value" in df.columns and "Returns Value" in df.columns:
        df["Sales After Returns"] = df["Total Sales Value"] - df["Returns Value"]

    return df


# =========================
# 🎯 TARGET CLEAN ONLY
# =========================
def build_target_pipeline(df):

    df = df.copy()
    df.columns = df.columns.str.strip()

    # numeric only
    for col in df.columns:
        if "Target" in col:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df
